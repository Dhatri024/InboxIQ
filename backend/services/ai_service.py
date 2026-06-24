from transformers import pipeline
from utils.helpers import detect_urgency, extract_action_items

# -----------------------------
# LOAD AI MODELS (LOAD ONCE)
# -----------------------------

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)

sentiment_analyzer = pipeline(
    "sentiment-analysis"
)

reply_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

# -----------------------------
# SMART REPLY
# -----------------------------

def generate_smart_reply(text, tone="formal"):

    prompt = f"""
    Write a {tone} professional email reply in 2-3 lines only.

    Email:
    {text}

    Reply:
    """

    result = reply_generator(
        prompt,
        max_new_tokens=120
    )

    return result[0]["generated_text"].strip()

# -----------------------------
# EMAIL CLASSIFICATION
# -----------------------------

def classify_email(text):

    labels = [
        "Work",
        "Meeting",
        "Finance",
        "Personal",
        "Spam",
        "Support"
    ]

    result = classifier(text[:1000], labels)

    return result["labels"][0]


# -----------------------------
# KEYWORDS (SAFE FALLBACK)
# -----------------------------

def extract_keywords(text):
    words = text.lower().split()

    stop_words = {
        "the", "is", "at", "on", "in", "and", "a", "to", "for",
        "we", "have", "will", "please", "regards", "hi", "hello",
        "you", "this", "that", "it", "be"
    }

    keywords = [
        w.strip(".,!?()[]{}")
        for w in words
        if w.isalpha() and w not in stop_words and len(w) > 2
    ]

    return list(set(keywords))[:10]


# -----------------------------
# ENTITIES (SAFE FALLBACK)
# -----------------------------

def extract_entities(text):

    entities = []
    words = text.split()

    for word in words:
        if word.istitle() and len(word) > 2:
            entities.append({
                "label": "PROPER_NOUN",
                "text": word
            })

    return entities[:10]


# -----------------------------
# EMAIL TYPE
# -----------------------------

def detect_email_type(text):

    text_lower = text.lower()

    patterns = {
        "Interview": ["interview", "schedule", "hr", "recruiter"],
        "Finance": ["invoice", "payment", "bill", "transaction"],
        "Work": ["project", "update", "task", "report"],
        "Meeting": ["meeting", "call", "zoom", "discussion"],
        "Urgent": ["urgent", "asap", "immediately"],
    }

    scores = {}

    for label, keywords in patterns.items():
        scores[label] = sum(1 for k in keywords if k in text_lower)

    return max(scores, key=scores.get)


# -----------------------------
# PRIORITY SCORE
# -----------------------------

def priority_score(text):
    score = 50
    text_lower = text.lower()

    if "urgent" in text_lower:
        score += 30
    if "asap" in text_lower:
        score += 20
    if "deadline" in text_lower:
        score += 25
    if "tomorrow" in text_lower:
        score += 15

    return min(score, 100)


# -----------------------------
# REMINDER SUGGESTION
# -----------------------------

def suggest_reminder(text):
    text = text.lower()

    if "meeting" in text:
        return "Schedule reminder 1 hour before meeting"
    if "deadline" in text:
        return "Set reminder 1 day before deadline"
    if "urgent" in text:
        return "Respond within 2 hours"
    return "No reminder needed"

def compute_email_score(text):

    text_lower = text.lower()
    score = 50

    # urgency signals
    if "urgent" in text_lower:
        score += 25
    if "asap" in text_lower:
        score += 20
    if "deadline" in text_lower:
        score += 20
    if "tomorrow" in text_lower:
        score += 10
    if "meeting" in text_lower:
        score += 10

    # negative signals
    if "fyi" in text_lower:
        score -= 10
    if "newsletter" in text_lower:
        score -= 20
    if "promotion" in text_lower:
        score -= 20

    return max(0, min(100, score))

def suggest_action(score):

    if score >= 80:
        return "Reply Immediately"
    elif score >= 60:
        return "Reply Today"
    elif score >= 40:
        return "Review Later"
    else:
        return "Ignore"

def generate_reason(text, urgency, category, priority_score):
    reasons = []

    text_lower = text.lower()

    if "urgent" in text_lower or "asap" in text_lower:
        reasons.append("Contains urgent keywords")

    if "deadline" in text_lower or "tomorrow" in text_lower:
        reasons.append("Has deadline reference")

    if "meeting" in text_lower:
        reasons.append("Mentions meeting")

    if priority_score > 80:
        reasons.append("High priority score detected")

    if category == "Work":
        reasons.append("Work-related email")

    if urgency == "High":
        reasons.append("High urgency detected")

    return " + ".join(reasons) if reasons else "Normal email pattern"

def calculate_confidence(urgency, category, priority_score):
    score = 0.5

    if urgency == "High":
        score += 0.2
    if category in ["Work", "Finance", "Interview"]:
        score += 0.2
    if priority_score > 70:
        score += 0.1

    return round(min(score, 0.99), 2)

def email_intelligence_score(urgency, priority, sentiment):
    score = 50

    if urgency == "High":
        score += 25
    if priority > 80:
        score += 20
    if sentiment == "NEGATIVE":
        score += 5

    return min(score, 100)

# -----------------------------
# MAIN AI ANALYSIS
# -----------------------------

def analyze_email_ai(text, tone="formal"):

    # -----------------------------
    # CORE ANALYSIS
    # -----------------------------
    summary_result = summarizer(
        text,
        max_length=80,
        min_length=20,
        do_sample=False,
        truncation=True
    )

    summary = summary_result[0]["summary_text"]

    sentiment_result = sentiment_analyzer(text[:512])
    sentiment = sentiment_result[0]["label"]

    # MUST COME FIRST (IMPORTANT FIX)
    urgency = detect_urgency(text)

    # ACTION ITEMS
    action_items = extract_action_items(text)

    # CATEGORY + TYPE
    category = classify_email(text)
    email_type = detect_email_type(text)

    # PRIORITY SCORE
    priority = priority_score(text)

    # INTELLIGENCE LOGIC
    intelligence_score = min(
        100,
        priority + (10 if urgency == "High" else 0)
    )

    # SMART REPLY
    smart_reply = generate_smart_reply(text, tone)

    # KEYWORDS + ENTITIES
    keywords = extract_keywords(text)
    entities = extract_entities(text)

    # REMINDER
    reminder = suggest_reminder(text)

    return {
        "summary": summary,
        "sentiment": sentiment,
        "urgency": urgency,
        "priority_score": priority,
        "intelligence_score": intelligence_score,
        "category": category,
        "email_type": email_type,
        "action_items": action_items,
        "keywords": keywords,
        "entities": entities,
        "reminder": reminder,
        "smart_reply": smart_reply
    }