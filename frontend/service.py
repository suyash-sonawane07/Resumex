"""
Analysis Service — Application State & Backend Integration
==========================================================
Owner: Member 3

Single integration point between the Streamlit frontend and the backend
modules. All calls go through the frozen Pydantic contracts in
api.models; no scoring or parsing logic lives here.

If a backend module is unavailable, `run_analysis` raises the original
error to the caller — there is no silent mock path in production. Sample
JDs loaded via `load_sample_jds()` are explicitly labeled as samples in
the UI and never presented as user-authored input.
"""

import json
import sys
from pathlib import Path
from typing import Callable, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.models import (
    BatchMatchResponse,
    JobProfile,
    MatchResult,
    ScoringWeights,
    ScannedPDFException,
    InvalidFileException,
    ResumeProcessingError,
)
from core.parser import MAX_FILE_SIZE_BYTES, parse_resume
from core.matcher import match_resume_to_job
from core.extractor import parse_job_description

MAX_FILES_PER_BATCH = 10
SAMPLE_JDS_PATH = PROJECT_ROOT / "data" / "benchmark" / "sample_jds.json"


def validate_uploads(files: list) -> List[str]:
    """Pre-flight validation of uploaded files. Returns error strings."""
    errors = []
    if len(files) > MAX_FILES_PER_BATCH:
        errors.append(
            f"Maximum {MAX_FILES_PER_BATCH} resumes per batch — "
            f"{len(files)} uploaded. Remove extras to continue."
        )
    for f in files:
        name = getattr(f, "name", "unknown")
        if not name.lower().endswith(".pdf"):
            errors.append(f"{name}: only PDF files are supported.")
        size = getattr(f, "size", None)
        if size is not None and size > MAX_FILE_SIZE_BYTES:
            errors.append(
                f"{name}: exceeds the 5 MB size limit "
                f"({size / 1024 / 1024:.1f} MB)."
            )
    return errors


def normalize_weights(w_core: float, w_context: float,
                      w_semantic: float) -> ScoringWeights:
    """Normalize slider weights so they sum to 1.0 (BoardUI slider pattern)."""
    total = w_core + w_context + w_semantic
    if total <= 0:
        return ScoringWeights()
    return ScoringWeights(
        w_core=round(w_core / total, 4),
        w_context=round(w_context / total, 4),
        w_semantic=round(w_semantic / total, 4),
    )


def build_job_profile(jd_text: str, title: str) -> JobProfile:
    """Parse raw JD text into a JobProfile contract."""
    return parse_job_description(
        jd_text=jd_text, job_id="job-ui-session", title=title or "Untitled Role"
    )


def run_analysis(
    files: list,
    job: JobProfile,
    weights: ScoringWeights,
    blind_screening: bool = True,
    progress_cb: Optional[Callable[[float, str], None]] = None,
) -> Tuple[BatchMatchResponse, List[str]]:
    """Run the full pipeline over uploaded files, all in memory.

    Returns (BatchMatchResponse with results ranked desc, error messages).
    Processing errors are isolated per file — one bad PDF never aborts
    the batch or clears session state.
    """
    results: List[MatchResult] = []
    errors: List[str] = []
    total = max(len(files), 1)
    for i, uploaded_file in enumerate(files):
        try:
            file_bytes = uploaded_file.read()
            parsed = parse_resume(
                file_bytes=file_bytes,
                filename=uploaded_file.name,
                redact_pii=blind_screening,
            )
            results.append(
                match_resume_to_job(resume=parsed, job=job, weights=weights)
            )
        except ScannedPDFException as e:
            errors.append(
                f"{e.filename or uploaded_file.name}: scanned or image-based "
                "PDF — no extractable text. Re-export from Word or Google Docs."
            )
        except InvalidFileException as e:
            errors.append(f"{e.filename or uploaded_file.name}: {e.message}")
        except ResumeProcessingError as e:
            errors.append(f"{e.filename or uploaded_file.name}: {e.message}")
        except Exception as e:  # never lose the session on one file
            errors.append(f"{uploaded_file.name}: unexpected error — {e}")
        if progress_cb:
            progress_cb((i + 1) / total, f"Processed {i + 1}/{len(files)}…")
    ranked = sorted(results, key=lambda r: r.hybrid_score, reverse=True)
    return (
        BatchMatchResponse(
            job_id=job.job_id,
            total_candidates=len(ranked),
            ranked_results=ranked,
            scoring_weights_used=weights,
        ),
        errors,
    )


def load_sample_jds() -> List[dict]:
    """Load benchmark JDs as explicitly-labeled *sample* presets."""
    try:
        return json.loads(SAMPLE_JDS_PATH.read_text())["jobs"]
    except (OSError, ValueError, KeyError):
        return []


def summarize_batch(batch: BatchMatchResponse) -> dict:
    """Aggregate KPIs for the results dashboard (display only, no scoring)."""
    results = batch.ranked_results
    if not results:
        return {"total": 0, "average": 0.0, "strongest": None,
                "missing_core": []}
    missing: dict = {}
    for r in results:
        for s in r.explainability.core_missing_skills:
            missing[s] = missing.get(s, 0) + 1
    return {
        "total": len(results),
        "average": sum(r.hybrid_score for r in results) / len(results),
        "strongest": max(results, key=lambda r: r.hybrid_score),
        "missing_core": sorted(missing.items(), key=lambda kv: -kv[1]),
    }


def status_for_score(score: float) -> str:
    """Bucket a hybrid score into a BoardUI-style status chip label."""
    if score >= 70:
        return "success"
    if score >= 40:
        return "warning"
    return "danger"


class InMemoryUpload:
    """In-memory file wrapper matching Streamlit's UploadedFile interface for benchmark evaluation."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self.data = data
        self.size = len(data)

    def read(self) -> bytes:
        return self.data


def load_benchmark_resumes() -> List[InMemoryUpload]:
    """Load the 10 benchmark resumes directly into RAM for instant 1-click evaluation."""
    resumes_dir = PROJECT_ROOT / "data" / "benchmark" / "resumes"
    if not resumes_dir.exists():
        return []
    uploads = []
    for pdf_path in sorted(resumes_dir.glob("*.pdf")):
        try:
            uploads.append(InMemoryUpload(pdf_path.name, pdf_path.read_bytes()))
        except Exception:
            pass
    return uploads

