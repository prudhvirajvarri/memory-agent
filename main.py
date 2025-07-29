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

