# process_data.py
import json
import pandas as pd
import os

# The name of the raw JSON file 
INPUT_JSON_FILE = 'raw_data_instagram.json' 
# The name of the clean CSV file
OUTPUT_CSV_FILE = 'processed_data_instagram.csv'

# In process_data.py

def process_instagram_data(raw_data):
    """Extracts key features from the raw Instagram JSON data."""
    processed_records = []
    
    for entry in raw_data:
        label = entry.get('account_label', 'unknown')
        

        record = {
            
            'username': entry.get('full_name', 'unknown_user'), 
            'full_name': entry.get('full_name', ''),
            'bio': entry.get('bio', ''),
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

# 

# In process_data.py

def main():
    """Main function to load, process, and save the data."""
    input_dir = "raw_json_data"
    print(f"Loading raw data from '{input_dir}' directory...")
    
    raw_data = []
    try:
        for filename in os.listdir(input_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(input_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:

                        raw_data.append(json.load(f))
                    except json.JSONDecodeError:
                        print(f"  -> Skipping corrupted or empty file: {filename}")
                        continue
    except FileNotFoundError:
        print(f"Error: The directory '{input_dir}' was not found. Did you run collect_data.py first?")
        return

    print("Processing data...")
    processed_list = process_instagram_data(raw_data)
    
    if not processed_list:
        print("No data was processed. Check the content of your JSON files.")
        return
        
    df = pd.DataFrame(processed_list)
    
    print("Creating engineered features...")
    df['followers_to_following_ratio'] = df['followers_count'] / (df['following_count'] + 1)
    df['username_digit_count'] = df['username'].apply(lambda x: sum(c.isdigit() for c in str(x)))
    df['target'] = df['account_label'].apply(lambda x: 1 if x == 'fake' else 0)
    
    df.to_csv(OUTPUT_CSV_FILE, index=False)
    
    print(f"\nProcessing complete! Clean data saved to '{OUTPUT_CSV_FILE}'.")
    print("Here's a preview of your clean data:")
    print(df.head())

if __name__ == "__main__":
    main()
