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
    if not text or not text.strip():
        return []

    text = clean_text(text)

    # Remove Gmail artifacts
    text = re.sub(
        r"^(?:download|print)\s+(?=(?:dear|hi|hello)\b)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove greeting
    text = re.sub(
        r"^(?:dear|hi|hello)\s+[^,]+,\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Separate numbered instructions
    text = re.sub(
        r"\bstep\s*[-–]?\s*\d+\s*:",
        "\n",
        text,
        flags=re.IGNORECASE,
    )

    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)

    request_patterns = [
        r"^(?:please|kindly)\s+",
        r"^(?:could|can|would)\s+you\b",
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
        "click", "configure", "log in",
    )

    ignored_starts = (
        "the meeting is scheduled",
        "the interview is scheduled",
        "the meeting has been scheduled",
        "the interview has been scheduled",
        "greetings from",
        "i am writing to inform",
        "this is to inform",
        "for your information",
        "just wanted to inform",
    )

    explicit_actions = []
    other_actions = []

    # Match action verbs when they begin a clause
    action_pattern = (
        r"(?:please\s+)?(?:"
        + "|".join(
            re.escape(verb)
            for verb in sorted(action_verbs, key=len, reverse=True)
        )
        + r")\b"
    )

    for sentence in sentences:
        sentence = sentence.strip(" \t-•")

        if not sentence:
            continue

        lower = sentence.lower()

        # Ignore negative reply instructions
        if re.search(
            r"\b(?:do not|don't|never|not required to)\s+(?:reply|respond)\b",
            lower,
        ):
            continue

        # Ignore email signatures
        if re.match(
            r"^(?:warm regards|best regards|kind regards|regards|"
            r"sincerely|thanks and regards)\b",
            lower,
        ):
            continue

        if any(lower.startswith(start) for start in ignored_starts):
            continue

        # Split multiple actions joined by commas or "and"
        parts = re.split(
            r",\s*(?=(?:" + action_pattern + r"))"
            r"|\s+and\s+(?=(?:" + action_pattern + r"))",
            sentence,
            flags=re.IGNORECASE,
        )

        for item in parts:
            item = item.strip(" ,")
            item_lower = item.lower()

            if not item:
                continue

            is_explicit_request = any(
                re.search(pattern, item_lower)
                for pattern in request_patterns
            )

            is_imperative = any(
                re.match(
                    r"^(?:please\s+)?" + re.escape(verb) + r"\b",
                    item_lower,
                )
                for verb in action_verbs
            )

            if is_explicit_request or is_imperative:
                target = (
                    explicit_actions
                    if is_explicit_request
                    else other_actions
                )

                if item not in explicit_actions + other_actions:
                    target.append(item)

    return (explicit_actions + other_actions)[:5]


# --------------------------------------------------
# KEYWORD EXTRACTION
# --------------------------------------------------


def extract_keywords(text, max_keywords=8):
    text = clean_text(text)

    if not text:
        return []

    # Remove Gmail artifacts and greetings
    text = re.sub(
        r"^(?:download|print)\s+(?=(?:dear|hi|hello)\b)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(?:dear|hi|hello)\s+[^,]+,\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove signatures
    text = re.split(
        r"\b(?:warm regards|best regards|kind regards|"
        r"thanks and regards|sincerely)\b",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    # Remove common email boilerplate
    text = re.sub(
        r"\bgreetings from\s+[^.!?]+[.!?]?",
        "",
        text,
        flags=re.IGNORECASE,
    )

    if not text.strip():
        return []

    ignored = {
        "dear", "hello", "greetings", "regards",
        "warm regards", "best regards", "thank you",
        "please", "kindly", "team", "download",
        "click", "log", "log in", "configure",
        "working", "ready", "link", "provided",
        "ensure", "share", "review", "prepare",
        "complete", "send", "update", "check",
        "follow up", "let me know", "immediately",
        "today", "tomorrow","congratulations", "scheduled", "join",
        "investigate", "resolve", "issue and resolve",
        "meeting is scheduled", "scheduled for",
        "failed twice today", "failed transaction immediately",
    }

    try:
        extractor = yake.KeywordExtractor(
            lan="en",
            n=3,
            top=max_keywords * 4,
            dedupLim=0.7,
        )

        keywords = extractor.extract_keywords(text)

        results = []
        seen = set()

        for keyword, score in keywords:
            keyword = keyword.strip()
            normalized = keyword.lower()

            if (
                keyword
                and len(keyword) > 2
                and normalized not in ignored
                and normalized not in seen
            ):
                results.append(keyword)
                seen.add(normalized)

            if len(results) >= max_keywords:
                break

        return results

    except Exception:
        return []



# --------------------------------------------------
# ENTITY EXTRACTION
# --------------------------------------------------


def extract_entities(text):
    text = clean_text(text)

    if not text:
        return []

    # Remove Gmail artifacts and greeting
    text = re.sub(
        r"^(?:download|print)\s+(?=(?:dear|hi|hello)\b)",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"^(?:dear|hi|hello)\s+[^,]+,\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Remove signature before entity recognition
    text = re.split(
        r"\b(?:warm regards|best regards|kind regards|"
        r"thanks and regards|sincerely)\b",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]

    nlp = get_nlp()

    if nlp is None:
        return []

    try:
        doc = nlp(text[:10000])

        allowed = {
            "PERSON", "ORG", "GPE", "MONEY",
            "PRODUCT", "EVENT", "DATE", "TIME",
        }

        ignored = {
            "team", "dear", "hello", "hi",
            "warm regards", "best regards",
            "early careers team", "greetings",
        }

        entities = []
        seen = set()

        for entity in doc.ents:
            value = entity.text.strip()
            normalized = value.lower()

            if (
                value
                and len(value) > 2
                and entity.label_ in allowed
                and normalized not in ignored
                and normalized not in seen
            ):
                entities.append(value)
                seen.add(normalized)

        return entities[:10]

    except Exception:
        return []

