import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from memory_manager import create_memory, retrieve_memory, delete_memory

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
# It will use the API key from the environment variable
client = OpenAI()

# Tool Definitions
# This tells the LLM what Python functions it can call

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_memory",
            "description": "Uses this function to store a new piece of information or fact. For example, when the user says 'Remember that my name is Prudhvi'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The specific fact or piece of information to remembered.",
                    },
                },
                "required": ["content"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_memory",
            "description": "Uses this function to find a relevent memory when the user asks a question. For example, when the user asks 'What is my name?'",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question or the topic to search for in memory.",
                    },
                    "n_results": {
                        "type": "integer",
                        "default": 1,
                        "description": "The number of results to return."
                    },
                },
                "required": ["query"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory",
            "description": "Uses this function to delete a specific memory when the user explicitly says to forget something. For example, when the user says 'Forget that my name is Prudhvi'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content_to_delete": {
                        "type": "string",
                        "description": "The specific content of the memory to deleted.",
                    },
                },
                "required": ["content_to_delete"]
            },
        },
    }
]

# Mapping tool names to actual python functions
available_functions = {
    "create_memory": create_memory,
    "retrieve_memory": retrieve_memory,
    "delete_memory": delete_memory,
}

def run_conversation():
    """Main conversation loop."""
    print("AI Memory Agent is ready. Type 'exit' to end the conversation.")
    
    # start with a system message to set the context for the AI
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant with access to tools for long-term memory."
        }
    ]
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Ending conversation. Goodbye!")
            break
        
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # First API call: The model decides if a tool is needed
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = messages,
            tools = tools,
            tool_choice = "auto",
        )
        response_message = response.choices[0].message
        messages.append(response_message) # Append the model's response to history
        
        tool_calls = response_message.tool_calls
        
        # Check if the model wants  to call a tool
        if tool_calls:
            print(f"AI wants to call a tool: {tool_calls[0].function.name}")
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                # Call the chosen function with the model's arguments
                function_response = function_to_call(**function_args)
                
                # Send the tool's result back to the model
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
            
            # SecondAPI call: Get a final, natural language response from the model
            second_response = client.chat.completions.create(
                model = "gpt-4o-mini",
                messages = messages,
            )
            final_response = second_response.choices[0].message.content
            print(f"AI: {final_response}")
            messages.append(second_response.choices[0].message)
        else:
            # If no tool is needed, just print the model's response
            final_response = response_message.content
            print(f"AI: {final_response}")
        
if __name__ == "__main__":
    run_conversation()