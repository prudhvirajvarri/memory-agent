import chromadb
import uuid

# Setup ChromaDB client. It will store data in a 'db' folder.
client = chromadb.PersistentClient(path="db")

# Create a collection to store memories.
# If the collection already exists, it will use the existing one.
memory_collection = client.get_or_create_collection(
    name="memory_agent_collection",
    metadata={"hnsw;space": "cosine"} # Using cosine distance for similarity
)

def create_memory(content: str):
    """
    creates and stores a memory.
    
    Args:
        content (str): The piece of information to remember.
        
    Returns:
        str: A confirmation message.
    """
    try:
        # We use a UUID for a unique ID.
        memory_id = str(uuid.uuid4())
        memory_collection.add(
            documents=[content],
            ids=[memory_id]
        )
        print(f"MEMORY CREATED: '{content}' with ID {memory_id}")
        return f"OK, I will remember that: '{content}'"
    except Exception as e:
        print(f"Error creating memory: {e}")
        return "Sorry, I had trouble remembering that."

def retrieve_memory(query: str, n_results: int = 1):
    """
    Retrieves the most relevant memory based on a query.
    
    Args:
        query (str): The user's question or topic to search for.
        n_results (int): The number of memories tp return.
    
    Returns:
        str: The most relevant memory found, or a message if none were found.
    """
    try:
        results = memory_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results or not results['documents'][0]:
            print("No relevant memory found.")
            return "I don't have any memories related to that."
        
        retrieved_content = results['documents'][0][0]
        print(f"MEMORY RETRIEVED for query '{query}': '{retrieved_content}'")
        return f"Based on my memory: {retrieved_content}"
    except Exception as e:
        print(f"Error retrieving memory: {e}")
        return "Sorry, I had trouble accessing my memory."

def delete_memory(content_to_delete: str):
    """
    Deletes a memory that contains specific content.
    
    Args:
        content_to_delete (str): The content of the memory to delete.
    
    Returns:
        str: A confirmation of deletion or a message if not found.
    """
    try:
        #Find memories that contains the content to delete
        results = memory_collection.get(
            where_document={"$contains": content_to_delete}
        )
        
        if not results['ids']:
            print(f"No memory found containing '{content_to_delete}'.")
            return f"I don't have a memory about '{content_to_delete}'."
        
        memory_ids_to_delete = results['ids']
        memory_collection.delete(ids=memory_ids_to_delete)
        
        print(f"MEMORY DELETED containing: '{content_to_delete}'")
        return f"OK. I have forgotten my memory about '{content_to_delete}'."
    except Exception as e:
        print(f"Error deleting memory: {e}")
        return "Sorry, I had trouble deleting that memory."