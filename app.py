# app.py
import joblib
import pandas as pd
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import certifi
import google.generativeai as genai
import sqlite3
from datetime import datetime

# NLP Imports
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import os

# PDF Import
from fpdf import FPDF

# 1. Initialize App & Configure APIs
app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = 'AIzaSyDyY5XIWED7zGMK32uX6ObdqI57LcSFk8Q' 
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Load the ADVANCED NLP Model & Vectorizer
try:
    model = joblib.load('final_nlp_model.joblib')
    vectorizer = joblib.load('tfidf_vectorizer.joblib')
    print("NLP model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("ERROR: Model or vectorizer file not found. Please run create_pipeline.py.")
    model = None
    vectorizer = None

# 3. Define ALL Helper Functions for Live Processing
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
    
    df_numerical = pd.DataFrame([record]).drop(columns=['username', 'bio'])
    
    cleaned_bio = preprocess_text(record['bio'])
    tfidf_features = vectorizer.transform([cleaned_bio]).toarray()
    tfidf_df = pd.DataFrame(tfidf_features, columns=vectorizer.get_feature_names_out())
    
    return pd.concat([df_numerical.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)

def get_gemini_analysis(scraped_data, prediction, confidence):
    try:
        prompt = f"""
You are a Senior Social Media Intelligence Analyst. Based on the profile metadata and model prediction below, deliver a concise, high-accuracy credibility assessment.

 **📄Profile Metadata**
• Username: {scraped_data.get('username')}
• Bio: {scraped_data.get('bio')}
• Followers: {scraped_data.get('followers_count')}
• Following: {scraped_data.get('following_count')}

 **📊Model Output**
• Prediction: LIKELY {prediction.upper()}
• Confidence: {confidence:.2f}%

 **🧠Your Response Must Include**
 **1️⃣Executive Summary**  
→ One sentence summarizing the account's overall credibility.

 **2️⃣Risk Indicators**  
→ Up to 2 short bullets starting with highlighting specific credibility concerns.

 **3️⃣Behavioral Tag**
→ One descriptive label that best characterizes the account's behavior or intent, by analyzing bio the label can be a possible profession, like if 
users bio consist of mbbs you can tell with genuine user that doctor just like this proffessions singers, engineer etc. Don't add complex proffessions
if you have to add then also add marathi translation of it.
🎯 Be concise, analytical, and business-appropriate. Avoid speculation. Focus on observable signals and model-backed insights. add emojis wherever necessary we are showing 
this report to show how our project is best so show accordingly.
"""

        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return "AI analysis could not be generated."

class PDF(FPDF):
    def header(self):
        self.add_font("DejaVu", "", "DejaVuSans.ttf")
        self.set_font('helvetica', 'B', 20)
        self.cell(0, 10, 'Fake Buster Analysis Report', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def create_pdf_report(data):
    pdf = PDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
        # Add the username as a subtitle below the main header
    username = data.get('username', 'N/A')
    pdf.set_font('helvetica', 'I', 12)
    pdf.cell(0, 10, f"Report for Profile: {username}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10) # Add extra space
    
    pdf.set_font('helvetica', 'B', 16)
    if data['prediction'] == 'Fake':
        pdf.set_text_color(220, 53, 69) # Red
    else:
        pdf.set_text_color(40, 167, 69) # Green
    pdf.cell(0, 10, f"Prediction: {data['prediction']}", new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, f"Confidence: {data['confidence_percent']}%", new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(5)

    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'AI Analyst Report', new_x="LMARGIN", new_y="NEXT", align='L')
    
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, data['ai_analysis'])

    return bytes(pdf.output())
# === Helper: Log searches into SQLite ===
# Add this import at the top of your Python file
import sqlite3
from datetime import datetime

# Your updated function
def log_search(username, prediction, confidence):
    conn = sqlite3.connect('search_history.db')
    c = conn.cursor()
    # The CREATE TABLE statement can stay the same
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            prediction TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # THE FIX: We now provide the timestamp from Python
    # This ensures it uses your server's local time (IST)
    c.execute('INSERT INTO searches (username, prediction, confidence, timestamp) VALUES (?, ?, ?, ?)',
              (username, prediction, confidence, datetime.now()))
    
    conn.commit()
    conn.close()
# 4. Define API Endpoints
@app.route('/predict', methods=['POST'])
def predict():
    if model is None or vectorizer is None:
        return jsonify({'error': 'Model or vectorizer is not loaded'}), 500
    
    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({'error': 'Username is required'}), 400
    
    username_to_check = data['username']
    
    scraped_data = {}
    try:
        api_key = '68a2090756d03bd6417bd25f'
        api_url = f"https://api.scrapingdog.com/instagram/profile?api_key={api_key}&username={username_to_check}"
        response = requests.get(api_url, timeout=30, verify=certifi.where())
        response.raise_for_status()
        scraped_data = response.json()
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
    log_search(username_to_check, result_label, confidence)
    return jsonify({
        'prediction': result_label,
        'confidence_percent': f"{confidence:.2f}",
        'ai_analysis': ai_analysis,
        'username': username_to_check,
        'scraped_data': scraped_data
    })
    
@app.route('/recent-searches', methods=['GET'])
def recent_searches():
    days = int(request.args.get('days', 1))  # default 1 day
    conn = sqlite3.connect('search_history.db')
    c = conn.cursor()
    query = """
        SELECT username, prediction, confidence, timestamp
        FROM searches
        WHERE timestamp >= datetime('now', ?)
        ORDER BY timestamp DESC
    """
    c.execute(query, (f'-{days} days',))
    rows = c.fetchall()
    conn.close()
    return jsonify([
        {'username': r[0], 'prediction': r[1], 'confidence': r[2], 'timestamp': r[3]}
        for r in rows
    ])

@app.route('/generate-report', methods=['POST'])
def generate_report():
    data = request.get_json()
    if not data:
        return 'Error: No data provided', 400
    
    pdf_data = create_pdf_report(data)
    
    return Response(pdf_data,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=FakeBuster_Report_{data.get("username")}.pdf'})
    
    
    
# Add this to your main Flask file (e.g., app.py)

from flask import jsonify

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('search_history.db')
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    c = conn.cursor()
    
    # Fetch the 10 most recent searches in descending order
    c.execute('SELECT username, prediction, timestamp FROM searches ORDER BY timestamp DESC LIMIT 10')
    
    history_data = c.fetchall()
    conn.close()
    
    # Convert the database rows to a list of dictionaries
    history_list = [dict(row) for row in history_data]
    
    return jsonify(history_list)

    
# 5. Run the Flask App
if __name__ == '__main__':
    app.run(debug=True, port=5000)