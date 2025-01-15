import pandas as pd

try:
    # Read the CSV file
    df = pd.read_csv('messages.csv')
    
    # Select only the specified columns
    columns_to_keep = ['sender_name', 'channel_id', 'content', '$createdAt']
    df_cleaned = df[columns_to_keep]
    
    # Remove bot messages
    df_cleaned = df_cleaned[~df_cleaned['sender_name'].isin(['bot', "Bot", "Chattie Bot"])]
    
    # Save cleaned data back to CSV
    df_cleaned.to_csv('messages.csv', index=False)
    
    print(f"Cleaned messages.csv - kept columns: {', '.join(columns_to_keep)}")
    print(f"Removed bot messages")
    print(f"Total messages: {len(df_cleaned)}")

except Exception as e:
    print(f"Error cleaning messages.csv: {str(e)}")
