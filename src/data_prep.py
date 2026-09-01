"""
Step 1 of the pipeline.

Loads NaijaSenti (real, human-annotated Nigerian-language tweets), filters
down to a health-domain subset via keyword matching, and applies a heuristic
label mapping (sentiment -> community-feedback category) as a STARTING
POINT for manual relabeling.

Output: data/processed/health_feedback_candidates.csv
Columns: text, language, source_sentiment, suggested_label, final_label(blank)

The heuristic mapping (negative->urgent_complaint, neutral->general_feedback,
positive->praise) is a reasonable first pass but will misclassify plenty of
rows (e.g. a negative-sentiment tweet about a health topic that isn't
actually urgent). `final_label` is left blank for manual review — that's
the "manual relabeling" step from the project plan.
"""

import csv
import re
from pathlib import Path

from health_lexicon import keywords_for

REPO_ROOT = Path(__file__).resolve().parent.parent
NAIJA_DIR = REPO_ROOT / "NaijaSenti" / "data" / "annotated_tweets"
OUT_PATH = REPO_ROOT / "data" / "processed" / "health_feedback_candidates.csv"

LANGS = ["hau", "ibo", "pcm", "yor"]
SPLITS = ["train", "dev", "test"]

SENTIMENT_TO_SUGGESTED_LABEL = {
    "negative": "urgent_complaint",
    "neutral": "general_feedback",
    "positive": "praise",
}


def load_split(lang: str, split: str):
    path = NAIJA_DIR / lang / f"{split}.tsv"
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            text = row.get("tweet", "").strip()
            label = row.get("label", "").strip()
            if text and label in SENTIMENT_TO_SUGGESTED_LABEL:
                rows.append((text, label))
    return rows


def is_health_related(text: str, lang: str) -> bool:
    text_lower = text.lower()
    for kw in keywords_for(lang):
        if kw.lower() in text_lower:
            return True
    return False


def clean_text(text: str) -> str:
    # NaijaSenti tweets have @user placeholders already; just normalise whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main():
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_rows = []
    stats = {lang: {"total": 0, "health": 0} for lang in LANGS}

    for lang in LANGS:
        for split in SPLITS:
            for text, sentiment in load_split(lang, split):
                stats[lang]["total"] += 1
                if is_health_related(text, lang):
                    stats[lang]["health"] += 1
                    all_rows.append({
                        "text": clean_text(text),
                        "language": lang,
                        "source_sentiment": sentiment,
                        "suggested_label": SENTIMENT_TO_SUGGESTED_LABEL[sentiment],
                        "final_label": "",  # fill in during manual review
                    })

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["text", "language", "source_sentiment", "suggested_label", "final_label"]
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print("Health-domain candidate rows by language:")
    for lang in LANGS:
        t, h = stats[lang]["total"], stats[lang]["health"]
        pct = (h / t * 100) if t else 0
        print(f"  {lang}: {h} / {t} total ({pct:.1f}%)")
    print(f"\nTotal candidates: {len(all_rows)}")
    print(f"Written to: {OUT_PATH}")


if __name__ == "__main__":
    main()
