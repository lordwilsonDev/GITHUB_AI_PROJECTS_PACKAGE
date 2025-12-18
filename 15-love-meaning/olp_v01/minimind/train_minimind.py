# minimind/train_minimind.py

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from joblib import dump

DATASET_CSV = Path("minimind/training_data.csv")
MODEL_PATH = Path("minimind/minimind_v0.1.joblib")


def train_baseline_predictor():
    if not DATASET_CSV.exists():
        print("Dataset not found. Run extract_dataset.py first.")
        return

    df = pd.read_csv(DATASET_CSV)
    print(f"📊 Loaded {len(df)} samples from dataset")

    # Ensure label is numeric 0/1
    df["label_ok"] = df["label_ok"].astype(int)

    # Need at least 2 classes
    if df["label_ok"].nunique() < 2:
        print("⚠️ Need at least 2 classes (some 0s and some 1s). Skipping training.")
        return

    # Need at least a couple of samples
    if len(df) < 3:
        print("⚠️ Need at least 3 samples to train/test. Skipping training.")
        return

    X = df[["CRC_raw", "latency_ms", "safety_score"]].astype(float)
    y = df["label_ok"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    print(f"✅ Training samples: {len(X_train)} | Test samples: {len(X_test)}")

    model = LogisticRegression()
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"✅ MiniMind v0.1 trained. Accuracy: {score:.2f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    dump(model, MODEL_PATH)
    print(f"💾 Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_baseline_predictor()
