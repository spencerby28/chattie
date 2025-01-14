from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.permission import Permission
from appwrite.role import Role
import random
import time
from datetime import datetime, timedelta
import faker
import os
from dotenv import load_dotenv
import json
from pathlib import Path
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

# Initialize Faker for generating fake data
fake = faker.Faker()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize database service
database = Databases(client)

# Create gen_ids directory if it doesn't exist
gen_ids_dir = Path('gen_ids')
gen_ids_dir.mkdir(exist_ok=True)

# Default avatar IDs
DEFAULT_AVATARS = [
    'acd1b47b-923a-4b3b-b3d5-4f8477322ec4',
    'b028239c-6769-4386-8c9c-f55161b2c6ef',
    'c907105b-3c66-4a41-af4f-769751568740',
    'c491e057-dd58-4d22-85c2-0801d469319b',
    'f509c043-1ac3-4640-ac6f-5e2b5d09c3bf',
    '00fbfeee-b33b-4eb3-b793-72806baa1038'
]

def list_channels():
    channels = database.list_documents(
        database_id='main',
        collection_id='channels',
        queries=[]
    )
    return channels['documents']

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

def delete_previous_messages():
    print("\nDeleting previous generated messages...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        for gen_file in gen_ids_dir.glob('generated_*.json'):
            with open(gen_file) as f:
                ids = json.load(f)
                futures = [executor.submit(delete_message, msg_id) for msg_id in ids]
                for future in as_completed(futures):
                    future.result()

def create_message(channel, i, num_messages):
    message = {
        'channel_id': channel['$id'],
        'workspace_id': channel['workspace_id'],
        'sender_type': 'user',
        'sender_id': fake.uuid4(),
        'content': fake.text(max_nb_chars=200),
        'sender_name': fake.name(),
        'edited_at': None,
        'mentions': [],
        'ai_context': None,
        'ai_prompt': None,
        'attachments': [],

    }
    
    result = database.create_document(
        database_id='main',
        collection_id='messages',
        document_id='unique()',
        data=message,
        permissions=[
            Permission.read(Role.label(channel['$id'])),
            Permission.write(Role.user(message['sender_id'])),
            Permission.delete(Role.user(message['sender_id']))
        ]
    )
    
    print(f"Created message {i+1}/{num_messages} in channel {channel['name']}")
    time.sleep(0.1)  # Small delay to prevent rate limiting
    return result['$id']

def generate_messages(channels, num_messages):
    generated_ids = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i in range(num_messages):
            channel = random.choice(channels)
            futures.append(executor.submit(create_message, channel, i, num_messages))
        
        for future in as_completed(futures):
            generated_ids.append(future.result())
    
    return generated_ids

def main():
    try:
        print("\nWelcome to the Fake Message Generator!")
        
        # Get all available channels
        all_channels = list_channels()
        if not all_channels:
            print("No channels found!")
            return
            
        # List all channels
        print("\nAvailable channels:")
        for i, channel in enumerate(all_channels, 1):
            print(f"{i}. {channel['name']} (ID: {channel['$id']})")
            
        # Ask if user wants to delete previous messages
        delete_prev = input("\nDo you want to delete previously generated messages? (y/n): ").lower()
        if delete_prev == 'y':
            delete_previous_messages()
            
        # Ask for channel selection
        print("\nChannel selection:")
        print("1. Use specific channel")
        print("2. Use multiple random channels")
        choice = input("Enter your choice (1 or 2): ")
        
        selected_channels = []
        if choice == '1':
            channel_num = int(input("Enter the channel number from the list above: "))
            selected_channels = [all_channels[channel_num - 1]]
        else:
            num_channels = int(input(f"How many channels to use (max {len(all_channels)}): "))
            num_channels = min(num_channels, len(all_channels))
            selected_channels = random.sample(all_channels, num_channels)
            
        # Ask for number of messages
        num_messages = int(input("\nHow many messages to generate: "))
        
        print(f"\nWill generate {num_messages} messages across {len(selected_channels)} channels")
        confirm = input("Continue? (y/n): ").lower()
        
        if confirm == 'y':
            generated_ids = generate_messages(selected_channels, num_messages)
            
            # Save generated IDs to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            with open(gen_ids_dir / f'generated_{timestamp}.json', 'w') as f:
                json.dump(generated_ids, f)
                
            print(f"\nSuccessfully generated {num_messages} messages!")
            print(f"Generated IDs saved to gen_ids/generated_{timestamp}.json")
        else:
            print("\nOperation cancelled")
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
