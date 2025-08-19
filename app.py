# app.py
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- 1. Initialize Flask App ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

# --- 2. Load the Trained Model ---
MODEL_PATH = 'xgboost_instagram_model.joblib'
print(f"Loading model from '{MODEL_PATH}'...")
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
except FileNotFoundError:
    print(f"Error: Model file not found at '{MODEL_PATH}'. Please run train_advanced_models.py first.")
    model = None

# --- 3. Define the Feature Processing Function ---
def process_input_data(scraped_data):
    """
    Takes raw scraped data (as a dictionary) and prepares it
    into a DataFrame for the model.
    """
    # Create a dictionary with the required features, using defaults if keys are missing
    record = {
        'is_verified': scraped_data.get('is_verified', False),
        'followers_count': scraped_data.get('followers_count', 0),
        'following_count': scraped_data.get('following_count', 0),
        'posts_count': scraped_data.get('media_count', 0), 
        'has_profile_pic': bool(scraped_data.get('profile_pic_url')),
        'is_business_account': scraped_data.get('is_business_account', False),
        'bio_length': len(scraped_data.get('bio', '')),
        'external_url': bool(scraped_data.get('bio_links')),
        # We need username to calculate username_digit_count
        'username': scraped_data.get('username', '') 
    }
    
    # Create engineered features
    record['followers_to_following_ratio'] = record['followers_count'] / (record['following_count'] + 1)
    record['username_digit_count'] = sum(c.isdigit() for c in str(record['username']))
    
    # Define the exact feature order the model was trained on
    features_order = [
        'is_verified', 'followers_count', 'following_count', 'posts_count',
        'has_profile_pic', 'is_business_account', 'bio_length', 'external_url',
        'followers_to_following_ratio', 'username_digit_count'
    ]
    
    # Create a pandas DataFrame
    df = pd.DataFrame([record])
    # Ensure the column order is correct
    df = df[features_order]
    
    return df

# In app.py

import certifi # Make sure this is imported at the top
import requests # Make sure this is imported at the top

# ... (keep the rest of the file the same: app initialization, model loading, etc.) ...

# --- UPDATE THE API PREDICTION ENDPOINT ---
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not loaded'}), 500

    # Get the data from the POST request (e.g., username)
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    username_to_check = data['username']
    print(f"Received live request for: {username_to_check}")

    # --- 1. LIVE SCRAPING ---
    # Call the ScrapingDog API in real-time
    scraped_data = {}
    try:
        # Use the correct API URL for Instagram
        api_key = '68a2090756d03bd6417bd25f' # Make sure to put your key here
        api_url = f"https://api.scrapingdog.com/instagram/profile?api_key={api_key}&username={username_to_check}"
        
        print(f"Calling ScrapingDog API for '{username_to_check}'...")
        response = requests.get(api_url, timeout=30, verify=certifi.where())
        response.raise_for_status()
        scraped_data = response.json()
        print("Successfully scraped live data.")

    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return jsonify({'error': f'Failed to scrape data for {username_to_check}'}), 500

    # --- 2. LIVE PROCESSING ---
    processed_df = process_input_data(scraped_data)
    
    # --- 3. LIVE PREDICTION ---
    prediction = model.predict(processed_df)
    probability = model.predict_proba(processed_df)

    result_label = 'Fake' if prediction[0] == 1 else 'Real'
    confidence = float(max(probability[0])) * 100
    
    print(f"Prediction for '{username_to_check}': {result_label} with {confidence:.2f}% confidence.")
    
    # Return the final result
    return jsonify({
        'username': username_to_check,
        'prediction': result_label,
        'confidence_percent': f"{confidence:.2f}"
    })

# --- 5. Run the Flask App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)