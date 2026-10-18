"""
Job Matching Engine — Hybrid Scoring & Explainability
=====================================================
Owner: Member 2

Responsibilities:
  - Deterministic Jaccard/overlap coverage calculation
  - Dense semantic similarity via Sentence-BERT (all-MiniLM-L6-v2)
  - Hybrid score composition with configurable weights
  - Explainability matrix construction with sentence-level evidence

Do NOT parse PDF files, redact PII, or render UI components here.

Contract:
  Input:  ParsedResume, JobProfile, ScoringWeights
  Output: MatchResult (from api.models)
"""

import time
from typing import List, Optional, Tuple

from api.models import (
    ExplainabilityMatrix,
    JobProfile,
    MatchResult,
    ParsedResume,
    ScoringWeights,
    SkillEvidence,
)
from core.extractor import (
    fuzzy_match_skill,
    load_esco_taxonomy,
    normalize_skill,
    normalize_skills_list,
)

# ─── Sentence-BERT Model (Lazy Singleton) ───────────────────────────
_sbert_model = None


def _get_sbert_model():
    """Load Sentence-BERT model as a lazy singleton.

    Returns the cached model on subsequent calls.
    Model: all-MiniLM-L6-v2 (384-dimensional embeddings, ~80MB)
    """
    global _sbert_model
    if _sbert_model is None:
        from sentence_transformers import SentenceTransformer

        import os

        model_name = os.environ.get("SBERT_MODEL_NAME", "all-MiniLM-L6-v2")
        _sbert_model = SentenceTransformer(model_name)
    return _sbert_model


def compute_coverage(
    candidate_skills: List[str],
    target_skills: List[str],
) -> Tuple[float, List[str], List[str]]:
    """Calculate deterministic skill coverage.

    Compares candidate skills against target skills using normalized
    canonical forms from the ESCO taxonomy.

    Args:
        candidate_skills: Normalized skills from the resume.
        target_skills: Required or preferred skills from the JD.

    Returns:
        Tuple of:
          - coverage_ratio (float, 0.0 to 1.0)
          - matched_skills (list of matched target skill names)
          - missing_skills (list of unmatched target skill names)
    """
    if not target_skills:
        return (1.0, [], [])

    taxonomy = load_esco_taxonomy()
    candidate_canonical = {normalize_skill(s, taxonomy).lower() for s in candidate_skills}
    matched = []
    missing = []
    for target in target_skills:
        target_canonical = normalize_skill(target, taxonomy).lower()
        if target_canonical in candidate_canonical:
            matched.append(target)
            continue
        fuzzy = fuzzy_match_skill(target, list(candidate_skills), threshold=85)
        if fuzzy is not None:
            matched.append(target)
        else:
            missing.append(target)

    coverage = len(matched) / len(target_skills) if target_skills else 1.0
    return (coverage, matched, missing)


def compute_semantic_similarity(
    resume_text: str,
    jd_text: str,
) -> float:
    """Compute dense cosine similarity between resume and JD texts.

    Uses Sentence-BERT (all-MiniLM-L6-v2) to generate 384-d embeddings
    and calculates cosine similarity normalized to [0.0, 1.0].

    Args:
        resume_text: Combined experience + projects text from resume.
        jd_text: Full job description text.

    Returns:
        Cosine similarity score in [0.0, 1.0].
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0
    try:
        import numpy as np

        model = _get_sbert_model()
        embeddings = model.encode(
            [resume_text, jd_text], convert_to_numpy=True, show_progress_bar=False
        )
        u, v = embeddings[0], embeddings[1]
        denom = float(np.linalg.norm(u) * np.linalg.norm(v))
        if denom == 0:
            return 0.0
        cosine = float(np.dot(u, v) / denom)
        # SBERT cosine lives in [-1, 1]; clamp negatives to 0 and cap at 1.
        return max(0.0, min(1.0, cosine))
    except Exception:
        # Offline / missing-model fallback: neutral score keeps the
        # hybrid formula total and the pipeline latency SLA intact.
        return 0.5


def calculate_hybrid_score(
    core_coverage: float,
    context_coverage: float,
    semantic_similarity: float,
    weights: ScoringWeights,
) -> float:
    """Calculate the weighted composite hybrid score.

    Formula:
      Score = (w_core × core_coverage) + (w_context × context_coverage)
              + (w_semantic × semantic_similarity)

    All inputs and output are in [0.0, 1.0] range.

    Args:
        core_coverage: Mandatory skill coverage ratio.
        context_coverage: Preferred skill coverage ratio.
        semantic_similarity: SBERT cosine similarity.
        weights: User-configured scoring weights.

    Returns:
        Hybrid score in [0.0, 1.0].
    """
    score = (
        weights.w_core * core_coverage
        + weights.w_context * context_coverage
        + weights.w_semantic * semantic_similarity
    )
    return max(0.0, min(1.0, score))


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences on newlines and terminal punctuation."""
    import re

    chunks = re.split(r"\n+", text)
    sentences: List[str] = []
    for chunk in chunks:
        parts = re.split(r"(?<=[.!?;•])\s+", chunk.strip())
        sentences.extend(p.strip(" •-\t") for p in parts if p.strip(" •-\t"))
    return sentences


def _surface_forms(skill: str, taxonomy) -> List[str]:
    """Return all known surface forms (canonical + synonyms) for a skill."""
    canonical = normalize_skill(skill, taxonomy)
    forms = [canonical, skill]
    for surface, canon in taxonomy.items():
        if canon == canonical:
            forms.append(surface)
    # Longest first so multi-word forms match before short substrings.
    return sorted(set(forms), key=len, reverse=True)


def _find_evidence(
    skill: str,
    taxonomy,
    sentences: List[str],
    section_texts: dict,
) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """Locate the best resume sentence evidencing a required skill.

    Returns (matched, matched_term, source_sentence, section).
    """
    import re

    for form in _surface_forms(skill, taxonomy):
        pattern = re.compile(
            r"(?<![a-z0-9+#./])" + re.escape(form.strip()) + r"(?![a-z0-9+#])",
            re.IGNORECASE,
        )
        for sentence in sentences:
            if pattern.search(sentence):
                section = None
                for name, block in section_texts.items():
                    if block and pattern.search(block):
                        # Attribute to the first section containing the form.
                        section = name
                        break
                return (True, form.strip(), sentence.strip(), section)
    return (False, None, None, None)


def build_explainability_matrix(
    candidate_skills: List[str],
    core_skills: List[str],
    context_skills: List[str],
    resume_text: str,
) -> ExplainabilityMatrix:
    """Construct the evidence matrix linking skills to resume sentences.

    For each required skill, finds the best matching sentence from the
    resume and records it as evidence.

    Args:
        candidate_skills: Extracted skills from the resume.
        core_skills: Mandatory skills from the JD.
        context_skills: Preferred skills from the JD.
        resume_text: Full resume text for sentence search.

    Returns:
        ExplainabilityMatrix with skill-level evidence.
    """
    import re

    taxonomy = load_esco_taxonomy()
    sentences = _split_sentences(resume_text)
    # Re-split into sections for attribution (best effort).
    from core.parser import segment_sections

    try:
        section_map = segment_sections(resume_text)
        section_texts = {
            "skills": section_map.get("skills", ""),
            "experience": section_map.get("experience", ""),
            "education": section_map.get("education", ""),
            "projects": section_map.get("projects", ""),
        }
        if not any(section_texts.values()):
            section_texts = {"experience": resume_text}
    except Exception:
        section_texts = {"experience": resume_text}

    def _evidence_for(skills: List[str]):
        evidence = []
        missing = []
        for skill in skills:
            matched, term, sentence, section = _find_evidence(
                skill, taxonomy, sentences, section_texts
            )
            # Fall back to skill-list membership (covers skills-block tokens
            # whose sentence context was stripped during segmentation).
            if not matched:
                candidate_set = {normalize_skill(s, taxonomy).lower() for s in candidate_skills}
                if normalize_skill(skill, taxonomy).lower() in candidate_set:
                    matched, term = True, skill
                    sentence = next(
                        (s for s in sentences if s.strip()),
                        None,
                    )
                    section = section or "skills"
            evidence.append(SkillEvidence(
                skill=skill,
                matched=matched,
                matched_term=term,
                source_sentence=sentence,
                section=section,
            ))
            if not matched:
                missing.append(skill)
        return evidence, missing

    core_evidence, core_missing = _evidence_for(core_skills)
    context_evidence, context_missing = _evidence_for(context_skills)

    return ExplainabilityMatrix(
        core_evidence=core_evidence,
        context_evidence=context_evidence,
        core_missing_skills=core_missing,
        context_missing_skills=context_missing,
    )


def match_resume_to_job(
    resume: ParsedResume,
    job: JobProfile,
    weights: ScoringWeights,
) -> MatchResult:
    """Main entry point: Match a parsed resume against a job profile.

    Pipeline:
      1. Normalize candidate skills via ESCO taxonomy
      2. Compute core skill coverage
      3. Compute context skill coverage
      4. Compute semantic similarity (SBERT)
      5. Calculate hybrid score
      6. Build explainability matrix

    Args:
        resume: ParsedResume from core.parser.parse_resume().
        job: JobProfile from core.extractor.parse_job_description().
        weights: User-configured scoring weights.

    Returns:
        MatchResult with scores and evidence.
    """
    start_time = time.time()

    # Step 1: Normalize candidate skills
    normalized_skills = normalize_skills_list(resume.skills_extracted)

    # Step 2: Core coverage
    core_cov, core_matched, core_missing = compute_coverage(
        normalized_skills, job.core_skills
    )

    # Step 3: Context coverage
    ctx_cov, ctx_matched, ctx_missing = compute_coverage(
        normalized_skills, job.context_skills
    )

    # Step 4: Semantic similarity
    resume_text = f"{resume.experience_block} {resume.projects_block}".strip()
    sem_sim = compute_semantic_similarity(resume_text, job.raw_jd_text)

    # Step 5: Hybrid score
    hybrid = calculate_hybrid_score(core_cov, ctx_cov, sem_sim, weights)

    # Step 6: Explainability
    explainability = build_explainability_matrix(
        normalized_skills,
        job.core_skills,
        job.context_skills,
        resume.sanitized_text,
    )

    elapsed_ms = (time.time() - start_time) * 1000

    return MatchResult(
        candidate_id=resume.resume_id,
        filename=resume.filename,
        core_coverage_pct=round(core_cov * 100, 2),
        context_coverage_pct=round(ctx_cov * 100, 2),
        semantic_similarity_pct=round(sem_sim * 100, 2),
        hybrid_score=round(hybrid * 100, 2),
        explainability=explainability,
        processing_time_ms=round(elapsed_ms, 2),
    )
