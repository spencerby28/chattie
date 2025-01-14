import logging
from typing import Dict, Any, List
from appwrite.services.databases import Databases
from appwrite.services.users import Users

from ..personas.generator import generate_personas
from ..personas.storage import store_personas
from ..channels.generator import generate_channels
from ..channels.storage import store_channels
from ..messages.creator import create_channel_initial_messages
from ..users.creator import create_ai_user

logger = logging.getLogger('chattie_agent')

async def create_workspace(
    description: str,
    workspace_id: str,
    api_key: str,
    databases: Databases,
    users: Users,
    num_personas: int = 5
) -> Dict[str, Any]:
    """Create a complete workspace with personas, channels, and initial messages"""
    logger.info("Starting workspace creation for ID: %s", workspace_id)
    logger.info("Workspace description: %s", description)
    
    # Generate personas
    personas = await generate_personas(description, num_personas, api_key)
    
    # Create AI users for each persona
    ai_user_ids = []
    for persona in personas:
        ai_user_id = await create_ai_user(users, persona['name'], workspace_id)
        if ai_user_id:
            ai_user_ids.append(ai_user_id)
            persona['ai_user_id'] = ai_user_id
    
    # Store personas in Appwrite
    stored_personas = await store_personas(databases, workspace_id, personas, ai_user_ids)
    
    # Generate channels
    channels = await generate_channels(description, api_key)
    
    # Store channels and create initial messages
    stored_channels = await store_channels(
        databases,
        workspace_id,
        channels,
        ai_user_ids,
        personas
    )
    
    # Create initial messages for each channel
    for channel in stored_channels:
        await create_channel_initial_messages(
            databases,
            channel,
            workspace_id,
            personas,
            ai_user_ids
        )
    
    logger.info("Workspace creation completed. Personas: %d, Channels: %d", 
                len(stored_personas), len(stored_channels))
                
    return {
        'personas': stored_personas,
        'channels': stored_channels,
        'workspace_theme': description
    } 