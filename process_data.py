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