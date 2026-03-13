from myapp.symptom_extractor import extract_symptoms_from_text, SYMPTOM_ORDER

examples = [
    "Feeling fevarish and exausted lately",
    "Having jaundees and yellow skin",
    "Experiencing dry caugh with pain in joints",
    "I have a migraine and feel weak",
    "I am just feeling happy and amazing"
]

for text in examples:
    vector = extract_symptoms_from_text(text)
    matched = [symptom for symptom, val in zip(SYMPTOM_ORDER, vector) if val == 1]
    print(f"Text: {text}")
    if matched:
        print("Matched Symptoms:", ", ".join(matched))
    else:
        print("No symptoms matched.")
