import logging
from typing import Dict, Any, List
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID

logger = logging.getLogger('chattie_agent')

DATABASE_ID = 'main'
CHANNELS_COLLECTION = 'channels'

async def store_channel(
    databases: Databases,
    workspace_id: str,
    channel: Dict[str, Any],
    ai_user_ids: List[str],
    personas: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Store a channel in Appwrite"""
    try:
        logger.info("Storing channel in Appwrite: %s", channel['name'])
        
        # Prepare channel data according to our schema
        channel_data = {
            'workspace_id': workspace_id,
            'name': channel['name'].lower().replace(' ', '-'),
            'type': 'public',
            'members': ai_user_ids,
            'description': channel['description'],
            'purpose': channel.get('purpose', ''),
            'topics': channel.get('topics', []),
            'debate_topics': channel.get('debate_topics', []),
            'last_message_at': None,
            'primary_personas': [
                persona['name'] for persona in personas 
                if persona['name'] in channel['primary_personas']
            ]
        }
        
        # Create channel in Appwrite
        stored_channel = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=CHANNELS_COLLECTION,
            document_id=ID.unique(),
            data=channel_data,
            permissions=[
                Permission.read(Role.users()),
                Permission.write(Role.users()),
                *[Permission.write(Role.user(user_id)) for user_id in ai_user_ids],
                Permission.update(Role.user(workspace_id)),
                Permission.delete(Role.user(workspace_id))
            ]
        )
        
        logger.info("Successfully stored channel: %s with ID: %s", 
                   channel_data['name'], stored_channel['$id'])
        return stored_channel
        
    except Exception as e:
        logger.error("Failed to store channel %s: %s", channel['name'], str(e))
        logger.exception(e)
        raise

async def store_channels(
    databases: Databases,
    workspace_id: str,
    channels: List[Dict[str, Any]],
    ai_user_ids: List[str],
    personas: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Store multiple channels in Appwrite"""
    stored_channels = []
    
    for idx, channel in enumerate(channels, 1):
        try:
            logger.info("Processing channel %d/%d: %s", idx, len(channels), channel['name'])
            stored_channel = await store_channel(
                databases,
                workspace_id,
                channel,
                ai_user_ids,
                personas
            )
            stored_channels.append(stored_channel)
        except Exception as e:
            logger.error("Failed to store channel %s: %s", channel['name'], str(e))
            logger.exception(e)
            
    return stored_channels 