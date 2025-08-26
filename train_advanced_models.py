# train_advanced_models.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

print("  Script Started  ")

# Load
DATASET_PATH = 'nlp_enriched_data.csv'
print(f"Loading final dataset from '{DATASET_PATH}'...")
df = pd.read_csv(DATASET_PATH)

# Define features
features = df.columns.drop('target')
target = 'target'

X = df[features]
y = df[target]

# Split model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Training XGBoost Model on {len(X_train)} samples...")
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_model.fit(X_train, y_train)

# Evaluate
print("\n--- XGBoost NLP Model Classification Report ---")
y_pred_xgb = xgb_model.predict(X_test)
print(classification_report(y_test, y_pred_xgb, target_names=['Real', 'Fake']))

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
