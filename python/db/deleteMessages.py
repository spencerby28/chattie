from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize database service
database = Databases(client)

def delete_message(msg_id):
    try:
        database.delete_document(
            database_id='main',
            collection_id='messages',
            document_id=msg_id
        )
        print(f"Deleted message {msg_id}")
    except Exception as e:
        print(f"Failed to delete message {msg_id}: {str(e)}")

def delete_messages_batch():
    offset = 0
    batch_size = 1000
    total_deleted = 0

    while True:
        try:
            # Get batch of messages
            messages = database.list_documents(
                database_id='main',
                collection_id='messages',
                queries=[
                    Query.limit(batch_size),
                    Query.offset(offset)
                ]
            )

            if not messages['documents']:
                break

            # Use ThreadPoolExecutor to delete messages in parallel
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(delete_message, message['$id']) 
                    for message in messages['documents']
                ]
                
                for future in as_completed(futures):
                    future.result()

            total_deleted += len(messages['documents'])
            print(f"Processed {total_deleted} messages")

            if len(messages['documents']) < batch_size:
                break

            offset += batch_size

        except Exception as e:
            print(f"Error processing batch: {str(e)}")
            break

    print(f"Total messages deleted: {total_deleted}")

if __name__ == "__main__":
    print("Starting message deletion...")
    delete_messages_batch()
    print("Message deletion complete!")
