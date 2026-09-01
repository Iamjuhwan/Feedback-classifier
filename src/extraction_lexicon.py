"""
Bootstrap lexicons for information extraction: symptom, facility, and
location mentions. Same v1-heuristic caveat as health_lexicon.py — this is
a keyword/regex pass, meant to be upgraded to a fine-tuned token classifier
once enough labeled spans exist (see README).
"""

SYMPTOMS = [
    "fever", "zazzabi", "iba",
    "cough", "tari",
    "headache", "ciwon kai", "efori",
    "vomiting", "amai", "eebi",
    "diarrhea", "diarrhoea", "gudawa", "igbe",
    "rash", "sore throat", "chills", "fatigue", "weakness",
    "malaria", "cholera", "lassa", "measles",
    "bleeding", "swelling", "pain", "ciwo", "irora", "mgbu",
]

FACILITIES = [
    "hospital", "asibiti", "ile iwosan", "ụlọ ọgwụ", "ulo ogwu",
    "clinic", "health center", "health centre", "phc",
    "pharmacy", "chemist",
    "ambulance", "primary health care",
]

# Nigerian states + a few major cities — not exhaustive, extend as needed
LOCATIONS = [
    "lagos", "abuja", "kano", "kaduna", "ibadan", "port harcourt", "enugu",
    "benin city", "jos", "ilorin", "abeokuta", "onitsha", "warri", "sokoto",
    "maiduguri", "zaria", "aba", "owerri", "uyo", "calabar", "katsina",
    "abia", "adamawa", "akwa ibom", "anambra", "bauchi", "bayelsa", "benue",
    "borno", "cross river", "delta", "ebonyi", "edo", "ekiti", "fct",
    "gombe", "imo", "jigawa", "kebbi", "kogi", "kwara", "nasarawa", "niger",
    "ogun", "ondo", "osun", "oyo", "plateau", "rivers", "sokoto", "taraba",
    "yobe", "zamfara",
]
