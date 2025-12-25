import os
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()

def change_setting(key: str, value: str) -> str:
    """Updates key-value pairs in the .env file."""
    env_key = key.upper().replace(" ", "_")
    dotenv.set_key(".env", env_key, str(value))
    dotenv.load_dotenv(override=True) 
    print(f"\n[SYSTEM]: Changed {env_key} to {value}")
    return f"Confirmed. I have updated {env_key} to {value}."

def run_chatbot():
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Create config with function tool
    config = types.GenerateContentConfig(
        tools=[change_setting],
        system_instruction="You are a system manager. Use 'change_setting' tool to update .env files."
    )
    
    print("--- 💬 Gemini Chat: Online ---")
    print("Type 'exit' to quit\n")
    
    # Create chat session
    chat = client.chats.create(model="gemini-2.5-flash", config=config)
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            response = chat.send_message(user_input)
            
            # Process response parts
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    # Execute the function
                    result = change_setting(**dict(part.function_call.args))
                    
                    # Send function result back to model
                    tool_response = chat.send_message(
                        types.Part.from_function_response(
                            name=part.function_call.name,
                            response={'result': result}
                        )
                    )
                    if tool_response.text:
                        print(f"AI: {tool_response.text}")
                elif part.text:
                    print(f"AI: {part.text}")
                    
        except KeyboardInterrupt:
            print("\nClosed by user.")
            break
        except Exception as e:
            print(f"[ERROR]: {e}")

if __name__ == "__main__":
    run_chatbot()
