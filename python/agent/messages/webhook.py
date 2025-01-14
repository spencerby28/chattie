import logging
import json
from typing import Dict, Any
from .autonomous import generate_response
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users

logger = logging.getLogger('chattie_agent')

async def handle_message_webhook(
    event_data: Dict[str, Any],
    api_key: str,
    appwrite_endpoint: str,
    appwrite_project: str,
    appwrite_api_key: str
) -> Dict[str, Any]:
    """Handle incoming message webhook and generate response"""
    try:
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(appwrite_endpoint)
        client.set_project(appwrite_project)
        client.set_key(appwrite_api_key)
        
        databases = Databases(client)
        users = Users(client)
        
        # Extract message data
        message = event_data['message']
        channel_id = message['channel_id']
        workspace_id = message['workspace_id']
        
        # Get channel data
        channel = databases.get_document(
            database_id='main',
            collection_id='channels',
            document_id=channel_id
        )
        
        # Get workspace personas
        personas_docs = databases.list_documents(
            database_id='main',
            collection_id='personas',
            queries=[
                f'workspace_id={workspace_id}'
            ]
        )
        personas = personas_docs['documents']
        
        # Generate and store response
        response = await generate_response(
            databases=databases,
            channel=channel,
            workspace_id=workspace_id,
            message=message,
            personas=personas,
            api_key=api_key
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error handling message webhook: {str(e)}")
        raise 