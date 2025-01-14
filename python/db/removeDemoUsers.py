from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.query import Query
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize services
database = Databases(client)
users = Users(client)

def delete_user_messages(user_id):
    """Delete all messages from a specific user"""
    try:
        # List all messages from this user
        messages = database.list_documents(
            database_id='main',
            collection_id='messages',
            queries=[
                Query.equal('sender_id', user_id),
                Query.limit(1000)
            ]
        )
        
        # Delete each message
        for message in messages['documents']:
            database.delete_document(
                database_id='main',
                collection_id='messages',
                document_id=message['$id']
            )
            print(f"Deleted message {message['$id']} from user {user_id}")
            
    except Exception as e:
        print(f"Error deleting messages for user {user_id}: {str(e)}")

def main():
    try:
        # Get all users first
        all_users = users.list(queries=[Query.limit(1000)])
        print(f"Found {all_users['total']} users")
        print(all_users['users'][56])
        
        # Filter for demo users
        demo_users = {
            'total': 0,
            'users': []
        }
        
        for user in all_users['users']:
            if user['name'].startswith('Demo User'):
                demo_users['users'].append(user)
                demo_users['total'] += 1
        
        if not demo_users['total']:
            print("No demo users found")
            return
            
        print(f"Found {demo_users['total']} demo users")
        
        # Delete messages and users
        for user in demo_users['users']:
            print(f"Processing user: {user['name']} ({user['$id']})")
            
            # First delete all their messages
            delete_user_messages(user['$id'])
            
            # Then delete the user
            try:
                users.delete(user['$id'])
                print(f"Deleted user {user['name']}")
            except Exception as e:
                print(f"Error deleting user {user['$id']}: {str(e)}")
                
        print("\nFinished removing demo users and their messages")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
