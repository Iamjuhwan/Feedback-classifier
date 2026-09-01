"""
Bootstrap keyword lexicon used to pull a health-domain subset out of the
general-domain NaijaSenti corpus. This is a v1 heuristic filter, not a
gold-standard health taxonomy — see README 'Known limitations'.
"""

HEALTH_KEYWORDS = {
    # English / Nigerian-Pidgin (shared largely with English)
    "en_pcm": [
        "covid", "corona", "coronavirus", "vaccine", "vaccinate", "vaccination",
        "hospital", "clinic", "doctor", "nurse", "health", "healthcare",
        "sick", "sickness", "disease", "malaria", "cholera", "lassa", "fever",
        "medicine", "drug", "pharmacy", "symptom", "infection", "patient",
        "ambulance", "nphcda", "ncdc", "who", "treatment", "diagnosis",
        "surgery", "injection", "outbreak", "epidemic", "pandemic",
    ],
    # Hausa
    "hau": [
        "likita", "asibiti", "lafiya", "rashin lafiya", "alluran rigakafi",
        "rigakafi", "cutar", "ciwo", "magani", "kwayoyi", "zazzabi",
        "asibitin", "jinya", "mara lafiya",
    ],
    # Yoruba
    "yor": [
        "dokita", "ile iwosan", "iwosan", "ajesara", "aisan", "ilera",
        "oogun", "arun", "iba", "arannilokun", "ile-iwosan",
    ],
    # Igbo
    "ibo": [
        "dọkịta", "dokita", "ụlọ ọgwụ", "ulo ogwu", "ọgwụ mgbochi",
        "ọrịa", "oria", "ahụike", "ahuike", "ọgwụ", "ogwu", "ọrịa iba",
    ],
}

def keywords_for(lang: str):
    """Return the relevant keyword list for a language code (hau/ibo/pcm/yor)."""
    shared = HEALTH_KEYWORDS["en_pcm"]
    specific = HEALTH_KEYWORDS.get(lang, [])
    return shared + specific
