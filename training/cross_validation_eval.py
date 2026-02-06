# cross_validation_eval.py
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.datasets import make_classification
import numpy as np

# --- 1️⃣ Create or load dataset (replace with your own data if available) ---
X, y = make_classification(
    n_samples=500, n_features=10, n_informative=5, n_redundant=2,
    random_state=42
)

# --- 2️⃣ Define ensemble model (same as before) ---
rf = RandomForestClassifier(n_estimators=100, random_state=42)
gb = GradientBoostingClassifier(random_state=42)
ensemble = VotingClassifier(estimators=[('rf', rf), ('gb', gb)], voting='soft')

# --- 3️⃣ Define stratified 5-fold cross-validation ---
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# --- 4️⃣ Evaluate using accuracy ---
cv_scores = cross_val_score(ensemble, X, y, cv=cv, scoring='accuracy')

print(f"Cross-Validation Scores: {cv_scores}")
print(f"Mean Accuracy: {np.mean(cv_scores):.3f}")
print(f"Standard Deviation: {np.std(cv_scores):.3f}")
