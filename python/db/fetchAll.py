from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize database service
database = Databases(client)

# Function to fetch all documents with pagination
def fetch_all_documents(database_id: str, collection_id: str, limit: int = 100):
    documents = []
    offset = 0
    
    while True:
        try:
            result = database.list_documents(
                database_id=database_id,
                collection_id=collection_id,
                queries=[
                    Query.limit(limit),
                    Query.offset(offset)
                ]
            )
            
            batch = result['documents']
            if not batch:
                break
                
            documents.extend(batch)
            offset += limit
            
            print(f"Fetched {len(batch)} documents from {collection_id}, total: {len(documents)}")
            
        except Exception as e:
            print(f"Error fetching {collection_id} at offset {offset}: {str(e)}")
            break
            
    return documents

# Fetch all messages
try:
    messages_docs = fetch_all_documents('main', 'messages')
    messages_df = pd.DataFrame(messages_docs)
    messages_df.to_csv('messages.csv', index=True)
    print(f"Saved {len(messages_docs)} messages to messages.csv")
except Exception as e:
    print(f"Error processing messages: {str(e)}")

# Fetch all AI personas
try:
    personas_docs = fetch_all_documents('main', 'ai_personas')
    personas_df = pd.DataFrame(personas_docs)
    personas_df.to_csv('ai_personas.csv', index=True)
    print(f"Saved {len(personas_docs)} personas to ai_personas.csv")
except Exception as e:
    print(f"Error processing personas: {str(e)}")
