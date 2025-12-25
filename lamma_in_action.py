import ollama
import os
from dotenv import load_dotenv, set_key, unset_key, find_dotenv
from pathlib import Path
from module.audio import whisper_transcription


# Define .env manipulation functions

def read_env_value(key: str) -> str:
    """
    Read a value from .env file
    
    Args:
        key: The environment variable key to read
    
    Returns:
        The value of the key or error message
    """
    try:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            dotenv_path = ".env"
        load_dotenv(dotenv_path, override=True)
        value = os.getenv(key)
        if value is None:
            return f"❌ Key '{key}' not found in .env file"
        return f"✅ {key}={value}"
    except Exception as e:
        return f"❌ Error reading .env: {str(e)}"


def update_env_value(key: str, value: str) -> str:
    """
    Update or create a key-value pair in .env file
    
    Args:
        key: The environment variable key
        value: The new value to set
    
    Returns:
        Success message
    """
    try:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            dotenv_path = ".env"
            Path(dotenv_path).touch(mode=0o600, exist_ok=True)
        
        set_key(dotenv_path, key, value)
        return f"✅ Updated: {key}={value}"
    except Exception as e:
        return f"❌ Error updating .env: {str(e)}"


def delete_env_value(key: str) -> str:
    """
    Delete a key from .env file
    
    Args:
        key: The environment variable key to delete
    
    Returns:
        Success message
    """
    try:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            return "❌ .env file not found"
        
        unset_key(dotenv_path, key)
        return f"✅ Deleted key: {key}"
    except Exception as e:
        return f"❌ Error deleting from .env: {str(e)}"


def create_file(filename: str, content: str) -> str:
    """
    Create a new file with content
    
    Args:
        filename: The name of the file to create
        content: The content to write to the file
    
    Returns:
        Success message
    """
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"✅ File '{filename}' created successfully!"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Map function names to functions
available_functions = {
    'create_file': create_file,
    'read_env_value': read_env_value,
    'update_env_value': update_env_value,
    'delete_env_value': delete_env_value,
}

# Initialize conversation history
conversation_history = []

print("🤖 Ollama Assistant with .env Tools")
print("=" * 50)
print("Commands:")
print("  - Type your request (e.g., 'Update my in .env to NewValue')")
print("  - Type 'exit' or 'quit' to stop")
print("=" * 50)

# # Main interactive loop
# while True:
#     # Get user input
#     user_input = input("\n👤 You: ").strip()
    
#     # Check for exit commands
#     if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
#         print("\n👋 Goodbye!")
#         break
    
#     if not user_input:
#         continue

while True:   
    user_input = whisper_transcription()
    if user_input is None:
        print("❌ No transcription received.")
        break
    
    # Add user message to conversation
    conversation_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Agent loop for this turn
    while True:
        response = ollama.chat(
            model='llama3.2',
            messages=conversation_history,
            tools=[create_file, read_env_value, update_env_value, delete_env_value]
        )
        
        # Add assistant response to history
        conversation_history.append(response.message)
        
        # Display assistant's text response
        if response.message.content:
            print(f"\n🤖 Assistant: {response.message.content}")
        
        # Check for tool calls
        if response.message.tool_calls:
            print(f"\n🔧 Executing {len(response.message.tool_calls)} tool(s):")
            
            for tool in response.message.tool_calls:
                print(f"   📌 {tool.function.name}({tool.function.arguments})")
                
                # Execute function
                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
                    result = function_to_call(**tool.function.arguments)
                    print(f"   {result}")
                    
                    # Add tool result to conversation
                    conversation_history.append({
                        'role': 'tool',
                        'content': result,
                        'tool_name': tool.function.name
                    })
            
            print()  # Blank line after tools
        else:
            # No more tool calls, break inner loop and wait for next user input
            break
