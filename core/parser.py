"""
Resume Parser — PDF Ingestion, Spatial Extraction & Section Segmentation
========================================================================
Owner: Member 1

Responsibilities:
  - PDF binary validation (MIME type, extension, file size)
  - Spatial layout-aware text extraction via pdfplumber
  - Scanned PDF detection and rejection
  - Multi-column text isolation
  - Section heading segmentation (Skills, Experience, Education, Projects)
  - Integration with sanitizer for PII redaction

Do NOT implement matching scores, skill normalization, or UI here.

Contract:
  Input:  file_bytes (bytes), filename (str)
  Output: ParsedResume (from api.models)
  Errors: ScannedPDFException, InvalidFileException, EmptyResumeException
"""

import hashlib
import re
import uuid
from typing import Dict

from api.models import (
    ParsedResume,
    ScannedPDFException,
    InvalidFileException,
    EmptyResumeException,
)
from core.sanitizer import sanitize_text

# ─── Configuration ──────────────────────────────────────────────────
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
MIN_CHAR_THRESHOLD = 50  # Below this → ScannedPDFException
ALLOWED_EXTENSIONS = {".pdf"}

# Section heading aliases for regex segmentation
SECTION_ALIASES = {
    "skills": ["skills", "technical skills", "competencies", "technologies", "tech stack"],
    "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
    "education": ["education", "academic background", "qualifications", "academic qualifications"],
    "projects": ["projects", "academic projects", "key initiatives", "personal projects"],
}


def validate_file(file_bytes: bytes, filename: str) -> None:
    """Validate file extension, size, and basic integrity.

    Args:
        file_bytes: Raw uploaded file content.
        filename: Original filename.

    Raises:
        InvalidFileException: If validation fails.
    """
    # TODO: Member 1 — implement MIME type check, extension check, size check
    if not filename.lower().endswith(".pdf"):
        raise InvalidFileException(
            message=f"Unsupported file type. Expected .pdf, got '{filename}'",
            filename=filename,
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise InvalidFileException(
            message=f"File exceeds maximum size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB",
            filename=filename,
        )
    if len(file_bytes) == 0:
        raise InvalidFileException(
            message="Uploaded file is empty",
            filename=filename,
        )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber with spatial layout awareness.

    Uses bounding box coordinate sorting (x0, top) to correctly handle
    multi-column layouts without horizontal line interleaving. Words are
    grouped into visual lines; when a page exhibits a clear vertical
    gutter (wide word-free band), lines are split at the gutter and the
    left column is read top-to-bottom before the right column, while
    full-width header lines (e.g. centered titles) are kept intact first.

    Args:
        file_bytes: Raw PDF content.

    Returns:
        Concatenated text from all pages in reading order.
    """
    import io

    import pdfplumber

    LINE_TOP_TOLERANCE = 3.0
    # Internal word gap above this marks a two-column split within a line
    # (normal inter-word spacing is only a few points).
    GUTTER_SPLIT_GAP = 50.0

    def _group_lines(words):
        words_sorted = sorted(words, key=lambda w: (w["top"], w["x0"]))
        lines: list = []
        for word in words_sorted:
            placed = False
            for line in lines:
                if abs(line[0]["top"] - word["top"]) <= LINE_TOP_TOLERANCE:
                    line.append(word)
                    placed = True
                    break
            if not placed:
                lines.append([word])
        return lines

    def _extract_page(page) -> str:
        words = page.extract_words() or []
        if not words:
            return ""
        lines = _group_lines(words)

        # Per-line gutter analysis: a line whose internal word gap is
        # abnormally wide contains text from two adjacent columns.
        split_positions = []
        line_parts = []  # (top, kind, left_words, right_words)
        for line in lines:
            ordered = sorted(line, key=lambda w: w["x0"])
            best_gap, best_idx = 0.0, -1
            for i in range(len(ordered) - 1):
                gap = ordered[i + 1]["x0"] - ordered[i]["x1"]
                if gap > best_gap:
                    best_gap, best_idx = gap, i
            if best_gap > GUTTER_SPLIT_GAP:
                split_x = (
                    ordered[best_idx]["x1"] + ordered[best_idx + 1]["x0"]
                ) / 2.0
                split_positions.append(split_x)
                line_parts.append(
                    (line[0]["top"], "split",
                     ordered[: best_idx + 1], ordered[best_idx + 1 :])
                )
            else:
                line_parts.append((line[0]["top"], "whole", ordered, []))

        if sum(1 for _, kind, _, _ in line_parts if kind == "split") < 2:
            # Single-column page: plain top-to-bottom reading order.
            return "\n".join(
                " ".join(w["text"] for w in sorted(line, key=lambda w: w["x0"]))
                for line in sorted(lines, key=lambda ln: ln[0]["top"])
            )

        gutter = sorted(split_positions)[len(split_positions) // 2]
        headers, left, right = [], [], []
        for top, kind, left_words, right_words in line_parts:
            if kind == "split":
                if left_words:
                    left.append((top, left_words))
                if right_words:
                    right.append((top, right_words))
                continue
            # Whole line: assign by horizontal center; centered lines
            # straddling the gutter are full-width headers.
            whole = left_words
            spans_gutter = any(w["x0"] < gutter < w["x1"] for w in whole) or (
                min(w["x0"] for w in whole) < gutter
                and max(w["x1"] for w in whole) > gutter
                and len(whole) <= 6
            )
            if spans_gutter:
                headers.append((top, whole))
            elif sum(w["x0"] + w["x1"] for w in whole) / (2 * len(whole)) < gutter:
                left.append((top, whole))
            else:
                right.append((top, whole))
        headers.sort(key=lambda t: t[0])
        left.sort(key=lambda t: t[0])
        right.sort(key=lambda t: t[0])
        ordered_parts = (
            [words for _, words in headers]
            + [words for _, words in left]
            + [words for _, words in right]
        )
        return "\n".join(" ".join(w["text"] for w in part) for part in ordered_parts)

    pages_text = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            pages_text.append(_extract_page(page))
    return "\n\n".join(t for t in pages_text if t)


def segment_sections(raw_text: str) -> Dict[str, str]:
    """Segment raw text into structured sections using heading detection.

    Identifies section boundaries using SECTION_ALIASES regex patterns.

    Args:
        raw_text: Full extracted resume text.

    Returns:
        Dictionary with keys: skills, experience, education, projects.
        Each value is the text content under that section heading.
    """
    sections: Dict[str, str] = {
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
    }
    if not raw_text or not raw_text.strip():
        return sections

    # Build heading patterns: each alias matches a whole line (case-insensitive),
    # optionally followed by ':' or trailing whitespace.
    key_by_alias: Dict[str, str] = {}
    for key, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            key_by_alias[alias.lower()] = key

    # Longest aliases first so "technical skills" wins over "skills".
    sorted_aliases = sorted(key_by_alias, key=len, reverse=True)
    heading_re = re.compile(
        r"^[\s#*\-\u2022]*(" + "|".join(re.escape(a) for a in sorted_aliases) + r")[\s:|\-]*$",
        re.IGNORECASE,
    )

    # Find heading line boundaries.
    boundaries: list = []  # (line_index, section_key)
    lines = raw_text.splitlines()
    for idx, line in enumerate(lines):
        match = heading_re.match(line.strip())
        if match:
            boundaries.append((idx, key_by_alias[match.group(1).lower()]))

    if not boundaries:
        # No headings detected: treat everything as experience content.
        sections["experience"] = raw_text.strip()
        return sections

    boundaries.sort(key=lambda b: b[0])
    for i, (line_idx, key) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(lines)
        chunk = "\n".join(lines[line_idx + 1 : end]).strip()
        if sections[key]:
            sections[key] = (sections[key] + "\n" + chunk).strip()
        else:
            sections[key] = chunk
    return sections


def extract_skills_from_block(skills_block: str) -> list:
    """Extract individual skill tokens from the skills section.

    Splits on common delimiters (commas, pipes, bullets, newlines)
    and normalizes to lowercase.

    Args:
        skills_block: Raw text from the skills section.

    Returns:
        List of lowercase skill strings.
    """
    # TODO: Member 1 — implement skill token extraction
    if not skills_block.strip():
        return []
    # Basic placeholder: split on common delimiters
    tokens = re.split(r"[,|•\n\r]+", skills_block)
    return [t.strip().lower() for t in tokens if t.strip()]


def generate_resume_id(filename: str, file_bytes: bytes) -> str:
    """Generate a deterministic unique ID for a resume.

    Uses SHA-256 hash of file content truncated to 12 hex chars,
    prefixed with 'res-'.

    Args:
        filename: Original filename.
        file_bytes: Raw file content.

    Returns:
        Deterministic resume ID string.
    """
    content_hash = hashlib.sha256(file_bytes).hexdigest()[:12]
    return f"res-{content_hash}"


def parse_resume(
    file_bytes: bytes,
    filename: str,
    redact_pii: bool = True,
) -> ParsedResume:
    """Main entry point: Parse a PDF resume into a structured ParsedResume.

    Pipeline:
      1. Validate file (extension, size, integrity)
      2. Extract text via pdfplumber (spatial layout-aware)
      3. Check for scanned PDF (char_count < 50)
      4. Segment into sections
      5. Extract skill tokens
      6. Sanitize text (PII redaction if enabled)
      7. Return structured ParsedResume

    Args:
        file_bytes: Raw uploaded PDF content.
        filename: Original filename from upload.
        redact_pii: Enable blind screening / PII redaction.

    Returns:
        ParsedResume: Validated, structured resume data.

    Raises:
        InvalidFileException: File validation failure.
        ScannedPDFException: PDF has no extractable text layer.
        EmptyResumeException: Parsing produced no content.
    """
    # Step 1: Validate
    validate_file(file_bytes, filename)

    # Step 2: Extract text
    raw_text = extract_text_from_pdf(file_bytes)

    # Step 3: Scanned PDF check
    char_count = len(re.sub(r"\s+", "", raw_text))
    if char_count < MIN_CHAR_THRESHOLD:
        raise ScannedPDFException(filename=filename)

    # Step 4: Segment sections
    sections = segment_sections(raw_text)

    # Step 5: Extract skill tokens
    skills = extract_skills_from_block(sections["skills"])

    # Step 6: Sanitize
    sanitized = sanitize_text(raw_text, enable_blind_screening=redact_pii)

    # Step 7: Build and return structured output
    return ParsedResume(
        resume_id=generate_resume_id(filename, file_bytes),
        filename=filename,
        raw_text=raw_text,
        sanitized_text=sanitized,
        skills_extracted=skills,
        skills_block=sections["skills"],
        experience_block=sections["experience"],
        education_block=sections["education"],
        projects_block=sections["projects"],
        is_blind_screened=redact_pii,
        char_count=char_count,
    )
