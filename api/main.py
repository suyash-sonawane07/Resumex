"""
FastAPI Application — Optional Decoupled REST Interface
========================================================
Owner: Member 3

Provides an optional HTTP API layer for the Resume Intelligence System.
The primary interface is the Streamlit UI (frontend/app.py), but this
module enables headless / programmatic access.

Do NOT implement core parsing or matching logic here.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List

from api.models import (
    BatchMatchResponse,
    JobProfile,
    MatchResult,
    ScoringWeights,
    ScannedPDFException,
    InvalidFileException,
)

app = FastAPI(
    title="Resume Intelligence API",
    description="AI-Powered Resume Matching & Explainability Engine",
    version="1.0.0-mvp",
)


@app.get("/health")
def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": "1.0.0-mvp"}


@app.post("/api/match", response_model=BatchMatchResponse)
async def match_resumes(
    jd_text: str = Form(..., description="Job description text"),
    files: List[UploadFile] = File(..., description="PDF resume files"),
    w_core: float = Form(default=0.5),
    w_context: float = Form(default=0.2),
    w_semantic: float = Form(default=0.3),
    job_title: str = Form(default="Untitled Role"),
    blind_screening: bool = Form(default=True),
):
    """Process uploaded resumes against a job description.

    Full in-memory pipeline (same code path as the Streamlit UI):
      1. Parse each resume (core.parser.parse_resume)
      2. Parse JD into core/context skills (core.extractor)
      3. Score + explain (core.matcher.match_resume_to_job)
      4. Return results ranked by hybrid score.
    """
    from core.extractor import parse_job_description
    from core.matcher import match_resume_to_job
    from core.parser import parse_resume

    weights = ScoringWeights(
        w_core=w_core, w_context=w_context, w_semantic=w_semantic
    )
    # Normalize so weights always sum to 1.0 (same rule as UI sliders).
    total = weights.w_core + weights.w_context + weights.w_semantic
    if total > 0:
        weights = ScoringWeights(
            w_core=round(weights.w_core / total, 4),
            w_context=round(weights.w_context / total, 4),
            w_semantic=round(weights.w_semantic / total, 4),
        )

    job = parse_job_description(
        jd_text=jd_text, job_id="job-api-session", title=job_title
    )

    results: List[MatchResult] = []
    errors: List[str] = []
    for upload in files[:10]:  # enforce MAX_BATCH_SIZE
        try:
            file_bytes = await upload.read()
            parsed = parse_resume(
                file_bytes=file_bytes,
                filename=upload.filename or "resume.pdf",
                redact_pii=blind_screening,
            )
            results.append(
                match_resume_to_job(resume=parsed, job=job, weights=weights)
            )
        except (ScannedPDFException, InvalidFileException) as e:
            errors.append(f"{e.filename}: {e.message}")
    if not results and errors:
        raise HTTPException(status_code=422, detail="; ".join(errors))

    ranked = sorted(results, key=lambda r: r.hybrid_score, reverse=True)
    return BatchMatchResponse(
        job_id=job.job_id,
        total_candidates=len(ranked),
        ranked_results=ranked,
        scoring_weights_used=weights,
    )
