"""
Step 3a: baseline classifier.

Character n-gram TF-IDF + Logistic Regression. Runs fully offline (no model
hub download needed), and char n-grams are a solid choice here because the
text is multilingual/code-mixed — word-level features fragment badly across
Hausa/Igbo/Yoruba/Pidgin, but character n-grams still catch shared roots and
morphology.

This is the "does the pipeline work at all" sanity check before the heavier
transformer fine-tune (see train_transformer.py, run on Colab/Kaggle where
the Hugging Face Hub is reachable).
"""

import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "labeled" / "labeled_dataset.csv"
MODEL_OUT = REPO_ROOT / "models" / "baseline_tfidf_logreg.joblib"


def load_data():
    texts, labels = [], []
    with open(DATA_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def main():
    texts, labels = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), min_df=2, max_features=20000)),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}\n")
    print(classification_report(y_test, preds, digits=3))

    labels_sorted = sorted(set(labels))
    cm = confusion_matrix(y_test, preds, labels=labels_sorted)
    print("Confusion matrix (rows=true, cols=predicted):")
    print("labels:", labels_sorted)
    for row in cm:
        print(row)

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_OUT)
    print(f"\nModel saved to: {MODEL_OUT}")


if __name__ == "__main__":
    main()
