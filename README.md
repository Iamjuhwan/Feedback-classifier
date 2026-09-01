# Community Health Feedback Classifier

Text classification + information extraction over multilingual Nigerian
community/health feedback — built to demonstrate the skills:
text classification, information extraction, and multilingual NLP applied to
health and social-data contexts.

## What it does

1. **Classifies** short community/health-related text into: `urgent_complaint`,
   `general_feedback`, `praise`, or `not_relevant`.
2. **Extracts** structured info from the text — symptom, facility, and
   location mentions — so a health authority could triage feedback at a glance.
3. Ships a small FastAPI demo endpoint for both.

## Data

**Source:** [NaijaSenti](https://github.com/hausanlp/NaijaSenti) — a real,
human-annotated Twitter sentiment corpus covering Hausa, Igbo, Nigerian-Pidgin,
and Yoruba (Muhammad et al., LREC 2022). ~63,000 tweets total.

**Pipeline (`src/`):**

| Step | Script | What it does |
|---|---|---|
| 1 | `data_prep.py` | Filters the full corpus to a health-domain subset via a bootstrap keyword lexicon (`health_lexicon.py`), and applies a heuristic sentiment→category mapping as a starting guess. |
| 2 | `build_review_workbook.py` | Exports the candidates to `relabeling_review.xlsx` — a dropdown-validated spreadsheet for manual correction. |
| 3a | `train_baseline.py` | TF-IDF (char n-gram) + Logistic Regression classifier — fast, fully offline, sanity-checks the pipeline. |
| 3b | `train_transformer.py` | Fine-tunes `Davlan/afro-xlmr-base` on the same labels for a stronger model. **Run this on Colab/Kaggle** — needs Hugging Face Hub access. |
| 3c | `extract.py` / `extraction_lexicon.py` | Information extraction — symptom/facility/location mentions via keyword + regex, upgradeable to a fine-tuned token classifier later. |
| 4 | `api.py` | FastAPI endpoint serving classification + extraction together (`POST /analyze`). |

## Current results

- **2,674** health-domain candidate rows pulled from NaijaSenti's ~63K real
  tweets (4.4% Hausa, 3.0% Igbo, 6.3% Pidgin, 3.7% Yoruba).
- **810** manually relabeled and corrected (3 dropped as `not_relevant` —
  too few to train that class; fold in more later if it grows).
- **Baseline classifier** (TF-IDF char n-grams + Logistic Regression):
  **61.7% accuracy, 0.615 macro-F1** on a held-out 20% split (random
  baseline ≈ 33% across 3 classes). `models/baseline_tfidf_logreg.joblib`.
- **API smoke-tested end-to-end**: text in → classification + extracted
  symptom/facility/location spans out.

## Next steps (in priority order)

1. Label more rows (aim for 1,500+) to lift the baseline and give the
   transformer fine-tune enough signal — it needs more data than logistic
   regression does to beat it.
2. Run `train_transformer.py` on Colab/Kaggle for the stronger multilingual
   model; compare macro-F1 against the baseline before swapping it into `api.py`.
3. Deploy `api.py` to Render (same pattern as your other CV projects) for a
   live demo link.

## Known limitations (v1, being worked through)

- **Keyword filtering is noisy.** Short Hausa/Yoruba/Igbo health words can
  false-positive inside names or idioms (e.g. "Lafiya" as part of a name).
  The manual relabeling pass (`not_relevant` option) cleans this up.
- **Sentiment ≠ urgency.** The heuristic label (negative→urgent_complaint) is
  only a starting guess for the human reviewer, not a ground-truth label.
- **NaijaSenti is general-domain Twitter, not health-specific.** A
  purpose-built dataset — e.g. Ahmad et al. (2024), *"Analyzing COVID-19
  Vaccination Sentiments in Nigerian Cyberspace"* (arXiv:2401.13133) — would
  be a stronger v2 data source; it isn't publicly downloadable from this
  environment, so it's a follow-up: request access from the authors and
  swap it into `data_prep.py`.

## Setup

```bash
git clone https://github.com/hausanlp/NaijaSenti.git   # data dependency
cd community-health-nlp
pip install -r requirements.txt
python src/data_prep.py
python src/build_review_workbook.py
# manually label data/processed/relabeling_review.xlsx -> save as data/labeled/labeled_dataset.csv, then:
python src/train_baseline.py
# on Colab/Kaggle, for the stronger model:
python src/train_transformer.py
# serve the demo:
uvicorn src.api:app --reload
```
