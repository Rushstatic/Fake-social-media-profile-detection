<<<<<<< HEAD
# In app.py

def process_input_data(scraped_data, vectorizer):
    """Processes scraped data for both numerical and all NLP features."""
    record = {
        'is_verified': scraped_data.get('is_verified', False),
        'followers_count': scraped_data.get('followers_count', 0),
        'following_count': scraped_data.get('following_count', 0),
        'posts_count': scraped_data.get('media_count', 0),
        'has_profile_pic': bool(scraped_data.get('profile_pic_url')),
        'is_business_account': scraped_data.get('is_business_account', False),
        'bio_length': len(scraped_data.get('bio', '')),
        'external_url': bool(scraped_data.get('bio_links')),
        'username': scraped_data.get('username', ''),
        'bio': scraped_data.get('bio', '')
    }
    record['followers_to_following_ratio'] = record['followers_count'] / (record['following_count'] + 1)
    record['username_digit_count'] = sum(c.isdigit() for c in str(record['username']))
    record['has_suspicious_link'] = has_suspicious_link(record['bio'])
    record['suspicious_bio_word_count'] = count_suspicious_bio_words(record['bio'])
    record['suspicious_username_word_count'] = count_suspicious_username_words(record['username'])
    
    df_numerical_and_custom = pd.DataFrame([record])

    cleaned_bio = preprocess_text(record['bio'])
    tfidf_features = vectorizer.transform([cleaned_bio]).toarray()
    
    # --- FIX IS HERE (Option A) ---
    # Rename the TF-IDF columns to the generic 'word_0', 'word_1', etc. format
    tfidf_df = pd.DataFrame(tfidf_features, columns=[f'word_{i}' for i in range(tfidf_features.shape[1])])

    df_numerical_and_custom = df_numerical_and_custom.drop(columns=['username', 'bio', 'target'], errors='ignore')
    
    df_final = pd.concat([df_numerical_and_custom.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)
    
    return df_final
=======
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
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
