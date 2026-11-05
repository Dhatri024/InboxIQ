import re
from collections import Counter

from utils.helpers import (
    detect_urgency,
    extract_action_items,
    extract_keywords,
    extract_entities,
    clean_text,
)


# --------------------------------------------------
# TEXT UTILITIES
# --------------------------------------------------

def _sentences(text):
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+|\n+", clean_text(text))
        if s.strip()
    ]


def _contains(text, phrases):
    return any(phrase in text for phrase in phrases)


# --------------------------------------------------
# SUMMARY GENERATION
# --------------------------------------------------


def generate_summary(text):
    sentences = _sentences(text)

    if not sentences:
        return "No email content provided."

    # Remove common email greetings.
    cleaned = []
    for sentence in sentences:
        sentence = re.sub(
            r"^(?:dear|hello|hi)\s+[^,]+,?\s*",
            "",
            sentence,
            flags=re.IGNORECASE,
        ).strip()
        if sentence:
            cleaned.append(sentence)

    if not cleaned:
        return "No meaningful email content found."

    lower = " ".join(cleaned).lower()

    if _contains(lower, ["payment failed", "payment failure",
                         "transactions have failed", "payment processing is not working"]):
        return (
            "The sender reports a payment processing issue or failed transactions "
            "and requests an investigation and an update on its resolution."
        )

    if "interview" in lower and _contains(
        lower, ["invite", "invitation", "invited", "pleased to invite"]
    ):
        return (
            "The sender invites the recipient to a technical interview "
            "and requests confirmation of availability."
        )

    if "meeting" in lower and _contains(
        lower, ["scheduled", "share the meeting notes", "minutes of meeting"]
    ):
        if "share" in lower or "forward" in lower:
            return (
                "The sender provides meeting scheduling information "
                "and requests that the meeting notes be shared."
            )
        return "The sender provides information about a scheduled meeting."

    if len(cleaned) <= 2:
        return " ".join(cleaned)[:500]

    important_terms = (
        "request", "please", "deadline", "due", "failed", "issue",
        "submit", "complete", "review", "confirm", "meeting",
        "interview", "payment", "project", "report", "schedule",
        "update", "tomorrow",
    )

    scored = []
    for index, sentence in enumerate(cleaned):
        lower_sentence = sentence.lower()
        score = sum(term in lower_sentence for term in important_terms)
        scored.append((score, -index, sentence))

    selected = sorted(scored, reverse=True)[:3]
    selected = sorted(selected, key=lambda item: -item[1])

    return " ".join(item[2] for item in selected)[:500]

def analyze_sentiment(text):
    lower = clean_text(text).lower()

    negative_words = {
        "problem", "issue", "failed", "failure", "error",
        "unfortunately", "delay", "cancel", "angry", "bad",
        "disappointed", "frustrated", "concern", "complaint",
        "broken", "unresolved", "not working", "not fixed",
        "not resolved", "unable", "rejected", "incorrect",
    }

    positive_words = {
        "great", "excellent", "success", "appreciate",
        "happy", "good", "resolved", "pleased", "wonderful",
        "congratulations", "thank you for your help",
    }

    negative_count = sum(
        1 for word in negative_words
        if re.search(r"\b" + re.escape(word) + r"\b", lower)
    )

    positive_count = sum(
        1 for word in positive_words
        if word in lower
    )

    if negative_count > positive_count:
        return "NEGATIVE"

    if positive_count > negative_count:
        return "POSITIVE"

    return "NEUTRAL"


# --------------------------------------------------
# EMAIL CLASSIFICATION
# --------------------------------------------------

def classify_email(text):
    lower = clean_text(text).lower()

    patterns = {
        "Finance": [
            "payment", "invoice", "transaction", "refund",
            "billing", "salary", "bank", "expense",
        ],
        "Support": [
            "not working", "technical issue", "bug",
            "error", "troubleshoot", "help", "failed",
            "failure", "unable to access",
        ],
        "Meeting": [
            "meeting", "minutes of meeting", "calendar invite",
            "zoom call", "teams call",
        ],
        "Work": [
            "project", "task", "report", "assignment",
            "submission", "deliverable", "work update",
        ],
        "Personal": [
            "birthday", "family", "vacation", "personal",
            "congratulations",
        ],
        "Spam": [
            "claim your prize", "winner", "limited time offer",
            "click here to win", "free gift",
        ],
    }

    scores = {
        category: sum(
            1 for phrase in keywords if phrase in lower
        )
        for category, keywords in patterns.items()
    }

    # Select the category with the strongest keyword match.
    category_priority = ("Spam", "Finance", "Support", "Work", "Meeting", "Personal")
    matched = [category for category in category_priority if scores[category] > 0]

    if not matched:
        return "Work"

    return max(matched, key=lambda category: scores[category])


# --------------------------------------------------
# EMAIL TYPE DETECTION
# --------------------------------------------------


def detect_email_type(text):
    lower = clean_text(text).lower()

    patterns = [
        ("Interview", ["interview", "recruiter", "job application", "hiring"]),
        ("Payment Issue", ["payment failed", "payment failure", "transaction failed"]),
        ("Meeting", [
            "meeting invitation", "calendar invite", "meeting scheduled",
            "meeting is scheduled", "minutes of meeting", "meeting notes",
        ]),
        ("Deadline", ["deadline", "due date", "submit by", "submit it by tomorrow", "submit by tomorrow", "due tomorrow"]),
        ("Support Request", ["not working", "technical issue", "help needed", "unable to access"]),
        ("Project Update", ["project update", "status report", "progress report"]),
        ("Document Request", ["share the document", "send the report", "attach the file"]),
    ]

    for label, keywords in patterns:
        if any(keyword in lower for keyword in keywords):
            return label

    return "General"

def priority_score(text):
    lower = clean_text(text).lower()
    urgency = detect_urgency(text)

    score = 40

    if urgency == "High":
        score += 35
    elif urgency == "Medium":
        score += 20

    if _contains(lower, [
        "payment failed", "payment failure", "system down",
        "security breach", "data loss", "service unavailable",
    ]):
        score += 15

    if _contains(lower, [
        "please investigate", "please resolve",
        "please fix", "action required",
    ]):
        score += 10

    if _contains(lower, [
        "newsletter", "promotion", "unsubscribe",
        "marketing email",
    ]):
        score -= 20

    return max(0, min(100, score))


def compute_email_score(text):
    return priority_score(text)


def suggest_action(score):
    if score >= 80:
        return "Reply Immediately"
    if score >= 60:
        return "Reply Today"
    if score >= 40:
        return "Review Later"
    return "Ignore"


# --------------------------------------------------
# INTELLIGENCE SCORE
# --------------------------------------------------

def email_intelligence_score(urgency, priority, sentiment):
    score = 40 + (priority * 0.45)

    if urgency == "High":
        score += 10
    elif urgency == "Medium":
        score += 5

    if sentiment == "NEGATIVE":
        score += 5

    return max(0, min(100, round(score)))


def generate_reason(text, urgency, category, priority_score):
    reasons = []
    lower = clean_text(text).lower()

    if urgency == "High":
        reasons.append("Contains high-urgency signals")
    elif urgency == "Medium":
        reasons.append("Contains a deadline or important signal")

    if category == "Finance":
        reasons.append("Finance-related email")
    elif category == "Support":
        reasons.append("Technical support issue")
    elif category == "Work":
        reasons.append("Work-related email")

    if priority_score >= 80:
        reasons.append("High priority score")

    if not reasons:
        reasons.append("No significant urgency signals")

    return " + ".join(reasons)


def calculate_confidence(urgency, category, priority_score):
    score = 0.60

    if urgency in ("High", "Medium"):
        score += 0.10

    if category in ("Work", "Finance", "Meeting", "Support"):
        score += 0.10

    if priority_score >= 70:
        score += 0.10

    return round(min(score, 0.95), 2)


# --------------------------------------------------
# REMINDER SUGGESTIONS
# --------------------------------------------------


def suggest_reminder(text):
    lower = clean_text(text).lower()

    deadline_patterns = [
        r"\bdue today\b",
        r"\bdue tomorrow\b",
        r"\bdeadline\b",
        r"\bsubmit by\b",
        r"\bcomplete by\b",
        r"\bby tomorrow\b",
        r"\bby \d{1,2}(?:st|nd|rd|th)?\b",
    ]

    meeting_patterns = [
        r"\bschedule (?:a )?meeting\b",
        r"\bmeeting\s+(?:is\s+)?scheduled\b",
        r"\bcalendar invite\b",
        r"\battend (?:the )?meeting\b",
        r"\bjoin (?:the )?(?:meeting|call)\b",
        r"\bzoom (?:meeting|call)\b",
        r"\bteams (?:meeting|call)\b",
    ]

    if any(re.search(pattern, lower) for pattern in deadline_patterns):
        return "Set reminder for the stated deadline"

    if any(re.search(pattern, lower) for pattern in meeting_patterns):
        return "Schedule reminder before the meeting"

    if _contains(lower, ["urgent", "asap", "immediately"]):
        return "Respond as soon as possible"

    return "No reminder needed"


def generate_smart_reply(text, tone="formal"):
    lower = clean_text(text).lower()
    tone = (tone or "formal").lower()

    formal = tone not in ("friendly", "casual", "informal")
    greeting = "Dear Sender," if formal else "Hello,"

    if "interview" in lower and _contains(
        lower, ["invite", "invitation", "invited", "pleased to invite"]
    ):
        body = (
            "Thank you for the interview invitation. "
            "I will review the details and confirm my availability shortly."
        )

    elif _contains(lower, ["meeting notes", "minutes of meeting", "mom attached"]):
        body = (
            "Thank you for sharing the meeting information. "
            "I will review the notes and follow up if anything needs clarification."
        )

    elif _contains(lower, [
        "payment failed", "payment failure",
        "transactions have failed", "payment processing issue",
    ]):
        body = (
            "Thank you for bringing this issue to our attention. "
            "We will review the reported payment problem and "
            "share an update once more information is available."
        )

    elif _contains(lower, [
        "share the document", "send the report",
        "attach the file", "provide the document",
    ]):
        body = (
            "Thank you for your request. "
            "I will review the document requirements and follow up accordingly."
        )

    elif _contains(lower, ["deadline", "due tomorrow", "submit by", "project report"]):
        body = (
            "Thank you for the update. "
            "I have noted the requested timeline and will review the next steps."
        )

    elif _contains(lower, ["thank you", "thanks for your help", "appreciate your support"]):
        body = (
            "You're welcome. "
            "Please feel free to reach out if you need anything else."
        )

    else:
        body = (
            "Thank you for your email. "
            "I will review the information and get back to you with an update."
        )

    if tone in ("casual", "informal"):
        greeting = "Hi,"
        body = body.replace("Thank you", "Thanks")
    elif tone == "friendly":
        greeting = "Hello,"

    return f"{greeting}\n\n{body}\n\nBest regards,"

def analyze_email_ai(text, tone="formal"):
    text = clean_text(text)

    if not text:
        raise ValueError("Email text cannot be empty.")

    summary = generate_summary(text)
    sentiment = analyze_sentiment(text)
    urgency = detect_urgency(text)
    action_items = extract_action_items(text)

    category = classify_email(text)
    email_type = detect_email_type(text)

    priority = priority_score(text)

    intelligence_score = email_intelligence_score(
        urgency,
        priority,
        sentiment,
    )

    smart_reply = generate_smart_reply(text, tone)

    keywords = extract_keywords(text)
    entities = extract_entities(text)

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
        "smart_reply": smart_reply,
    }
