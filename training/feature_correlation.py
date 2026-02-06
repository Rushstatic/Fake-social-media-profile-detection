# feature_correlation.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification

# --- 1️⃣ Generate or load your dataset ---
# Replace this synthetic dataset with your real dataframe (X)
X, y = make_classification(
    n_samples=500,
    n_features=10,
    n_informative=5,
    n_redundant=2,
    random_state=42
)

# Simulated feature names — replace these with your actual feature names
feature_names = [
    "followers_count", "following_count", "bio_length",
    "username_digit_count", "post_count", "followers_to_following_ratio",
    "external_url_flag", "verified_flag", "emoji_presence", "keyword_density"
]

df = pd.DataFrame(X, columns=feature_names)
df["label"] = y

# --- 2️⃣ Compute correlation matrix ---
corr_matrix = df.corr()

# --- 3️⃣ Plot and save heatmap ---
plt.figure(figsize=(10, 8))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    square=True,
    cbar_kws={"shrink": 0.8}
)
plt.title("Feature Correlation Heatmap for Fake Profile Detection Dataset")
plt.tight_layout()
plt.savefig("feature_correlation_heatmap.jpg", dpi=300)
plt.show()
