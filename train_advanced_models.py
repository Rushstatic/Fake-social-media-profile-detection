<<<<<<< HEAD
# train_advanced_models.py (Final NLP Version)
=======
# train_advanced_models.py
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

<<<<<<< HEAD
print("--- Script Started: Training Final NLP Model ---")

# --- 1. Load the FINAL NLP-Enriched Data ---
=======
print("  Script Started  ")

# Load
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
DATASET_PATH = 'nlp_enriched_data.csv'
print(f"Loading final dataset from '{DATASET_PATH}'...")
df = pd.read_csv(DATASET_PATH)

<<<<<<< HEAD
# --- 2. Define Features (X) and Target (y) ---
# The features are all columns EXCEPT the 'target' column.
=======
# Define features
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
features = df.columns.drop('target')
target = 'target'

X = df[features]
y = df[target]

<<<<<<< HEAD
# --- 3. Split Data and Train Model ---
=======
# Split model
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Training XGBoost Model on {len(X_train)} samples...")
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_model.fit(X_train, y_train)

<<<<<<< HEAD
# --- 4. Evaluate ---
=======
# Evaluate
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
print("\n--- XGBoost NLP Model Classification Report ---")
y_pred_xgb = xgb_model.predict(X_test)
print(classification_report(y_test, y_pred_xgb, target_names=['Real', 'Fake']))

<<<<<<< HEAD
# --- 5. Save the Final Model ---
MODEL_FILENAME = 'final_nlp_model.joblib'
print(f"\nSaving the final NLP model...")
joblib.dump(xgb_model, MODEL_FILENAME)
print(f"Model saved as '{MODEL_FILENAME}'.")

print("\n--- Script Finished ---")
=======
# Nlp feature words as well
print("\n--- Top 15 Most Important Features ---")

feature_importance = pd.DataFrame({
    'feature': features,
    'importance': xgb_model.feature_importances_
}).sort_values('importance', ascending=False)

# Can change no for more or less features
print(feature_importance.head(15))

print("\nSaving the final NLP model...")
joblib.dump(xgb_model, 'final_nlp_model.joblib')
print("Model saved as 'final_nlp_model.joblib'.")

print("\n--- Script Finished ---")
>>>>>>> 6e2c125f6b247aa07a71a0746227657e04f82833
