import logging
import json
from typing import List, Dict, Any
from ..core.llm import generate_with_deepseek

logger = logging.getLogger('chattie_agent')

CHANNEL_GENERATION_PROMPT = """Create channels for a workspace focused on: {description}

Create channels that would facilitate meaningful discussions and debates about different aspects of {description}. Each channel should encourage healthy disagreement and different perspectives. Each channel should have:
1. A clear name (no spaces, lowercase, use hyphens if needed)
2. A specific purpose related to {description}
3. The type of discussions and debates that should happen there
4. Which personas would be most active here (based on their conflicting roles and opinions)
5. Key controversial topics that will spark debate

Format as JSON array with:
- name: string
- description: string
- purpose: string
- primary_personas: string[] (names of personas who should be most active here)
- topics: string[] (key discussion and debate points for this channel)
- debate_topics: string[] (specific controversial topics that will spark disagreement)
"""

async def generate_channels(description: str, api_key: str) -> List[Dict[str, Any]]:
    """Generate channels based on workspace description"""
    logger.info("Generating channels with Deepseek")
    channels_prompt = CHANNEL_GENERATION_PROMPT.format(
        description=description
    )
    channels_json = await generate_with_deepseek(channels_prompt, api_key)
    channels = json.loads(channels_json)
    logger.info("Generated %d channels", len(channels))
    return channels 