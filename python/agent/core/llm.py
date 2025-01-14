import logging
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI

logger = logging.getLogger('chattie_agent')

async def generate_with_llm(prompt: str, api_key: str) -> str:
    """Generate text using GPT-4-mini"""
    try:
        logger.info("\nMaking request to OpenAI API...")
        
        llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4o-mini",
            openai_api_key=api_key
        )
        
        result = llm.invoke(prompt)
        content = result.content
        
        # Strip markdown formatting
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()
        
        logger.debug("\nCleaned Content:")
        logger.debug("=" * 50)
        logger.debug(content)
        logger.debug("=" * 50)
        
        return content
        
    except Exception as e:
        logger.error(f"\nError in generate_with_llm: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error("Traceback:")
            traceback.print_tb(e.__traceback__)
        raise

# Alias for backward compatibility
generate_with_deepseek = generate_with_llm 