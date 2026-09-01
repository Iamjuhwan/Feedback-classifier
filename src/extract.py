"""
Step 3b: information extraction.

Lexicon + regex span extraction for symptom, facility, and location
mentions. Deliberately simple and fast (no model download needed) — this is
the "structured summary" a health-authority reviewer would want next to the
urgent_complaint / general_feedback / praise classification.

Upgrade path: once there's a labeled span dataset, swap this for a
fine-tuned token classifier (spaCy or a HF token-classification head) — the
function signature (`extract(text) -> dict`) stays the same, so nothing
downstream has to change.
"""

import re
from extraction_lexicon import SYMPTOMS, FACILITIES, LOCATIONS


def _find_matches(text: str, terms: list[str]) -> list[str]:
    text_lower = text.lower()
    found = []
    for term in terms:
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, text_lower):
            found.append(term)
    return found


def extract(text: str) -> dict:
    return {
        "symptoms": _find_matches(text, SYMPTOMS),
        "facilities": _find_matches(text, FACILITIES),
        "locations": _find_matches(text, LOCATIONS),
    }


if __name__ == "__main__":
    samples = [
        "Fever and vomiting for two days at the Lagos clinic, no doctor available",
        "The Abuja hospital pharmacy don run out of malaria drugs since last week",
        "Thank you to the health center in Kano for the fast vaccination service",
    ]
    for s in samples:
        print(s)
        print(extract(s))
        print()
