import os
import asyncio
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import random
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chat participants template
PARTICIPANTS = [
    {"id": "user_1", "name": "Alice", "role": "software engineer"},
    {"id": "user_2", "name": "Bob", "role": "product manager"},
    {"id": "user_3", "name": "Carol", "role": "data scientist"},
    {"id": "user_4", "name": "David", "role": "UX designer"},
    {"id": "user_5", "name": "Eve", "role": "DevOps engineer"},
    {"id": "user_6", "name": "Frank", "role": "QA engineer"},
    {"id": "user_7", "name": "Grace", "role": "frontend developer"},
    {"id": "user_8", "name": "Henry", "role": "backend developer"}
]

CHANNELS = [
    "general",
    "project-alpha",
    "tech-discussion",
    "random",
    "team-updates"
]

async def generate_conversation(conversation_id: int, llm: ChatOpenAI) -> list:
    """Generate a single conversation between multiple participants."""
    try:
        # Randomly select 3-4 participants for each conversation
        num_participants = random.randint(3, 4)
        selected_participants = random.sample(PARTICIPANTS, num_participants)
        selected_channel = random.choice(CHANNELS)
        
        participants_prompt = "\n".join([f"- {p['name']} ({p['role']})" for p in selected_participants])
        
        prompt = PromptTemplate(
            input_variables=["participants", "channel"],
            template="""Generate a realistic chat conversation in the #{channel} channel between these participants:
            {participants}
            
            The conversation should:
            - Be 20-30 messages long
            - Feel natural and casual
            - Include technical discussion related to their roles
            - Have a clear topic or purpose
            - Include realistic timestamps for each message (in ISO format)
            - Show natural conversation flow with multiple people participating
            
            Format each message as:
            [timestamp] sender_name: message_content"""
        )

        formatted_prompt = prompt.format(
            participants=participants_prompt,
            channel=selected_channel
        )

        response = await llm.ainvoke(formatted_prompt)
        
        # Parse the conversation into individual messages
        messages = []
        for line in response.content.split('\n'):
            if line.strip():
                try:
                    timestamp_str = line[1:line.find(']')]
                    sender_name = line[line.find(']')+2:line.find(':')]
                    content = line[line.find(':')+2:].strip()
                    
                    # Find the participant info
                    sender = next((p for p in selected_participants if p['name'] == sender_name), None)
                    if sender:
                        message = {
                            "channel_id": selected_channel,
                            "workspace_id": "demo_workspace",
                            "sender_type": "user",
                            "sender_id": sender['id'],
                            "content": content,
                            "sender_name": sender_name,
                            "edited_at": datetime.fromisoformat(timestamp_str).isoformat(),
                            "mentions": [],
                            "ai_context": None,
                            "ai_prompt": None,
                            "attachments": [],
                            "thread_id": None,
                            "thread_count": 0
                        }
                        messages.append(message)
                except Exception as e:
                    logger.error(f"Error parsing message line: {line}. Error: {str(e)}")
                    continue
                    
        return messages
        
    except Exception as e:
        logger.error(f"Error generating conversation {conversation_id}: {str(e)}")
        return []

async def generate_multiple_conversations(num_conversations: int = 3) -> list:
    """Generate multiple conversations using concurrent execution with rate limiting."""
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")
    
    async def process_batch(batch_ids):
        tasks = [generate_conversation(conv_id, llm) for conv_id in batch_ids]
        results = await asyncio.gather(*tasks)
        return [msg for conv in results for msg in conv]  # Flatten list of message lists

    # Process in batches of 3 to avoid rate limits
    batch_size = 3
    all_messages = []
    
    for i in range(0, num_conversations, batch_size):
        batch_ids = range(i, min(i + batch_size, num_conversations))
        logger.info(f"Processing batch {i//batch_size + 1}")
        
        batch_messages = await process_batch(batch_ids)
        all_messages.extend(batch_messages)
        
        if i + batch_size < num_conversations:
            logger.info("Rate limit pause between batches...")
            await asyncio.sleep(2)  # 2 second delay between batches
    
    return all_messages

async def main():
    """Main execution function."""
    logger.info("Starting message generation...")
    messages = await generate_multiple_conversations()
    
    # Log results
    logger.info(f"Generated {len(messages)} messages successfully")
    
    # Save to JSON file
    output_file = "generated_messages.json"
    with open(output_file, 'w') as f:
        json.dump(messages, f, indent=2)
    logger.info(f"Saved messages to {output_file}")
    
    # Log preview
    for msg in messages[:5]:  # Preview first 5 messages
        logger.info(f"\nMessage from {msg['sender_name']} in #{msg['channel_id']}:")
        logger.info(msg['content'][:100] + "...")

if __name__ == "__main__":
    asyncio.run(main())
