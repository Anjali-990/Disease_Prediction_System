import re
import string
#for wrong /misspelled words
import difflib
# Matching dataset's input features
# Matching dataset's input features (extended for common typos)
SYMPTOM_KEYWORDS = {
    "fever": ["fever", "high temperature", "hot body", "fevar", "fevarish", "fevrish"],
    "headache": ["headache", "migraine", "head pain", "hedache"],
    "nausea": ["nausea", "queasy", "sick to stomach"],
    "vomiting": ["vomiting", "throwing up", "threw up"],
    "fatigue": ["fatigue", "tired", "exhausted", "exausted", "weak"],
    "joint_pain": ["joint pain", "aching joints", "painful joints"],
    "skin_rash": ["rash", "skin rash", "itchy skin", "red spots"],
    "cough": ["cough", "coughing", "dry cough", "caugh", "coff"],
    "weight_loss": ["lost weight", "losing weight", "weight loss"],
    "yellow_eyes": ["yellow eyes", "jaundice", "yellowing eyes", "yellow skin", "jaundees"]
}


# Maintaining the same order model expects
SYMPTOM_ORDER = list(SYMPTOM_KEYWORDS.keys())

# Precompile regex patterns for all keywords for performance
COMPILED_KEYWORDS = {
    symptom: [re.compile(rf"\b{re.escape(keyword)}\b") for keyword in keywords]
    for symptom, keywords in SYMPTOM_KEYWORDS.items()
}

# Basic stopword list (expand as needed)
# Stopwords to ignore during fuzzy matching
STOPWORDS = {
    "the", "and", "or", "but", "of", "to", "a", "an", "is", "are", "was", "were",
    "in", "on", "at", "by", "for", "with", "amazing", "great", "today", "very", "really", "ready"
}

def fuzzy_match(words, keyword_phrase, threshold=0.75):
    """
    Check if any word in 'words' approximately matches any part of 'keyword_phrase'.
    """
    keyword_words = keyword_phrase.lower().split()
    for kw in keyword_words:
        for word in words:
            if word in STOPWORDS or len(word) < 4:
                continue
            if difflib.SequenceMatcher(None, word, kw).ratio() >= threshold:
                return True
    return False

def extract_symptoms_from_text(text: str):
    """
    Converts plain text symptom description into binary symptom vector.
    Output is a list like: [1, 0, 1, 0, ...] matching model input format.
    """
    # Normalize text: lowercase and remove punctuation
    text = text.lower()
    text_clean = text.translate(str.maketrans('', '', string.punctuation))
    words = text_clean.split()
   


    symptom_vector = []
    matched_symptoms = []
    fuzzy_threshold = 0.75  # adjust as needed
    for symptom in SYMPTOM_ORDER:
        matched = False
        # 1. Exact phrase match
        if any(pattern.search(text_clean) for pattern in COMPILED_KEYWORDS[symptom]):
            matched = True
        else:
            # 2. Fuzzy match
            for keyword in SYMPTOM_KEYWORDS[symptom]:
                for kw_word in keyword.split():
                    for word in words:
                        if (
                            word not in STOPWORDS and
                            len(word) >= 4
                        ):
                            score = difflib.SequenceMatcher(None, word, kw_word).ratio()
                            if score >= fuzzy_threshold:
                                matched = True
                                break
                    if matched:
                        break
                if matched:
                    break

        symptom_vector.append(1 if matched else 0)
        if matched:
            matched_symptoms.append(symptom.replace("_", " ").title())

    return symptom_vector, matched_symptoms