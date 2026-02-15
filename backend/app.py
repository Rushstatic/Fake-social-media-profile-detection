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
import os
import logging

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')


from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# NLP Imports
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize

# PDF Import
from fpdf import FPDF

# ---------------------------
# Basic config & app init
# ---------------------------
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

app = Flask(__name__)
CORS(app)

# NOTE: Keep your API keys secure. This mirrors your original file.
GEMINI_API_KEY = 'AIzaSyDyY5XIWED7zGMK32uX6ObdqI57LcSFk8Q'
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

# ---------------------------
# Load model + vectorizer
# ---------------------------
model = None
vectorizer = None
saved_feature_names = None

try:
    model = joblib.load('final_nlp_model.joblib')
    vectorizer = joblib.load('tfidf_vectorizer.joblib')
    # optional: load explicit feature names if you saved them during training
    if os.path.exists('feature_names.joblib'):
        saved_feature_names = joblib.load('feature_names.joblib')
    logging.info("NLP model and vectorizer loaded successfully.")
except FileNotFoundError as e:
    logging.error("ERROR: Model or vectorizer file not found. Please run create_pipeline.py.")
    logging.exception(e)

# ---------------------------
# Helper functions
# ---------------------------
def has_suspicious_link(text):
    if not isinstance(text, str):
        return False
    return 'telegram' in text.lower() or 't.me' in text.lower() or 'onlyfans' in text.lower()

def count_suspicious_bio_words(text):
    suspicious_bio_keywords = ['giveaway', 'free', 'followers', 'linkinbio', 'promo', 'dm for collab', 'ambassador']
    if not isinstance(text, str):
        return 0
    return sum(1 for word in suspicious_bio_keywords if word in text.lower())

def count_suspicious_username_words(text):
    suspicious_username_keywords = ['official', 'service', 'link', 'free', 'buy', 'shop', 'store', 'promo']
    if not isinstance(text, str):
        return 0
    return sum(1 for word in suspicious_username_keywords if word in text.lower())

def preprocess_text(text):
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        # If NLTK stopwords aren't available in runtime, fallback to a small set
        stop_words = {"the", "and", "is", "in", "to", "of"}
    stemmer = PorterStemmer()
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#', '', text)
    text = re.sub(r'[^A-Za-z\s]', '', text)
    try:
        tokens = word_tokenize(text.lower())
    except LookupError:
        tokens = text.lower().split()

    stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]
    return " ".join(stemmed_tokens)

def process_input_data(scraped_data, vectorizer):
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
    # engineered features
    record['followers_to_following_ratio'] = record['followers_count'] / (record['following_count'] + 1)
    record['username_digit_count'] = sum(c.isdigit() for c in str(record.get('username', '')))
    record['has_suspicious_link'] = has_suspicious_link(record['bio'])
    record['suspicious_bio_word_count'] = count_suspicious_bio_words(record['bio'])
    record['suspicious_username_word_count'] = count_suspicious_username_words(record['username'])

    # Build numerical dataframe (drop username, bio)
    df_numerical = pd.DataFrame([record]).drop(columns=['username', 'bio'])

    # Clean bio & TF-IDF
    cleaned_bio = preprocess_text(record['bio'])
    tfidf_features = vectorizer.transform([cleaned_bio]).toarray()
    tfidf_df = pd.DataFrame(tfidf_features, columns=vectorizer.get_feature_names_out())

    combined = pd.concat([df_numerical.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)
    return combined

def get_gemini_analysis(scraped_data, prediction, confidence):
    try:
        prompt = f"""
You are a Senior Social Media Intelligence Analyst. Based on the profile metadata and model prediction below, deliver a concise, high-accuracy credibility assessment.

 **📄Profile Metadata**
• Username: {scraped_data.get('username')}
• Bio: {scraped_data.get('bio')}
• Followers: {scraped_data.get('followers_count')}
• Following: {scraped_data.get('following_count')}

**📊Model Output** • Prediction: LIKELY {prediction.upper()} • Confidence: {confidence:.2f}% **🧠Your Response Must Include** **1️⃣Executive Summary** → One sentence summarizing the account's overall credibility. **2️⃣Risk Indicators** → Up to 2 short bullets starting with highlighting specific credibility concerns. **3️⃣Behavioral Tag** → One descriptive label that best characterizes the account's behavior or intent, by analyzing bio the label can be a possible profession, like if users bio consist of mbbs you can tell with genuine user that doctor just like this proffessions singers, engineer etc. Don't add complex proffessions if you have to add then also add marathi translation of it. 🎯 Be concise, analytical, and business-appropriate. Avoid speculation. Focus on observable signals and model-backed insights. add emojis wherever necessary we are showing this report to show how our project is best so show accordingly. """
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.exception("Gemini API call failed")
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
    username = data.get('username', 'N/A')
    pdf.set_font('helvetica', 'I', 12)
    pdf.cell(0, 10, f"Report for Profile: {username}", new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 16)
    if data.get('prediction') == 'Fake':
        pdf.set_text_color(220, 53, 69) # Red
    else:
        pdf.set_text_color(40, 167, 69) # Green
    pdf.cell(0, 10, f"Prediction: {data.get('prediction')}", new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, f"Confidence: {data.get('confidence_percent')}%", new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.ln(5)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'AI Analyst Report', new_x="LMARGIN", new_y="NEXT", align='L')
    pdf.set_font('DejaVu', '', 12)
    pdf.multi_cell(0, 10, data.get('ai_analysis', ''))
    return bytes(pdf.output())

# ---------------------------
# SQLite logging helper
# ---------------------------
def log_search(username, prediction, confidence):
    conn = sqlite3.connect('search_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            prediction TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('INSERT INTO searches (username, prediction, confidence, timestamp) VALUES (?, ?, ?, ?)',
              (username, prediction, confidence, datetime.now()))
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('search_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            prediction TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

    
    

def fetch_with_retry(api_url):
    session = requests.Session()

    retry_strategy = Retry(
        total=1,  # try 3 times
        backoff_factor=0,  # wait 1s, 2s, 4s
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)

    response = session.get(api_url, timeout=8, verify=certifi.where())
    response.raise_for_status()
    return response.json()


# ---------------------------
# API endpoints
# ---------------------------
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
        api_key = '699001b6c495d5b82eef88fb'
        api_url = f"https://api.scrapingdog.com/instagram/profile?api_key={api_key}&username={username_to_check}"
        scraped_data = fetch_with_retry(api_url)
    except requests.exceptions.RequestException as e:
        logging.exception("API call failed")
        return jsonify({'error': f'Failed to scrape data for {username_to_check}'}), 500

    # Build processed features
    processed_df = process_input_data(scraped_data, vectorizer)

    # ---------- FEATURE ALIGNMENT (fix KeyError) ----------
    # Determine model expected features (best-effort)
    model_feats = None
    try:
        # XGBoost sklearn wrapper usually exposes get_booster().feature_names
        booster = model.get_booster()
        if hasattr(booster, 'feature_names') and booster.feature_names is not None:
            model_feats = list(booster.feature_names)
    except Exception:
        logging.debug("Could not read feature_names from model.get_booster().feature_names")

    # fallback: load saved feature list if present
    if model_feats is None and saved_feature_names is not None:
        logging.debug("Using saved feature_names.joblib as fallback")
        model_feats = list(saved_feature_names)

    # last fallback: use the features produced by our current pipeline (no change)
    if model_feats is None:
        logging.debug("No model feature list found; using current processed_df columns as model features")
        model_feats = list(processed_df.columns)

    # Debug printouts
    missing = [f for f in model_feats if f not in processed_df.columns]
    extra = [c for c in processed_df.columns if c not in model_feats]
    logging.debug(f"Processed columns: {len(processed_df.columns)}; Model expects: {len(model_feats)}")
    if missing:
        logging.debug(f"[DEBUG] Missing features count={len(missing)}; sample: {missing[:30]}")
    if extra:
        logging.debug(f"[DEBUG] Extra features count={len(extra)}; sample: {extra[:30]}")

    # Reindex to model features; fill missing with zeros and drop extras
    processed_df = processed_df.reindex(columns=model_feats, fill_value=0)

    # Ensure numeric dtype
    try:
        processed_df = processed_df.astype(float)
    except Exception:
        # If conversion fails for any reason, coerce numeric columns
        processed_df = processed_df.apply(pd.to_numeric, errors='coerce').fillna(0.0)

    # ----------------- PREDICTION -----------------
    try:
        prediction = model.predict(processed_df)
        # If the model supports predict_proba use it; otherwise fallback to predict output
        try:
            probability = model.predict_proba(processed_df)
            confidence = float(max(probability[0])) * 100
        except Exception:
            # If predict_proba not available, set a basic confidence
            confidence = 100.0 if prediction[0] in (0, 1) else 50.0
    except Exception as e:
        logging.exception("Model prediction failed")
        return jsonify({'error': 'Model prediction failed', 'details': str(e)}), 500

    result_label = 'Fake' if int(prediction[0]) == 1 else 'Real'
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
    days = int(request.args.get('days', 1))
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

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('search_history.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT username, prediction, timestamp FROM searches ORDER BY timestamp DESC LIMIT 10')
    history_data = c.fetchall()
    conn.close()
    history_list = [dict(row) for row in history_data]
    return jsonify(history_list)

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

