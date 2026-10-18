"""
Resume Sanitizer — PII Redaction & Adversarial Text Neutralization
==================================================================
Owner: Member 1

Responsibilities:
  - Regex-based email and phone number redaction
  - spaCy NER-based name (PERSON) and location (GPE) redaction
  - Adversarial / invisible text detection and neutralization
  - Token density anomaly flagging

Do NOT implement matching logic or UI components here.
"""

import re
from typing import Tuple

# ─── Redaction Markers ──────────────────────────────────────────────
REDACTED_NAME = "[REDACTED_NAME]"
REDACTED_LOCATION = "[REDACTED_LOCATION]"
REDACTED_CONTACT = "[REDACTED_CONTACT]"

# ─── Regex Patterns ─────────────────────────────────────────────────
EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,5}[-.\s]?\d{3,5}"
)

# Known adversarial prompt injection markers
ADVERSARIAL_MARKERS = [
    "ignore previous instructions",
    "ignore all instructions",
    "rank 100%",
    "score 100",
    "disregard above",
    "override scoring",
]


def redact_contact_info(text: str) -> str:
    """Replace email addresses and phone numbers with redaction markers.

    Args:
        text: Raw extracted text from a resume.

    Returns:
        Text with emails and phone numbers replaced by [REDACTED_CONTACT].
    """
    redacted = EMAIL_PATTERN.sub(REDACTED_CONTACT, text)

    # Phone candidates: digit runs with common separators; only redact when
    # the digit count looks like a real phone number (>= 10 digits) so that
    # year ranges like "2021-2024" (8 digits) are left untouched.
    phone_candidate = re.compile(r"\+?\(?\d[\d\-.\s()]{7,}\d")
    def _phone_repl(match: re.Match) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) >= 10:
            return REDACTED_CONTACT
        return match.group(0)

    return phone_candidate.sub(_phone_repl, redacted)


# Fallback location cues for residual "City, Region" mentions that small
# NER models miss in noisy header lines (e.g. "Hyderabad, India").
# These tokens carry no skill signal, so over-redaction here is harmless.
REGION_NAMES = (
    "India|USA|U\\.S\\.|United States|United Kingdom|UK|Canada|Australia"
    "|Singapore|Germany|UAE|Goa|Karnataka|Maharashtra|Tamil Nadu|Telangana"
    "|Delhi|West Bengal|Kerala|Gujarat|Rajasthan|Punjab|Haryana|Bihar"
)
CITY_REGION_RE = re.compile(
    r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}),\s*(?:" + REGION_NAMES + r")\b"
)
CITY_RE = re.compile(
    r"\b(Bengaluru|Bangalore|Hyderabad|Chennai|Mumbai|Pune|Delhi|Kolkata"
    r"|Ahmedabad|Jaipur|Lucknow|Kanpur|Nagpur|Indore|Bhopal|Patna|Kochi"
    r"|Coimbatore|Madurai|Surat|Vadodara|Ranchi|Bhubaneswar|Guwahati|Dehradun"
    r"|Chandigarh|Noida|Gurgaon|Gurugram|Faridabad|Ghaziabad|Panaji|Goa"
    r"|Mysuru|Mysore|Vijayawada|Visakhapatnam)\b"
)


# ─── Skill-aware NER guard + header-name rule ─────────────────────────
# First-line header that is clearly a candidate name (2-4 capitalized
# words, no digits) is redacted even when NER misses it in context.
NAME_HEADER_RE = re.compile(r"^[A-Z][a-z'.\-]+(?:\s+[A-Z][a-z'.\-]+){1,3}$")
NON_NAME_HEADERS = {"resume", "curriculum vitae", "cv", "profile", "bio data"}


def _skill_protected_intervals(text):
    """Character intervals occupied by known ESCO skill surface forms.

    Prevents NER from redacting skills it mistakes for entities
    (en_core_web_sm labels e.g. "Pandas" or "Docker" as PERSON).
    """
    try:
        from core.extractor import load_esco_taxonomy
    except ImportError:  # pragma: no cover - extractor unavailable
        return []
    taxonomy = load_esco_taxonomy()
    intervals = []
    for surface in taxonomy:
        if len(surface) < 2:
            continue
        pattern = re.compile(
            r"(?<![a-z0-9+#./])" + re.escape(surface) + r"(?![a-z0-9+#])",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            intervals.append((match.start(), match.end()))
    intervals.sort()
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _overlaps_protected(start, end, protected):
    return any(start < p_end and end > p_start for p_start, p_end in protected)


# ─── Lazy spaCy NER pipeline (loaded once; None if model unavailable) ─
_nlp = None
_nlp_load_attempted = False


def _get_nlp():
    """Load the spaCy NER model lazily, returning None if unavailable."""
    global _nlp, _nlp_load_attempted
    if not _nlp_load_attempted:
        _nlp_load_attempted = True
        try:
            import spacy
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Blank English pipeline as last resort (no NER).
                _nlp = None
        except ImportError:
            _nlp = None
    return _nlp


def redact_demographics(text: str) -> str:
    """Replace person names and locations using spaCy NER.

    Uses spaCy en_core_web_sm model to identify:
      - PERSON entities → replaced with [REDACTED_NAME]
      - GPE entities   → replaced with [REDACTED_LOCATION]

    Args:
        text: Text (preferably with contacts already redacted).

    Returns:
        Text with demographic identifiers redacted.
    """
    redacted = text
    # Header-name rule FIRST (on intact text): a leading name line (e.g.
    # "Vikram Nair") is PII even when NER misses it; skill terms are never
    # treated as names.
    lines = redacted.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        candidate = line.strip()
        base = len("\n".join(lines[:i])) + (1 if i else 0)
        if (
            NAME_HEADER_RE.match(candidate)
            and candidate.lower() not in NON_NAME_HEADERS
            and not _overlaps_protected(
                base, base + len(candidate),
                _skill_protected_intervals(redacted),
            )
        ):
            lines[i] = REDACTED_NAME
        break
    redacted = "\n".join(lines)

    protected = _skill_protected_intervals(redacted)
    nlp = _get_nlp()
    if nlp is not None:
        # Union of full-text spans and per-line spans: header names tag
        # correctly in isolation but can be missed amid contact-marker noise.
        spans = []
        for ent in nlp(redacted).ents:
            if ent.label_ in ("PERSON", "GPE") and not _overlaps_protected(
                ent.start_char, ent.end_char, protected
            ):
                spans.append((ent.start_char, ent.end_char, ent.label_))
        offset = 0
        for line in redacted.splitlines(keepends=True):
            stripped = line.strip()
            lead = line.index(stripped) if stripped else 0
            for ent in nlp(stripped).ents:
                if ent.label_ in ("PERSON", "GPE"):
                    start = offset + lead + ent.start_char
                    end = offset + lead + ent.end_char
                    if not _overlaps_protected(start, end, protected):
                        spans.append((start, end, ent.label_))
            offset += len(line)
        # Drop overlapping spans (keep the longest / first).
        spans.sort(key=lambda s: (s[0], -(s[1] - s[0])))
        filtered = []
        last_end = -1
        for start, end, label in spans:
            if start >= last_end:
                filtered.append((start, end, label))
                last_end = end
        for start, end, label in reversed(filtered):
            marker = REDACTED_NAME if label == "PERSON" else REDACTED_LOCATION
            redacted = redacted[:start] + marker + redacted[end:]
    # Pattern fallback for residual "City, Region" mentions and standalone
    # major-city tokens the small NER model misses (no skill signal lost:
    # none of these tokens appear in the ESCO taxonomy).
    redacted = CITY_REGION_RE.sub(REDACTED_LOCATION, redacted)
    redacted = CITY_RE.sub(REDACTED_LOCATION, redacted)
    return redacted


def sanitize_text(text: str, enable_blind_screening: bool = True) -> str:
    """Full sanitization pipeline: contacts → demographics → adversarial.

    Args:
        text: Raw extracted resume text.
        enable_blind_screening: If False, skip PII redaction.

    Returns:
        Sanitized text ready for embedding generation.
    """
    if not enable_blind_screening:
        return text

    sanitized = redact_contact_info(text)
    sanitized = redact_demographics(sanitized)
    sanitized = neutralize_adversarial_text(sanitized)
    return sanitized


def neutralize_adversarial_text(text: str) -> str:
    """Detect and flag adversarial prompt injection attempts.

    Scans for known injection patterns. Does NOT remove them (they are
    already plain text after invisible-text stripping), but flags them
    so downstream modules can log the attempt.

    Args:
        text: Extracted text.

    Returns:
        Text with adversarial markers flagged (prefixed with [ADV_FLAG]).
    """
    flagged = text
    for marker in ADVERSARIAL_MARKERS:
        pattern = re.compile(re.escape(marker), re.IGNORECASE)
        flagged = pattern.sub(lambda m: f"[ADV_FLAG] {m.group(0)}", flagged)
    return flagged


def detect_adversarial_markers(text: str) -> Tuple[bool, list]:
    """Check if text contains known adversarial injection patterns.

    Args:
        text: Text to scan.

    Returns:
        Tuple of (is_adversarial: bool, detected_markers: list[str]).
    """
    text_lower = text.lower()
    detected = [m for m in ADVERSARIAL_MARKERS if m in text_lower]
    return (len(detected) > 0, detected)
