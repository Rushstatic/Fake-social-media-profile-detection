# baseline_comparison.py
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.datasets import make_classification

# --- Create or load your dataset ---
X, y = make_classification(
    n_samples=500, n_features=10, n_informative=5, n_redundant=2,
    random_state=42
)

# --- Train-test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --- Define baseline models ---
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "SVM": SVC(probability=True, random_state=42),
    "KNN": KNeighborsClassifier(),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": GradientBoostingClassifier(random_state=42)
}

# --- Train and evaluate ---
results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    results.append((name, acc, f1))

# --- Ensemble model ---
ensemble = VotingClassifier(
    estimators=[('rf', models["Random Forest"]), ('xgb', models["XGBoost"])],
    voting='soft'
)
ensemble.fit(X_train, y_train)
y_pred_ens = ensemble.predict(X_test)
acc_ens = accuracy_score(y_test, y_pred_ens)
f1_ens = f1_score(y_test, y_pred_ens)
results.append(("Proposed Ensemble", acc_ens, f1_ens))

# --- Display results ---
print("\nModel Performance Comparison:")
print("Model\t\tAccuracy\tF1-Score")
for name, acc, f1 in results:
    print(f"{name:20s} {acc:.3f}\t\t{f1:.3f}")
