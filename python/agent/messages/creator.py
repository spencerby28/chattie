import logging
import random
from typing import Dict, Any, Optional, List
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID

logger = logging.getLogger('chattie_agent')

DATABASE_ID = 'main'
MESSAGES_COLLECTION = 'messages'

async def create_initial_message(
    databases: Databases,
    channel_id: str,
    workspace_id: str,
    ai_user_id: str,
    persona_name: str,
    greeting: str
) -> Optional[str]:
    """Create an initial message from an AI persona in a channel"""
    try:
        logger.info(f"\n=== Creating Initial Message ===")
        logger.info(f"Channel ID: {channel_id}")
        logger.info(f"Workspace ID: {workspace_id}")
        logger.info(f"AI User ID: {ai_user_id}")
        logger.info(f"Persona Name: {persona_name}")
        logger.info(f"Message Content: {greeting[:100]}...")  # Log first 100 chars of message
        
        message_data = {
            'channel_id': channel_id,
            'workspace_id': workspace_id,
            'sender_type': 'ai',
            'sender_id': ai_user_id,
            'content': greeting,
            'sender_name': persona_name,
            'edited_at': None,
            'mentions': [],
            'ai_context': None,
            'ai_prompt': None,
            'attachments': []
        }
        
        logger.info("Creating message document in Appwrite...")
        result = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            document_id=ID.unique(),
            data=message_data,
            permissions=[
                Permission.read(Role.label(channel_id)),
                Permission.write(Role.user(ai_user_id))
            ]
        )
        logger.info(f"Successfully created message document with ID: {result['$id']}")
        logger.info("=== Initial Message Creation Complete ===\n")
        return result['$id']
        
    except Exception as e:
        logger.error(f"Failed to create initial message for {persona_name} in channel {channel_id}")
        logger.error(f"Error details: {str(e)}")
        logger.exception(e)
        return None

async def create_core_belief_message(
    databases: Databases,
    channel_id: str,
    workspace_id: str,
    ai_user_id: str,
    persona: Dict[str, Any]
) -> Optional[str]:
    """Create a core belief message for a persona in a channel"""
    try:
        logger.info(f"\n=== Processing Core Belief Message for {persona['name']} ===")
        
        # Generate a core belief message based on the persona's opinions and personality
        selected_opinion = random.choice(persona['opinions'])
        logger.info(f"Selected opinion: {selected_opinion}")
        
        core_belief = f"As {persona['role']}, my core belief is: {selected_opinion}. {persona['personality'][:100]}..."
        logger.info(f"Generated core belief message: {core_belief[:100]}...")
        
        message_id = await create_initial_message(
            databases,
            channel_id,
            workspace_id,
            ai_user_id,
            persona['name'],
            core_belief
        )
        
        if message_id:
            logger.info(f"Successfully created core belief message with ID: {message_id}")
        return message_id
        
    except Exception as e:
        logger.error(f"Failed to create core belief message for {persona['name']}: {str(e)}")
        logger.exception(e)
        return None

async def create_channel_initial_messages(
    databases: Databases,
    channel: Dict[str, Any],
    workspace_id: str,
    personas: List[Dict[str, Any]],
    ai_user_ids: List[str]
) -> List[str]:
    """Create initial messages for all primary personas in a channel"""
    message_ids = []

    logger.info(f"Personas: {personas}")
    logger.info(f"AI User IDs: {ai_user_ids}")
    logger.info(f"Channel: {channel}")
    logger.info(f"Workspace ID: {workspace_id}")

    
    for persona in personas:
        #if persona['name'] in channel['primary_personas']:
            ai_user_id = next((uid for uid in ai_user_ids if uid == persona.get('ai_user_id')), None)
            if ai_user_id:
                message_id = await create_core_belief_message(
                    databases,
                    channel['$id'],
                    workspace_id,
                    ai_user_id,
                    persona
                )
                if message_id:
                    message_ids.append(message_id)
            else:
                logger.error(f"Could not find AI user ID for persona {persona['name']}")
                
    return message_ids 