"""
Step 3b (upgrade path): fine-tune a multilingual transformer on the labeled
dataset, instead of the char-ngram baseline.

NOTE: this needs internet access to the Hugging Face Hub to download the
base model — run it on Google Colab or Kaggle (both already in your
toolkit), not in a network-restricted sandbox. Upload data/labeled/labeled_dataset.csv
alongside this script, or mount Drive/Kaggle dataset.

Recommended base model: Davlan/afro-xlmr-base — pretrained on 20 African
languages including Hausa, Igbo, Yoruba; handles the code-mixed Pidgin
reasonably via its broad multilingual pretraining.
"""

import csv
import numpy as np
from datasets import Dataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)

MODEL_NAME = "Davlan/afro-xlmr-base"
DATA_PATH = "data/labeled/labeled_dataset.csv"
OUTPUT_DIR = "models/afro-xlmr-health-feedback"

LABELS = ["urgent_complaint", "general_feedback", "praise"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
ID2LABEL = {i: l for i, l in enumerate(LABELS)}


def load_data():
    texts, labels = [], []
    with open(DATA_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(LABEL2ID[row["label"]])
    return texts, labels


def main():
    texts, labels = load_data()
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)

    train_ds = Dataset.from_dict({"text": X_train, "label": y_train}).map(tokenize, batched=True)
    test_ds = Dataset.from_dict({"text": X_test, "label": y_test}).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=len(LABELS), id2label=ID2LABEL, label2id=LABEL2ID
    )

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=5,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="f1_macro",
    )

    def compute_metrics(eval_pred):
        logits, labels_ = eval_pred
        preds = np.argmax(logits, axis=-1)
        report = classification_report(
            labels_, preds, target_names=LABELS, output_dict=True, zero_division=0
        )
        return {"f1_macro": report["macro avg"]["f1-score"], "accuracy": report["accuracy"]}

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    metrics = trainer.evaluate()
    print(metrics)

    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Model saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
