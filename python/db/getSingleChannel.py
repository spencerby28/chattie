import csv
from collections import defaultdict
from datetime import datetime

def get_channel_messages(channel_name: str):
    """
    Retrieves all messages from a specific channel and saves them to a text file.
    
    Args:
        channel_name (str): Name of the channel to get messages from
    """
    messages = []
    
    # Read messages from CSV
    with open('messages.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            if row[1] == "67871d7f002c48f49a54":  # Check channel ID matches
                messages.append({
                    'sender': row[0],
                    'content': row[2], 
                    'timestamp': row[3]
                })
    
    # Sort messages by timestamp
    try:
        messages.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
    except ValueError:
        # Handle invalid timestamps but still sort valid ones
        valid_messages = []
        invalid_messages = []
        for msg in messages:
            try:
                datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                valid_messages.append(msg)
            except ValueError:
                invalid_messages.append(msg)
        
        valid_messages.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
        messages = valid_messages + invalid_messages

    # Format and write messages to file
    output = []
    for msg in messages:
        output.append(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}")
        output.append("|||")  # Message separator
        
    with open('channel-id-messages.txt', 'w') as f:
        f.write("\n".join(output))

get_channel_messages("67871d7f002c48f49a54")