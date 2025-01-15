import csv
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize database service
database = Databases(client)

try:
    # Get all messages from the workspace using Query
    messages = database.list_documents(
        database_id='main',
        collection_id='messages',
        queries=[
            Query.equal('workspace_id', '67880f8900347856473d'),
            Query.limit(1000)
        ]
    )
    
    # Save messages to CSV file
    with open('workspace_messages.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'channel_id', 'workspace_id', 'sender_type', 
            'sender_id', 'content', 'edited_at', 'sender_name'
        ])
        writer.writeheader()
        
        for msg in messages['documents']:
            filtered_msg = {
                'channel_id': msg['channel_id'],
                'workspace_id': msg['workspace_id'],
                'sender_type': msg['sender_type'],
                'sender_id': msg['sender_id'],
                'content': msg['content'],
                'edited_at': msg['edited_at'],
                'sender_name': msg['sender_name']
            }
            writer.writerow(filtered_msg)

    print("Messages successfully saved to workspace_messages.csv")

except Exception as e:
    print(f"Error retrieving messages: {str(e)}")
