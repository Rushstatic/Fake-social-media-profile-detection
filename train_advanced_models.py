# train_advanced_models.py (Simplified Version)
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

print("--- Script Started ---")

try:
    # --- 1. Load the Clean Data ---
    DATASET_PATH = 'processed_data_instagram.csv'
    print(f"Loading dataset from '{DATASET_PATH}'...")
    df = pd.read_csv(DATASET_PATH)

    # --- 2. Define Features (X) and Target (y) ---
    features = [
        'is_verified', 'followers_count', 'following_count', 'posts_count',
        'has_profile_pic', 'is_business_account', 'bio_length', 'external_url',
        'followers_to_following_ratio', 'username_digit_count'
    ]
    target = 'target'

    X = df[features]
    y = df[target]

    # --- 3. Split Data into Training and Testing Sets ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Data split complete. Training set has {len(X_train)} samples.")

    # --- 4. Train and Evaluate XGBoost Model ---
    print("\n--- Training XGBoost Model ---")
    xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb_model.fit(X_train, y_train)
    print("--- XGBoost Model Training Finished ---")

    # Evaluate the model
    y_pred_xgb = xgb_model.predict(X_test)
    print("\nXGBoost Classification Report:")
    print(classification_report(y_test, y_pred_xgb, target_names=['Real', 'Fake']))

    # --- 5. Save the Model ---
    print("\nSaving the trained XGBoost model...")
    joblib.dump(xgb_model, 'xgboost_instagram_model.joblib')
    print("Model saved as 'xgboost_instagram_model.joblib'.")

except Exception as e:
    print(f"\nAN ERROR OCCURRED: {e}")

print("\n--- Script Finished ---")