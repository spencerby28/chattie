import pandas as pd

# Read the CSV file
try:
    df = pd.read_csv('messages.csv')
    
    # Count total rows before deduplication
    initial_count = len(df)
    
    # Drop duplicate rows based on message content
    df_no_duplicates = df.drop_duplicates(subset=['content'], keep='first')
    
    # Count rows after deduplication
    final_count = len(df_no_duplicates)
    
    # Save deduplicated data back to CSV
    df_no_duplicates.to_csv('messages.csv', index=True)
    
    duplicates_removed = initial_count - final_count
    print(f"Removed {duplicates_removed} duplicate messages")
    print(f"Final message count: {final_count}")

except Exception as e:
    print(f"Error processing messages.csv: {str(e)}")
