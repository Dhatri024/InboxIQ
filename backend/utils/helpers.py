import re
import yake
import spacy

# -----------------------------
# SAFE SPACY LOAD (IMPORTANT)
# -----------------------------
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    print("⚠️ spaCy model not found. Run: python -m spacy download en_core_web_sm")


# -----------------------------
# URGENCY DETECTION
# -----------------------------
def detect_urgency(text):

    if not text:
        return "Low"

    urgent_keywords = [
        "urgent",
        "immediately",
        "asap",
        "deadline",
        "important",
        "priority",
        "critical",
        "tomorrow"
    ]

    text_lower = text.lower()

    matches = sum(
        keyword in text_lower
        for keyword in urgent_keywords
    )

    if matches >= 3:
        return "High"
    elif matches >= 1:
        return "Medium"
    else:
        return "Low"


# -----------------------------
# ACTION ITEM EXTRACTION
# -----------------------------
def extract_action_items(text):

    sentences = re.split(r'(?<=[.!?]) +', text)

    action_keywords = [
        "submit", "complete", "review", "send",
        "update", "schedule", "finish", "prepare",
        "call", "report", "share", "reply"
    ]

    action_items = []

    for sentence in sentences:
        lower = sentence.lower()

        if any(word in lower for word in action_keywords):
            if len(sentence.split()) < 40:   # IMPORTANT FILTER
                action_items.append(sentence.strip())

    return action_items[:5]

# -----------------------------
# KEYWORD EXTRACTION (IMPROVED)
# -----------------------------
def extract_keywords(text):

    if not text:
        return []

    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=2,
        top=5
    )

    keywords = kw_extractor.extract_keywords(text)

    final_keywords = []

    for keyword, score in keywords:
        cleaned = keyword.strip()

        if cleaned and cleaned not in final_keywords:
            final_keywords.append(cleaned)

    return final_keywords


# -----------------------------
# ENTITY EXTRACTION (SAFE VERSION)
# -----------------------------
def extract_entities(text):

    doc = nlp(text)

    allowed = {"PERSON", "ORG", "GPE", "DATE", "TIME", "MONEY"}

    entities = []

    for ent in doc.ents:
        clean_text = ent.text.strip()

        # FILTER junk + short words
        if (
            ent.label_ in allowed and
            len(clean_text) > 2 and
            clean_text.lower() not in ["please", "hi", "hey", "team"]
        ):
            entities.append({
                "label": ent.label_,
                "text": clean_text
            })

    return entities[:10]

def extract_keywords(text):
    import yake

    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=2,
        top=5
    )

    keywords = kw_extractor.extract_keywords(text)

    return [kw[0] for kw in keywords]

def safe_entities(entities):
    if not entities:
        return []
    return [
        {
            "text": e.get("text", ""),
            "label": e.get("label", "")
        }
        for e in entities
    ]