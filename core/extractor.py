"""
Skill Extractor & Job Description Parser
=========================================
Owner: Member 2

Responsibilities:
  - Parse raw job description text into core vs. context skills
  - Load and query the ESCO taxonomy for skill normalization
  - Fuzzy string matching for synonym resolution

Do NOT parse PDF files or render UI components here.

Contract:
  Input:  raw JD text (str)
  Output: JobProfile (from api.models)
"""

import csv
import os
import re
from typing import Dict, List, Optional, Set, Tuple

from api.models import JobProfile

# ─── ESCO Taxonomy Path ─────────────────────────────────────────────
ESCO_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "esco_skills.csv",
)

# Cached taxonomy (loaded once)
_taxonomy_cache: Optional[Dict[str, str]] = None


def load_esco_taxonomy(csv_path: str = ESCO_CSV_PATH) -> Dict[str, str]:
    """Load the ESCO skills taxonomy from CSV.

    Builds a lookup dictionary mapping each synonym (lowercased) to its
    canonical skill name.

    Args:
        csv_path: Path to esco_skills.csv.

    Returns:
        Dict mapping synonym → canonical skill name.
        Example: {"postgresql": "SQL", "react.js": "React"}
    """
    global _taxonomy_cache
    if _taxonomy_cache is not None:
        return _taxonomy_cache

    taxonomy: Dict[str, str] = {}
    if not os.path.exists(csv_path):
        _taxonomy_cache = taxonomy
        return taxonomy

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            canonical = row["canonical_skill"].strip()
            # Map canonical name to itself
            taxonomy[canonical.lower()] = canonical
            # Map each synonym to canonical
            synonyms_str = row.get("synonyms", "")
            if synonyms_str:
                for syn in synonyms_str.split(","):
                    syn_clean = syn.strip().lower()
                    if syn_clean:
                        taxonomy[syn_clean] = canonical

    _taxonomy_cache = taxonomy
    return taxonomy


def normalize_skill(skill: str, taxonomy: Optional[Dict[str, str]] = None) -> str:
    """Normalize a skill string to its ESCO canonical form.

    Falls back to the original (lowercased, stripped) if no match found.

    Args:
        skill: Raw skill string.
        taxonomy: Pre-loaded taxonomy dict. Loaded automatically if None.

    Returns:
        Canonical skill name or cleaned original.
    """
    if taxonomy is None:
        taxonomy = load_esco_taxonomy()

    skill_lower = skill.strip().lower()
    return taxonomy.get(skill_lower, skill.strip())


def normalize_skills_list(skills: List[str]) -> List[str]:
    """Normalize a list of skills, deduplicating by canonical form.

    Args:
        skills: List of raw skill strings.

    Returns:
        Deduplicated list of canonical skill names.
    """
    taxonomy = load_esco_taxonomy()
    seen: Set[str] = set()
    normalized: List[str] = []
    for s in skills:
        canonical = normalize_skill(s, taxonomy)
        canonical_lower = canonical.lower()
        if canonical_lower not in seen:
            seen.add(canonical_lower)
            normalized.append(canonical)
    return normalized


CORE_SECTION_MARKERS = (
    "must have", "required", "requirement", "requirements",
    "minimum qualification", "minimum qualifications",
    "what you'll do", "what you will do",
    "responsibilities", "core", "mandatory",
)
CONTEXT_SECTION_MARKERS = (
    "preferred", "good to have", "nice to have", "bonus", "plus",
    "desired", "optional",
)


def _split_jd_segments(jd_text: str) -> Tuple[str, str]:
    """Split JD text into (core_segment, context_segment) by headings.

    Lines (or inline phrases) containing preferred-type markers start the
    context segment; required-type markers (re)start the core segment. Text
    before any marker defaults to the core segment. Marker phrases are
    dropped but surrounding content is kept, so both bulleted JDs and
    single-line JDs like "Required: Python. Preferred: AWS" classify
    correctly.
    """
    markers = sorted(
        [(m, "context") for m in CONTEXT_SECTION_MARKERS]
        + [(m, "core") for m in CORE_SECTION_MARKERS],
        key=lambda t: len(t[0]),
        reverse=True,
    )
    alternation = "|".join(
        (r"\b" + re.escape(m) + r"\b") if re.match(r"^\w", m) else re.escape(m)
        for m, _ in markers
    )
    kind_by_marker = {m.lower(): kind for m, kind in markers}
    splitter = re.compile(r"(" + alternation + r")\s*:?", re.IGNORECASE)

    core_parts: List[str] = []
    context_parts: List[str] = []
    current = "core"
    pos = 0
    for match in splitter.finditer(jd_text):
        chunk = jd_text[pos : match.start()]
        (context_parts if current == "context" else core_parts).append(chunk)
        marker_text = re.sub(r"\s*:?$", "", match.group(0)).strip().lower()
        current = kind_by_marker.get(marker_text, current)
        pos = match.end()
    tail = jd_text[pos:]
    (context_parts if current == "context" else core_parts).append(tail)
    return ("\n".join(core_parts), "\n".join(context_parts))


def _detect_skills_in_text(segment: str, taxonomy: Dict[str, str]) -> List[str]:
    """Detect canonical skills mentioned in a text segment.

    Matches canonical names and synonyms as case-insensitive substrings
    with word boundaries, returning deduplicated canonical forms in order
    of first appearance.
    """
    lowered = f"\n{segment.lower()}\n"
    hits: List[Tuple[int, str]] = []
    seen: Set[str] = set()
    # Longest surface forms first so multi-word synonyms win.
    for surface, canonical in sorted(taxonomy.items(), key=lambda kv: len(kv[0]), reverse=True):
        if canonical in seen:
            continue
        pattern = r"(?<![a-z0-9+#./])" + re.escape(surface) + r"(?![a-z0-9+#])"
        match = re.search(pattern, lowered)
        if match:
            seen.add(canonical)
            hits.append((match.start(), canonical))
    hits.sort(key=lambda h: h[0])
    return [canonical for _, canonical in hits]


def parse_job_description(jd_text: str, job_id: str = "job-001", title: str = "Untitled Role") -> JobProfile:
    """Parse raw job description text into a structured JobProfile.

    Separates requirements into core (mandatory) and context (preferred)
    skills using keyword detection.

    Args:
        jd_text: Raw job description text.
        job_id: Unique identifier for the job.
        title: Job title.

    Returns:
        JobProfile with classified core and context skills.
    """
    taxonomy = load_esco_taxonomy()
    core_segment, context_segment = _split_jd_segments(jd_text)
    # A skill named in the required region is core even if it is repeated
    # under a "preferred" heading; context keeps only the non-core remainder.
    core_skills = _detect_skills_in_text(core_segment, taxonomy)
    context_skills = [
        s for s in _detect_skills_in_text(context_segment, taxonomy)
        if s not in core_skills
    ]
    # Fallback: if no headings were detected, everything is core.
    if not core_skills and not context_skills:
        core_skills = _detect_skills_in_text(jd_text, taxonomy)
    return JobProfile(
        job_id=job_id,
        title=title,
        raw_jd_text=jd_text,
        core_skills=core_skills,
        context_skills=context_skills,
    )


def fuzzy_match_skill(
    candidate_skill: str,
    target_skills: List[str],
    threshold: int = 85,
) -> Optional[Tuple[str, int]]:
    """Find the best fuzzy match for a candidate skill in target skills.

    Args:
        candidate_skill: Skill from the resume.
        target_skills: Skills from the job description.
        threshold: Minimum fuzzy match score (0-100).

    Returns:
        Tuple of (matched_skill, score) or None if no match above threshold.
    """
    from fuzzywuzzy import fuzz

    best: Optional[Tuple[str, int]] = None
    for target in target_skills:
        score = max(
            fuzz.ratio(candidate_skill.strip().lower(), target.strip().lower()),
            fuzz.token_set_ratio(candidate_skill.strip().lower(), target.strip().lower()),
        )
        if score >= threshold and (best is None or score > best[1]):
            best = (target, int(score))
    return best
