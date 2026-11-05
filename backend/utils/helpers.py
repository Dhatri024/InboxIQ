import re
import yake
import spacy

# --------------------------------------------------
# SAFE SPACY LOADING
# --------------------------------------------------

_nlp = None
_nlp_loaded = False


def get_nlp():
    global _nlp, _nlp_loaded

    if not _nlp_loaded:
        _nlp_loaded = True
        try:
            _nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError):
            _nlp = None

    return _nlp


# --------------------------------------------------
# TEXT UTILITIES
# --------------------------------------------------

def clean_text(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


# --------------------------------------------------
# URGENCY DETECTION
# --------------------------------------------------

def detect_urgency(text):
    text_lower = clean_text(text).lower()

    if not text_lower:
        return "Low"

    high_patterns = [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\basap\b",
        r"\bemergency\b",
        r"\bcritical\b",
        r"\bright away\b",
        r"\bas soon as possible\b",
        r"\bwithout delay\b",
        r"\baction required immediately\b",
    ]

    medium_patterns = [
        r"\bimportant\b",
        r"\bpriority\b",
        r"\bdeadline\b",
        r"\bdue today\b",
        r"\bdue tomorrow\b",
        r"\bby today\b",
        r"\bby tomorrow\b",
        r"\bwithin \d+ hours?\b",
        r"\bpending approval\b",
        r"\bfollow up required\b",
        r"\bunresolved\b",
        r"\bstill not working\b",
        r"\bnot fixed\b",
        r"\bnot resolved\b",
    ]

    if any(re.search(pattern, text_lower) for pattern in high_patterns):
        return "High"

    if any(re.search(pattern, text_lower) for pattern in medium_patterns):
        return "Medium"

    return "Low"


# --------------------------------------------------
# ACTION ITEM EXTRACTION
# --------------------------------------------------

def extract_action_items(text):
    text = clean_text(text)

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)

    request_patterns = [
        r"^(?:please|kindly)\s+",
        r"^(?:could|can|would)\s+you\b",
        r"^(?:could|can|would)\s+you\s+please\b",
        r"\bi\s+need\s+you\s+to\b",
        r"^don't forget to\b",
        r"^remember to\b",
    ]

    action_verbs = (
        "submit", "complete", "review", "send", "update",
        "schedule", "finish", "prepare", "call", "contact",
        "share", "reply", "confirm", "respond", "attend",
        "provide", "approve", "check", "verify", "investigate",
        "report", "follow up", "let me know", "fix",
        "resolve", "upload", "download", "sign", "arrange",
        "discuss", "deliver", "coordinate", "ensure",
        "process", "forward", "return", "clarify",
    )

    ignored_starts = (
        "the meeting is scheduled",
        "the interview is scheduled",
        "the meeting has been scheduled",
        "the interview has been scheduled",
        "i am writing to inform",
        "this is to inform",
        "for your information",
        "just wanted to inform",
    )

    results = []

    for sentence in sentences:
        sentence = sentence.strip(" \t-•")
        if not sentence:
            continue

        sentence = re.sub(
            r"^(?:hi|hello|dear)\s+[^,:\n]+[,:\s]+",
            "",
            sentence,
            flags=re.IGNORECASE,
        ).strip()

        if not sentence:
            continue

        lower = sentence.lower()

        if any(lower.startswith(start) for start in ignored_starts):
            continue

        is_explicit_request = any(
            re.search(pattern, lower)
            for pattern in request_patterns
        )

        is_imperative = any(
            re.match(r"^(?:please\s+)?"+re.escape(verb)+r"\b", lower)
            for verb in action_verbs
        )

        if is_explicit_request or is_imperative:
            if sentence not in results:
                results.append(sentence)

    return results[:5]


# --------------------------------------------------
# KEYWORD EXTRACTION
# --------------------------------------------------

def extract_keywords(text, max_keywords=8):
    text = clean_text(text)
    text = re.sub(r"^(?:dear|hi|hello)\s+[^,\n]+[, :]\s*", "", text, flags=re.IGNORECASE)

    if not text:
        return []

    try:
        extractor = yake.KeywordExtractor(
            lan="en",
            n=2,
            top=max_keywords,
            dedupLim=0.7,
        )

        keywords = extractor.extract_keywords(text)

        return [
            keyword.strip()
            for keyword, score in keywords
            if keyword.strip()
        ][:max_keywords]

    except Exception:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        stop_words = {
            "this", "that", "with", "from", "have",
            "your", "will", "would", "could", "please",
            "about", "there", "their", "which", "when",
        }

        return list(dict.fromkeys(
            word for word in words if word not in stop_words
        ))[:max_keywords]


# --------------------------------------------------
# ENTITY EXTRACTION
# --------------------------------------------------

def extract_entities(text):
    text = clean_text(text)
    text = re.sub(r"^(?:dear|hi|hello)\s+[^,\n]+[, :]\s*", "", text, flags=re.IGNORECASE)

    if not text:
        return []

    nlp = get_nlp()

    if nlp is None:
        return []

    try:
        doc = nlp(text[:10000])

        entities = []

        for entity in doc.ents:
            value = entity.text.strip()
            if value.lower() in {"team", "dear", "hello", "hi"}:
                continue

            if (
                value
                and entity.label_ in {
                    "PERSON", "ORG", "GPE", "MONEY", "PRODUCT", "EVENT",
                }
                and value not in entities
            ):
                entities.append(value)

        return entities[:15]

    except Exception:
        return []
