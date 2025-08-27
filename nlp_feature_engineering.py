<<<<<<< HEAD
# nlp_feature_engineering.py (Final Corrected Version)
import pandas as pd
import re
import joblib
import os
=======
# nlp_feature_engineering.py 
import pandas as pd
import re
import joblib
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

<<<<<<< HEAD
# --- Define all functions first ---

def has_suspicious_link(text):
    if not isinstance(text, str): return False
=======
INPUT_CSV = 'processed_data_instagram.csv'
OUTPUT_CSV = 'nlp_enriched_data.csv'

print(f"Loading data from {INPUT_CSV}...")
df = pd.read_csv(INPUT_CSV)

def has_suspicious_link(text):
    """Checks if bio text contains keywords like 'telegram' or 't.me'."""
    if not isinstance(text, str):
        return False
    # Check for common suspicious link patterns
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
    if 'telegram' in text.lower() or 't.me' in text.lower() or 'onlyfans' in text.lower():
        return True
    return False

<<<<<<< HEAD
def count_suspicious_bio_words(text):
    suspicious_bio_keywords = ['giveaway', 'free', 'followers', 'linkinbio', 'promo', 'dm for collab', 'ambassador']
=======
#Kewords
suspicious_bio_keywords = ['giveaway', 'free', 'followers', 'linkinbio', 'promo', 'dm for collab', 'ambassador']
suspicious_username_keywords = ['official', 'service', 'link', 'free', 'buy', 'shop', 'store', 'promo']

def count_suspicious_bio_words(text):
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
    if not isinstance(text, str): return 0
    count = 0
    for word in suspicious_bio_keywords:
        if word in text.lower(): count += 1
    return count

def count_suspicious_username_words(text):
<<<<<<< HEAD
    suspicious_username_keywords = ['official', 'service', 'link', 'free', 'buy', 'shop', 'store', 'promo']
=======
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
    if not isinstance(text, str): return 0
    count = 0
    for word in suspicious_username_keywords:
        if word in text.lower(): count += 1
    return count

<<<<<<< HEAD
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
=======
# Text processing
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_text(text):
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    tokens = word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return " ".join(stemmed_tokens)

<<<<<<< HEAD
# --- Define the main execution logic ---

def main():
    """Loads, processes, and saves the final dataset and vectorizer."""
    INPUT_CSV = 'processed_data_instagram.csv'
    OUTPUT_CSV = 'nlp_enriched_data.csv'

    print(f"Loading data from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)

    print("Applying custom feature engineering...")
    df['has_suspicious_link'] = df['bio'].apply(has_suspicious_link)
    df['suspicious_bio_word_count'] = df['bio'].apply(count_suspicious_bio_words)
    df['suspicious_username_word_count'] = df['username'].apply(count_suspicious_username_words)

    print("Preprocessing bio text for TF-IDF...")
    df['cleaned_bio'] = df['bio'].apply(preprocess_text)

    print("Applying TF-IDF...")
    tfidf_vectorizer = TfidfVectorizer(max_features=100)
    tfidf_features = tfidf_vectorizer.fit_transform(df['cleaned_bio']).toarray()
    tfidf_df = pd.DataFrame(tfidf_features, columns=[f'word_{i}' for i in range(tfidf_features.shape[1])])

    print("Combining all features...")
    
    # This list defines the exact columns we want in our final dataset
    features_to_keep = [
        'is_verified', 'followers_count', 'following_count', 'posts_count',
        'has_profile_pic', 'is_business_account', 'bio_length', 'external_url',
        'followers_to_following_ratio', 'username_digit_count',
        'has_suspicious_link', 'suspicious_bio_word_count', 'suspicious_username_word_count',
        'target'
    ]
    df_base_features = df[features_to_keep]

    # Combine the selected features with the new TF-IDF features
    df_final = pd.concat([df_base_features.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)

    df_final.to_csv(OUTPUT_CSV, index=False)
    joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')

    print(f"\nNLP feature engineering complete!")
    print(f"Enriched data saved to '{OUTPUT_CSV}'.")
    print(f"TF-IDF Vectorizer saved to 'tfidf_vectorizer.joblib'.")
    print("New dataset shape:", df_final.shape)
    print(df_final.head())

# --- Run the main function ---
if __name__ == "__main__":
    main()
=======

print("Applying custom feature engineering...")
df['has_suspicious_link'] = df['bio'].apply(has_suspicious_link)
df['suspicious_bio_word_count'] = df['bio'].apply(count_suspicious_bio_words)
df['suspicious_username_word_count'] = df['username'].apply(count_suspicious_username_words)

print("Preprocessing bio text for TF-IDF...")
df['cleaned_bio'] = df['bio'].apply(preprocess_text)

print("Applying TF-IDF...")
tfidf_vectorizer = TfidfVectorizer(max_features=100)
tfidf_features = tfidf_vectorizer.fit_transform(df['cleaned_bio']).toarray()
tfidf_df = pd.DataFrame(tfidf_features, columns=[f'word_{i}' for i in range(tfidf_features.shape[1])])

print("Combining all features...")
df_original_features = df.drop(columns=['username', 'full_name', 'bio', 'account_label', 'cleaned_bio'])
df_final = pd.concat([
    df_original_features,
    df[['has_suspicious_link', 'suspicious_bio_word_count', 'suspicious_username_word_count']].reset_index(drop=True),
    tfidf_df
], axis=1)

df_final.to_csv(OUTPUT_CSV, index=False)
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer.joblib')

print(f"\nNLP feature engineering complete!")
print(f"Enriched data saved to '{OUTPUT_CSV}'.")
print(f"TF-IDF Vectorizer saved to 'tfidf_vectorizer.joblib'.")
print("New dataset shape:", df_final.shape)
print(df_final.head())
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
