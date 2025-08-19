# process_data.py
import json
import pandas as pd
import os

# The name of the raw JSON file you created
INPUT_JSON_FILE = 'raw_data_instagram.json' 
# The name of the clean CSV file we will create
OUTPUT_CSV_FILE = 'processed_data_instagram.csv'

# In process_data.py

def process_instagram_data(raw_data):
    """Extracts key features from the raw Instagram JSON data."""
    processed_records = []
    
    for entry in raw_data:
        label = entry.get('account_label', 'unknown')
        
        # --- Feature Extraction (UPDATED LOGIC) ---
        # The 'username' field seems to be missing from the API response.
        # We will use 'full_name' as the main identifier.
        record = {
            # FIX: Use 'full_name' since 'username' is missing
            'username': entry.get('full_name', 'unknown_user'), 
            'full_name': entry.get('full_name', ''),
            'is_verified': entry.get('is_verified', False),
            'followers_count': entry.get('followers_count', 0),
            'following_count': entry.get('following_count', 0),
            'posts_count': entry.get('media_count', 0), 
            'has_profile_pic': bool(entry.get('profile_pic_url')),
            'is_business_account': entry.get('is_business_account', False),
            'bio_length': len(entry.get('bio', '')),
            'external_url': bool(entry.get('bio_links')),
            'account_label': label
        }
        
        processed_records.append(record)
        
    return processed_records

# In process_data.py

def main():
    """Main function to load, process, and save the data."""
    
    # CHANGE: Point to the new directory
    input_dir = "raw_json_data"
    print(f"Loading raw data from '{input_dir}' directory...")
    
    # CHANGE: Read all individual JSON files from the directory
    raw_data = []
    try:
        for filename in os.listdir(input_dir):
            if filename.endswith(".json"):
                with open(os.path.join(input_dir, filename), 'r') as f:
                    raw_data.append(json.load(f))
    except FileNotFoundError:
        print(f"Error: The directory '{input_dir}' was not found. Did you run collect_data.py first?")
        return

    # The rest of the function remains the same...
    print("Processing data...")
    processed_list = process_instagram_data(raw_data)
    
    # ... (the rest of the code is unchanged)
    
    if not processed_list:
        print("No data was processed. Check your raw JSON file for content.")
        return
        
    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.DataFrame(processed_list)
    
    print("Creating engineered features...")
    # --- Feature Engineering ---
    # Create the follower/following ratio, adding 1 to avoid division by zero
    df['followers_to_following_ratio'] = df['followers_count'] / (df['following_count'] + 1)
    # Get the number of digits in the username
    df['username_digit_count'] = df['username'].apply(lambda x: sum(c.isdigit() for c in str(x)))
    
    # Convert our target label to a number (fake=1, real=0)
    df['target'] = df['account_label'].apply(lambda x: 1 if x == 'fake' else 0)
    
    # Save the clean data to a CSV file
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    
    print(f"\nProcessing complete! Clean data saved to '{OUTPUT_CSV_FILE}'.")
    print("Here's a preview of your clean data:")
    print(df.head())

if __name__ == "__main__":
    main()