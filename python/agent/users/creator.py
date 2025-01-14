import logging
import secrets
import string
from typing import Optional
from appwrite.services.users import Users
from appwrite.id import ID

logger = logging.getLogger('chattie_agent')

def generate_secure_password(length=32):
    """Generate a secure random password"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def create_ai_user(users: Users, persona_name: str, workspace_id: str) -> Optional[str]:
    """Create an AI user account for a specific persona"""
    logger.info("Creating AI user for persona: %s in workspace: %s", persona_name, workspace_id)
    try:
        # Generate a secure random password
        password = generate_secure_password()
        # Create a sanitized username from persona name
        username = persona_name.lower().replace(' ', '_')
        email = f"{username}.{workspace_id}@chattie.local"
        
        logger.info("Attempting to create AI user with email: %s", email)
        # Create the user in Appwrite using admin client
        ai_user = users.create(
            user_id=ID.unique(),
            email=email,
            password=password,
            name=persona_name
        )
        
        logger.info("Successfully created AI user: %s", ai_user['$id'])
        return ai_user['$id']
        
    except Exception as e:
        logger.warning("Error creating AI user: %s", str(e))
        # Check if user already exists
        try:
            logger.info("Checking if AI user already exists")
            existing_user = users.get(f"ai-{workspace_id}-{username}")
            logger.info("Found existing AI user: %s", existing_user['$id'])
            return existing_user['$id']
        except Exception as inner_e:
            logger.error("Failed to get existing user: %s", str(inner_e))
            return None 