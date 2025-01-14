import logging
import json
from typing import List, Dict, Any
from ..core.llm import generate_with_deepseek

logger = logging.getLogger('chattie_agent')

PERSONA_GENERATION_PROMPT = """Create {num_personas} unique and engaging AI personas for a workspace focused on: {description}

Each persona should have strong, often conflicting opinions and perspectives related to this workspace's focus. They should actively disagree with each other's approaches and methodologies. Create personas that represent different schools of thought and opposing viewpoints about {description}. Each persona should have:

1. A memorable name or username (professional but approachable)
2. A distinct personality and communication style
3. Areas of expertise/knowledge base specifically relevant to {description}
4. A brief backstory that explains their perspective and why they strongly disagree with other approaches to {description}
5. Their typical way of interacting with users, including how they challenge others' views
6. Their role in the way they live their life
7. Strong, controversial opinions about {description} that directly conflict with other personas
8. Points of contention they regularly debate with others

Format the response as a JSON array with objects containing:
- name: string
- personality: string (detailed description including their strong opinions and what they disagree with)
- conversation_style: string (formal/casual/technical etc)
- knowledge_base: string[] (areas of expertise)
- role: string (their role in life)
- greeting: string (their typical first message that shows their personality)
- opinions: string[] (list of strong beliefs they hold about {description})
- disagreements: string[] (list of specific points they regularly debate or disagree with)
- debate_style: string (how they engage in disagreements)

The response MUST be a valid JSON array.
"""

async def generate_personas(description: str, num_personas: int, api_key: str) -> List[Dict[str, Any]]:
    """Generate AI personas based on workspace description"""
    logger.info("Generating personas with Deepseek")
    personas_prompt = PERSONA_GENERATION_PROMPT.format(
        num_personas=num_personas,
        description=description
    )
    personas_json = await generate_with_deepseek(personas_prompt, api_key)
    personas = json.loads(personas_json)
    logger.info("Generated %d personas", len(personas))
    return personas 