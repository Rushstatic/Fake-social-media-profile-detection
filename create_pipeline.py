#create_pipeline.py
import pandas as pd
import re
import joblib
import os
import json
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report 
from xgboost import XGBClassifier

# --- Define All Helper Functions ---
def has_suspicious_link(text):
    if not isinstance(text, str): return False
    return 'telegram' in text.lower() or 't.me' in text.lower() or 'onlyfans' in text.lower()

def count_suspicious_bio_words(text):
    suspicious_bio_keywords = ['giveaway', 'free', 'followers', 'linkinbio', 'promo', 'dm for collab', 'ambassador']
    if not isinstance(text, str): return 0
    return sum(1 for word in suspicious_bio_keywords if word in text.lower())

def count_suspicious_username_words(text):
    suspicious_username_keywords = ['official', 'service', 'link', 'free', 'buy', 'shop', 'store', 'promo']
    if not isinstance(text, str): return 0
    return sum(1 for word in suspicious_username_keywords if word in text.lower())

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    tokens = word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return " ".join(stemmed_tokens)


# In create_pipeline.py

def main():
    """A unified pipeline to process data, train the model, and save all artifacts."""
    print("--- Starting Unified NLP Pipeline ---")
    
    # 1. Load Raw Data
    input_dir = "raw_json_data"
    raw_data = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    raw_data.append(json.load(f))
                except json.JSONDecodeError:
                    continue
    
    # 2. Process into a DataFrame
    records = []
    for entry in raw_data:
        records.append({
            'username': entry.get('username', ''), 'bio': entry.get('bio', ''),
            'is_verified': entry.get('is_verified', False), 'followers_count': entry.get('followers_count', 0),
            'following_count': entry.get('following_count', 0), 'posts_count': entry.get('media_count', 0),
            'has_profile_pic': bool(entry.get('profile_pic_url')), 'is_business_account': entry.get('is_business_account', False),
            'bio_length': len(entry.get('bio', '')), 'external_url': bool(entry.get('bio_links')),
            'account_label': entry.get('account_label', 'unknown')
        })
    df = pd.DataFrame(records)
    df['target'] = df['account_label'].apply(lambda x: 1 if x == 'fake' else 0)

    # 3. Create ALL Features
    df['followers_to_following_ratio'] = df['followers_count'] / (df['following_count'] + 1)
    df['username_digit_count'] = df['username'].apply(lambda x: sum(c.isdigit() for c in str(x)))
    df['has_suspicious_link'] = df['bio'].apply(has_suspicious_link)
    df['suspicious_bio_word_count'] = df['bio'].apply(count_suspicious_bio_words)
    df['suspicious_username_word_count'] = df['username'].apply(count_suspicious_username_words)
    df['cleaned_bio'] = df['bio'].apply(preprocess_text)

    # 4. Create and Fit the Vectorizer for NLP Features
    tfidf_vectorizer = TfidfVectorizer(max_features=100)
    tfidf_features = tfidf_vectorizer.fit_transform(df['cleaned_bio']).toarray()
    tfidf_df = pd.DataFrame(tfidf_features, columns=tfidf_vectorizer.get_feature_names_out())

    # 5. Create the Final DataFrame for Training
    numerical_and_custom_features = df.drop(columns=['username', 'bio', 'account_label', 'cleaned_bio', 'target'])
    target_series = df['target']

    X_final = pd.concat([numerical_and_custom_features.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)
    y_final = target_series

    # 6. Train the Model using the clean X and y
# 6. Train the Model using the clean X and y
    X_train, X_test, y_train, y_test = train_test_split(X_final, y_final, test_size=0.2, random_state=42)

# --- ADD THIS NEW SECTION HERE ---
# Calculate the scale_pos_weight based on the training data
    real_count = y_train.value_counts()[0]
    fake_count = y_train.value_counts()[1]
    scale = real_count / fake_count
    print(f"Class Imbalance Scale: {scale:.2f}") # Optional: print the scale to see it

# Add the 'scale_pos_weight' parameter when you create the model
    model = XGBClassifier(
    use_label_encoder=False, 
    eval_metric='logloss', 
    random_state=42,
    scale_pos_weight=scale  # The new parameter is added here
)
# --- END OF NEW SECTION ---

    model.fit(X_train, y_train)

    # 7. Evaluate and Save
    print("\n--- Final Model Classification Report ---")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))
    
    print("\nSaving final model and vectorizer...")
    joblib.dump(model, 'final_nlp_model.joblib')
    joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')
    print("Artifacts saved successfully.")
if __name__ == "__main__":
    main()