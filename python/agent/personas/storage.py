import logging
from typing import Dict, Any, List
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID

logger = logging.getLogger('chattie_agent')

DATABASE_ID = 'main'
AI_PERSONAS_COLLECTION = 'ai_personas'

async def store_persona(
    databases: Databases,
    workspace_id: str,
    persona: Dict[str, Any],
    ai_user_id: str
) -> Dict[str, Any]:
    """Store a persona in Appwrite"""
    try:
        logger.info("Storing persona in Appwrite: %s", persona['name'])
        
        # Prepare the persona data according to our schema
        persona_data = {
            'workspace_id': workspace_id,
            'name': persona['name'],
            'personality': persona['personality'],
            'avatar_url': f"https://api.dicebear.com/7.x/avataaars/svg?seed={persona['name']}",
            'conversation_style': persona['conversation_style'],
            'knowledge_base': persona['knowledge_base'],
            'greeting': persona['greeting'],
            'role': persona['role'],
            'opinions': persona.get('opinions', []),
            'disagreements': persona.get('disagreements', []),
            'debate_style': persona.get('debate_style', ''),
            'ai_user_id': ai_user_id
        }
        
        # Create or update the persona in Appwrite
        stored_persona = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=AI_PERSONAS_COLLECTION,
            document_id=ID.unique(),
            data=persona_data,
            permissions=[
                Permission.read(Role.users()),
                Permission.write(Role.user(ai_user_id)),
                Permission.update(Role.user(ai_user_id)),
                Permission.delete(Role.user(workspace_id)),
                Permission.read(Role.label(ai_user_id))
            ]
        )
        
        logger.info("Successfully stored persona: %s with ID: %s", 
                   persona['name'], stored_persona['$id'])
        return stored_persona
        
    except Exception as e:
        logger.error("Failed to store persona %s: %s", persona['name'], str(e))
        logger.exception(e)
        raise

async def store_personas(
    databases: Databases,
    workspace_id: str,
    personas: List[Dict[str, Any]],
    ai_user_ids: List[str]
) -> List[Dict[str, Any]]:
    """Store multiple personas in Appwrite"""
    stored_personas = []
    
    for idx, (persona, ai_user_id) in enumerate(zip(personas, ai_user_ids), 1):
        try:
            logger.info("Processing persona %d/%d: %s", idx, len(personas), persona['name'])
            stored_persona = await store_persona(databases, workspace_id, persona, ai_user_id)
            stored_personas.append(stored_persona)
        except Exception as e:
            logger.error("Failed to store persona %s: %s", persona['name'], str(e))
            logger.exception(e)
            
    return stored_personas 