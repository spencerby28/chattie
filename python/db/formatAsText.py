import csv
from collections import defaultdict
from datetime import datetime

def format_messages_as_text():
    # Dictionary to store messages by channel
    channels = defaultdict(list)
    
    # Read messages from CSV
    with open('messages.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            channel = row[0]  # Channel name
            message_id = row[1]  # Message ID
            content = row[2]  # Message content
            timestamp = row[3]  # Timestamp
            
            # Add message to channel
            channels[channel].append({
                'id': message_id,
                'content': content,
                'timestamp': timestamp
            })
    
    # Format output text
    output = []
    for channel, messages in channels.items():
        # Add channel header
        output.append(f"\n=== Channel: {channel} ===\n")
        
        # Sort messages by timestamp, handling any invalid timestamps
        try:
            messages.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
        except ValueError:
            # Skip invalid timestamps but still sort valid ones
            valid_messages = []
            invalid_messages = []
            for msg in messages:
                try:
                    datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    valid_messages.append(msg)
                except ValueError:
                    invalid_messages.append(msg)
            
            valid_messages.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
            messages[:] = valid_messages + invalid_messages
        
        # Add messages
        for msg in messages:
            output.append(f"[{msg['timestamp']}] {msg['content']}")
            output.append("|||")  # Using ||| as a specific separator between messages
            
    # Write output to messages.txt
    with open('messages.txt', 'w') as f:
        f.write("\n".join(output))

format_messages_as_text()