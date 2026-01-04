# client.py
import asyncio
import ollama
from fastmcp import Client
import json
import time

SYSTEM_PROMPT = """DNS assistant with Technitium API. Execute immediately. Max 2 sentences.

TOOLS:
add_dns_record(domain,name,ip) - Add record
get_dns_records(domain) - View records  
update_dns_record(domain,current_ip,new_ip) - Change IP
rename_dns_record(old_domain,new_domain) - Rename domain
delete_dns_record(domain,ip) - Remove record
find_domain_by_ip(ip) - Find by IP
list_dns_zones() - List zones
create_dns_zone(zone) - Create zone
delete_dns_zone(zone,confirm=True) - Delete zone

CRITICAL MULTI-TASK RULE:
When user says "create zone IF EXISTS then add record":
- Skip create_dns_zone completely
- ONLY call add_dns_record directly
- The add_dns_record tool works even if zone exists

When user says "create zone AND add record":
- Call BOTH tools in same response: [create_dns_zone, add_dns_record]
- Don't wait for first result

RULES:
- IPs are numbers: 192.168.1.100
- Domains have letters: example.com
- If task says "if exists" = assume it exists, skip creation
- Execute multiple tools in parallel when possible

EXAMPLES:
"create zone x.com if exists then add test.x.com to 1.1.1.1"
-> ONLY call: add_dns_record(domain="x.com",name="test",ip="1.1.1.1")

"create zone x.com and add test.x.com to 1.1.1.1"  
-> call: create_dns_zone(zone="x.com") AND add_dns_record(domain="x.com",name="test",ip="1.1.1.1")"""

async def convert_mcp_tools_to_ollama(tools):
    ollama_tools = []
    for tool in tools:
        ollama_tool = {
            'type': 'function',
            'function': {
                'name': tool.name,
                'description': tool.description or '',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': []
                }
            }
        }
        if hasattr(tool, 'inputSchema') and tool.inputSchema:
            schema = tool.inputSchema
            if 'properties' in schema:
                ollama_tool['function']['parameters']['properties'] = schema['properties']
            if 'required' in schema:
                ollama_tool['function']['parameters']['required'] = schema['required']
        ollama_tools.append(ollama_tool)
    return ollama_tools

async def execute_tool(client, tool_name, arguments):
    try:
        result = await client.call_tool(tool_name, arguments)
        if hasattr(result, 'content') and result.content:
            text_result = result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
            try:
                return json.loads(text_result)
            except:
                return text_result
        return str(result)
    except Exception as e:
        return {'success': False, 'error': str(e)}

def truncate(text, max_len=50):
    """Truncate text for display"""
    return text if len(text) <= max_len else text[:max_len-3] + "..."

async def chat_with_ollama():
    print("🔄 Connecting to DNS MCP server...")
    
    async with Client("dns_server.py") as client:
        print("✅ Connected to MCP server")
        
        tools_list = await client.list_tools()
        print(f"🛠️  Loaded {len(tools_list)} tools")
        
        ollama_tools = await convert_mcp_tools_to_ollama(tools_list)
        ollama_client = ollama.Client(host='http://localhost:11434')
        
        try:
            ollama_client.list()
            print("✅ Connected to Ollama")
        except Exception as e:
            print(f"❌ Could not connect to Ollama: {e}")
            return
        
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        
        print("\n" + "="*60)
        print("💬 DNS Manager (type 'exit' to quit)")
        print("="*60)
        print("💡 Tip: 'add test.data.com to 1.1.1.1' works on existing zones\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            messages.append({'role': 'user', 'content': user_input})
            print("\n🤖 ", end='', flush=True)
            
            try:
                max_rounds = 3
                current_round = 0
                
                while current_round < max_rounds:
                    start = time.time()
                    
                    response = ollama_client.chat(
                        model='qwen2.5:7b-instruct-q4_0',
                        messages=messages,
                        tools=ollama_tools,
                        options={
                            'temperature': 0,
                            'num_ctx': 2048,
                            'num_predict': 40,
                            'top_k': 5,
                            'top_p': 0.8
                        }
                    )
                    
                    elapsed = time.time() - start
                    
                    if response['message'].get('tool_calls'):
                        # Show timing
                        if current_round == 0:
                            print(f"[{elapsed:.1f}s]")
                        else:
                            print(f"  [Round {current_round + 1}, {elapsed:.1f}s]")
                        
                        messages.append(response['message'])
                        
                        for tool in response['message']['tool_calls']:
                            tool_name = tool['function']['name']
                            tool_args = tool['function']['arguments']
                            
                            # Better display
                            args_display = ', '.join(
                                f'{k}={truncate(str(v), 15)}' 
                                for k,v in tool_args.items()
                            )
                            print(f"  🔧 {tool_name}({args_display})")
                            
                            result = await execute_tool(client, tool_name, tool_args)
                            
                            if isinstance(result, dict):
                                if result.get('success') is False:
                                    error_msg = result.get('error', 'Failed')
                                    print(f"     ❌ {truncate(error_msg, 50)}")
                                else:
                                    msg = result.get('message', 'Done')
                                    print(f"     ✅ {truncate(msg, 60)}")
                            
                            messages.append({
                                'role': 'tool',
                                'content': json.dumps(result) if isinstance(result, dict) else str(result),
                            })
                        
                        current_round += 1
                        
                    else:
                        # No more tool calls
                        if current_round > 0:
                            # Get summary after tools
                            try:
                                final = ollama_client.chat(
                                    model='qwen2.5:7b-instruct-q4_0',
                                    messages=messages,
                                    options={
                                        'temperature': 0,
                                        'num_predict': 30,
                                        'num_ctx': 1024
                                    }
                                )
                                print(f"\n  ✨ {final['message']['content']}\n")
                                messages.append(final['message'])
                            except Exception as e:
                                print(f"\n  ⚠️ Summary error: {e}\n")
                        else:
                            # No tools used
                            print(f"{response['message']['content']} [{elapsed:.1f}s]\n")
                            messages.append(response['message'])
                        
                        break
                
                if current_round >= max_rounds:
                    print(f"\n  ⚠️ Stopped at {max_rounds} rounds. Try simpler tasks.\n")
                    
            except Exception as e:
                print(f"❌ Error: {e}\n")
                if messages[-1]['role'] == 'user':
                    messages.pop()

if __name__ == "__main__":
    try:
        asyncio.run(chat_with_ollama())
    except KeyboardInterrupt:
        print("\n👋 Interrupted!")
    except Exception as e:
        print(f"❌ Error: {e}")
