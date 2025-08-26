# app.py
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
# Import NLP tools
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

# Initialization
app = Flask(__name__)
CORS(app)

print("Loading NLP model and vectorizer...")
model = joblib.load('final_nlp_model.joblib')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.joblib')
print("Model and vectorizer loaded successfully.")

# 2.
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
def preprocess_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    tokens = word_tokenize(text.lower())
    stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return " ".join(stemmed_tokens)

# 3. feature processing
def process_input_data(scraped_data):
    
    record = {
        'is_verified': scraped_data.get('is_verified', False),
        'followers_count': scraped_data.get('followers_count', 0),
        'following_count': scraped_data.get('following_count', 0),
        'posts_count': scraped_data.get('media_count', 0),
        'has_profile_pic': bool(scraped_data.get('profile_pic_url')),
        'is_business_account': scraped_data.get('is_business_account', False),
        'bio_length': len(scraped_data.get('bio', '')),
        'external_url': bool(scraped_data.get('bio_links')),
        'username': scraped_data.get('username', '')
    }
    record['followers_to_following_ratio'] = record['followers_count'] / (record['following_count'] + 1)
    record['username_digit_count'] = sum(c.isdigit() for c in str(record['username']))
    
    # Create a DataFrame for the numerical features
    df_numerical = pd.DataFrame([record])
    df_numerical = df_numerical.drop(columns=['username'])

    # Process text feature
    bio_text = scraped_data.get('bio', '')
    cleaned_bio = preprocess_text(bio_text)
    
    # Use the loaded vectorizer to transform the bio
    tfidf_features = tfidf_vectorizer.transform([cleaned_bio]).toarray()
    df_text = pd.DataFrame(tfidf_features, columns=[f'word_{i}' for i in range(tfidf_features.shape[1])])

    # Combine numerical and text features
    df_final = pd.concat([df_numerical.reset_index(drop=True), df_text.reset_index(drop=True)], axis=1)
    return df_final

# 4 api prediction
@app.route('/predict', methods=['POST'])
def predict():
    scraped_data = request.get_json()
    if not scraped_data:
        return jsonify({'error': 'No data provided'}), 400

    processed_df = process_input_data(scraped_data)
    
    prediction = model.predict(processed_df)
    probability = model.predict_proba(processed_df)

    result_label = 'Fake' if prediction[0] == 1 else 'Real'
    confidence = float(max(probability[0])) * 100
    
    return jsonify({
        'prediction': result_label,
        'confidence_percent': f"{confidence:.2f}"
    })

# Final run
if __name__ == '__main__':
    app.run(debug=True, port=5000)
