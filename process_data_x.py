# process_data_x.py
import pandas as pd
import json
import os

def process_x_data(raw_data):
    """Extracts key features from the raw X/Twitter JSON data."""
    processed_records = []
    print(f"  -> Found {len(raw_data)} total files to process.")

    for i, entry in enumerate(raw_data):
        try:
            user_info = entry['data']['tweetResult']['result']['core']['user_results']['result']
            
            if user_info.get('__typename') != 'User' or 'legacy' not in user_info:
                print(f"  -> File {i+1}: Skipping (Protected or unavailable profile)")
                continue

            user_data = user_info['legacy']
            label = entry.get('account_label', 'unknown')
            
            print(f"  -> File {i+1}: Successfully processing user '{user_data.get('screen_name')}'")

            record = {
                'username': user_data.get('screen_name', ''),
                'full_name': user_data.get('name', ''),
                'is_verified': user_info.get('is_blue_verified', False),
                'followers_count': user_data.get('followers_count', 0),
                'following_count': user_data.get('friends_count', 0),
                'posts_count': user_data.get('statuses_count', 0),
                'has_profile_pic': not user_data.get('default_profile_image', True),
                'bio_length': len(user_data.get('description', '')),
                'account_label': label
            }
            processed_records.append(record)
        
        except (KeyError, TypeError):
            print(f"  -> File {i+1}: Skipping (Error message or wrong format)")
            continue
            
    return processed_records

def main():
    """Loads, processes, and saves the X data."""
    input_dir = "raw_json_data/x"
    output_csv = "processed_data_x.csv"

    print(f"Loading raw data from '{input_dir}'...")
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
        print(f"Error: The directory '{input_dir}' was not found.")
        return

    print("Processing X data...")
    processed_list = process_x_data(raw_data)
    
    if not processed_list:
        print("No valid data was processed.")
        return
        
    df = pd.DataFrame(processed_list)
    
    print("Creating engineered features for X data...")
    df['followers_to_following_ratio'] = df['followers_count'] / (df['following_count'] + 1)
    df['username_digit_count'] = df['username'].apply(lambda x: sum(c.isdigit() for c in str(x)))
    df['target'] = df['account_label'].apply(lambda x: 1 if x == 'fake' else 0)
    
    df.to_csv(output_csv, index=False)
    
    print(f"\nProcessing complete! Clean data saved to '{output_csv}'.")
    print("Here's a preview of your clean X data:")
    print(df.head())

if __name__ == "__main__":
    main()