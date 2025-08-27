# app.py (Final Complete Version)
import joblib
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import certifi
import google.generativeai as genai
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os
from fpdf import FPDF

# --- 1. Initialize App & Configure Gemini ---
app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = 'AIzaSyD7Me8MrIDsLaPhYVb_Z2NBiSHAgt5PCKU' # Paste your key here
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')

try:
    model = joblib.load('final_nlp_model.joblib')
    vectorizer = joblib.load('tfidf_vectorizer.joblib')
    print("NLP model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("ERROR: Model or vectorizer file not found. Please re-run create_pipeline.py.")
    model = None
    vectorizer = None

#2. Define ALL Helper Functions for Live Processing ---
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

def process_input_data(scraped_data, vectorizer):
    record = {
        'is_verified': scraped_data.get('is_verified', False), 'followers_count': scraped_data.get('followers_count', 0),
        'following_count': scraped_data.get('following_count', 0), 'posts_count': scraped_data.get('media_count', 0),
        'has_profile_pic': bool(scraped_data.get('profile_pic_url')), 'is_business_account': scraped_data.get('is_business_account', False),
        'bio_length': len(scraped_data.get('bio', '')), 'external_url': bool(scraped_data.get('bio_links')),
        'username': scraped_data.get('username', ''), 'bio': scraped_data.get('bio', '')
    }
    record['followers_to_following_ratio'] = record['followers_count'] / (record['following_count'] + 1)
    record['username_digit_count'] = sum(c.isdigit() for c in str(record.get('username', '')))
    record['has_suspicious_link'] = has_suspicious_link(record['bio'])
    record['suspicious_bio_word_count'] = count_suspicious_bio_words(record['bio'])
    record['suspicious_username_word_count'] = count_suspicious_username_words(record['username'])
    
    df_numerical = pd.DataFrame([record])
    df_numerical = df_numerical.drop(columns=['username', 'bio'])
    
    cleaned_bio = preprocess_text(record['bio'])
    tfidf_features = vectorizer.transform([cleaned_bio]).toarray()
    tfidf_df = pd.DataFrame(tfidf_features, columns=vectorizer.get_feature_names_out())
    
    return pd.concat([df_numerical.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)


def get_gemini_analysis(scraped_data, prediction, confidence):
    """Calls the Gemini API to get a detailed analysis."""
    try:
        prompt = f"""
        You are an expert social media analyst. You have been given profile data and a prediction.

        **Profile Data:**
        - Username: {scraped_data.get('username')}
        - Bio: {scraped_data.get('bio')}
        - Followers: {scraped_data.get('followers_count')}
        - Following: {scraped_data.get('following_count')}

        **Primary Model Prediction:**
        - Verdict: LIKELY {prediction.upper()}
        - Confidence: {confidence:.2f}%

        **Your Task:**
        1. Write a very concise, one-sentence **Analysis Summary**.
        2. After the summary, create a list of up to 3 bulleted **"Points of Caution."** Start each point with the marker CAUTION:.
        """
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return "AI analysis could not be generated."
    
    #3. NEW: Define the PDF Creation Function
class PDF(FPDF):
    def header(self):
        # Logo (optional, if you have a logo.png in your folder)
        #self.image('logo.png', 10, 8, 33)
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, 'Fake Buster Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# In app.py

def create_pdf_report(data):
    """Creates a PDF report from the analysis data."""
    pdf = PDF()
    pdf.add_page()
    
    # --- FIX IS HERE ---
    # Add a Unicode font that supports a wide range of characters
    # This font is included with the fpdf2 library
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    
    # Prediction Verdict
    pdf.set_font('helvetica', 'B', 16) # Use standard font for the title
    if data['prediction'] == 'Fake':
        pdf.set_text_color(220, 53, 69) # Red
    else:
        pdf.set_text_color(40, 167, 69) # Green
    pdf.cell(0, 10, f"Prediction: {data['prediction']}", ln=1)
    pdf.set_text_color(0, 0, 0) # Reset color
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, f"Confidence: {data['confidence_percent']}%", ln=1)
    pdf.ln(5)

    # AI Analyst Report
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'AI Analyst Report', ln=1)
    
    # --- USE THE UNICODE FONT for the main text ---
    pdf.set_font('DejaVu', '', 12) 
    pdf.multi_cell(0, 10, data['ai_analysis'])

    # Return the PDF data in memory
    return bytes(pdf.output())

# --- 4. Define the API Prediction Endpoint ---
@app.route('/predict', methods=['POST'])
def predict():
    if model is None or vectorizer is None:
        return jsonify({'error': 'Model or vectorizer is not loaded'}), 500
    
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    username_to_check = data['username']
    print(f"Received live request for: {username_to_check}")

    scraped_data = {}
    try:
        api_key = '68a2090756d03bd6417bd25f' # Put your ScrapingDog key here
        api_url = f"https://api.scrapingdog.com/instagram/profile?api_key={api_key}&username={username_to_check}"
        response = requests.get(api_url, timeout=30, verify=certifi.where())
        response.raise_for_status()
        scraped_data = response.json()
        print("Successfully scraped live data.")
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return jsonify({'error': f'Failed to scrape data for {username_to_check}'}), 500

    processed_df = process_input_data(scraped_data, vectorizer)
    
    processed_df = processed_df[model.get_booster().feature_names]

    prediction = model.predict(processed_df)
    probability = model.predict_proba(processed_df)
    result_label = 'Fake' if prediction[0] == 1 else 'Real'
    confidence = float(max(probability[0])) * 100
    
    ai_analysis = get_gemini_analysis(scraped_data, result_label, confidence)
    
    return jsonify({
        'prediction': result_label,
        'confidence_percent': f"{confidence:.2f}",
        'ai_analysis': ai_analysis
    })

# In app.py

# In app.py

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json()
    if not data:
        return 'Error: No data provided', 400
        
    # Create the PDF in memory
    pdf_data = create_pdf_report(data)
    
    # Send the PDF back to the browser for download
    # The browser will handle asking the user where to save it.
    return Response(pdf_data,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=Fake_Buster_Report.pdf'})
    
    
#5. Run the Flask App
if __name__ == '__main__':
    app.run(debug=True, port=5000)