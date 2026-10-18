"""
Shared Data Contracts — AI-Powered Resume Intelligence System
=============================================================
This module defines the Pydantic v2 schemas that form the communication
contracts between all three development modules:

  - Member 1 (Resume Parser)  →  produces ParsedResume
  - Member 2 (Matching Engine) →  consumes ParsedResume, produces MatchResult
  - Member 3 (UI / Integration) →  consumes BatchMatchResponse, renders UI

⚠️  FROZEN CONTRACT: Do not modify this file on a feature branch.
    Any schema change requires unanimous agreement from all 3 members
    and must be committed to the 'develop' branch directly.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ─── Scoring Configuration ───────────────────────────────────────────

class ScoringWeights(BaseModel):
    """User-configurable weights for the hybrid matching formula.

    Invariant: w_core + w_context + w_semantic == 1.0
    """
    w_core: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Weight for mandatory/core skill coverage"
    )
    w_context: float = Field(
        default=0.2, ge=0.0, le=1.0,
        description="Weight for preferred/context skill coverage"
    )
    w_semantic: float = Field(
        default=0.3, ge=0.0, le=1.0,
        description="Weight for SBERT semantic similarity"
    )


# ─── Resume Processing Contracts (Member 1 Output) ──────────────────

class ParsedResume(BaseModel):
    """Structured output from the resume parsing pipeline.

    Produced by: core.parser.parse_resume()
    Consumed by: core.matcher.match_resume_to_job()
    """
    resume_id: str = Field(
        ..., description="UUID or sanitized filename hash"
    )
    filename: str = Field(
        ..., description="Original uploaded filename"
    )
    raw_text: str = Field(
        ..., description="Full extracted text before sanitization"
    )
    sanitized_text: str = Field(
        ..., description="Text with PII redacted (if blind screening enabled)"
    )
    skills_extracted: List[str] = Field(
        default_factory=list,
        description="List of extracted skill tokens (lowercased)"
    )
    skills_block: str = Field(
        default="",
        description="Raw text under the Skills/Technologies section heading"
    )
    experience_block: str = Field(
        default="",
        description="Raw text under the Experience/Employment section heading"
    )
    education_block: str = Field(
        default="",
        description="Raw text under the Education section heading"
    )
    projects_block: str = Field(
        default="",
        description="Raw text under the Projects section heading"
    )
    is_blind_screened: bool = Field(
        default=True,
        description="Whether PII redaction was applied"
    )
    char_count: int = Field(
        ..., ge=0,
        description="Total character count of extracted text"
    )


# ─── Job Description Contracts (Member 2 Input) ─────────────────────

class JobProfile(BaseModel):
    """Structured representation of a job description.

    Produced by: core.extractor.parse_job_description() or UI input
    Consumed by: core.matcher.match_resume_to_job()
    """
    job_id: str = Field(
        ..., description="Unique identifier for the job posting"
    )
    title: str = Field(
        ..., description="Job title"
    )
    raw_jd_text: str = Field(
        ..., description="Original unprocessed job description text"
    )
    core_skills: List[str] = Field(
        ..., description="Mandatory/required skills extracted from JD"
    )
    context_skills: List[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have skills extracted from JD"
    )


# ─── Matching & Explainability Contracts (Member 2 Output) ──────────

class SkillEvidence(BaseModel):
    """Evidence linking a required skill to a resume sentence."""
    skill: str = Field(
        ..., description="The required skill being evaluated"
    )
    matched: bool = Field(
        ..., description="Whether the skill was found in the resume"
    )
    matched_term: Optional[str] = Field(
        default=None,
        description="The exact term/synonym found in the resume"
    )
    source_sentence: Optional[str] = Field(
        default=None,
        description="Verbatim resume sentence containing the evidence"
    )
    section: Optional[str] = Field(
        default=None,
        description="Resume section where evidence was found (skills/experience/education/projects)"
    )


class ExplainabilityMatrix(BaseModel):
    """Complete evidence mapping for a candidate-job match."""
    core_evidence: List[SkillEvidence] = Field(
        default_factory=list,
        description="Evidence for each mandatory skill"
    )
    context_evidence: List[SkillEvidence] = Field(
        default_factory=list,
        description="Evidence for each preferred skill"
    )
    core_missing_skills: List[str] = Field(
        default_factory=list,
        description="Mandatory skills not found in the resume"
    )
    context_missing_skills: List[str] = Field(
        default_factory=list,
        description="Preferred skills not found in the resume"
    )


class MatchResult(BaseModel):
    """Complete matching result for a single candidate against a job.

    Produced by: core.matcher.match_resume_to_job()
    Consumed by: frontend.components rendering functions
    """
    candidate_id: str = Field(
        ..., description="Maps to ParsedResume.resume_id"
    )
    filename: str = Field(
        ..., description="Original resume filename"
    )
    core_coverage_pct: float = Field(
        ..., ge=0.0, le=100.0,
        description="Percentage of mandatory skills matched"
    )
    context_coverage_pct: float = Field(
        ..., ge=0.0, le=100.0,
        description="Percentage of preferred skills matched"
    )
    semantic_similarity_pct: float = Field(
        ..., ge=0.0, le=100.0,
        description="SBERT cosine similarity as percentage"
    )
    hybrid_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Weighted composite score"
    )
    explainability: ExplainabilityMatrix = Field(
        ..., description="Line-item evidence for each skill"
    )
    processing_time_ms: float = Field(
        ..., ge=0.0,
        description="End-to-end processing time in milliseconds"
    )


class BatchMatchResponse(BaseModel):
    """Aggregated matching results for a batch of candidates.

    Produced by: application orchestrator
    Consumed by: frontend.app.render_leaderboard()
    """
    job_id: str
    total_candidates: int = Field(..., ge=0)
    ranked_results: List[MatchResult] = Field(
        default_factory=list,
        description="Results sorted descending by hybrid_score"
    )
    scoring_weights_used: ScoringWeights


# ─── Custom Exceptions ──────────────────────────────────────────────

class ResumeProcessingError(Exception):
    """Base exception for resume processing failures."""
    def __init__(self, message: str, filename: str = ""):
        self.message = message
        self.filename = filename
        super().__init__(self.message)


class ScannedPDFException(ResumeProcessingError):
    """Raised when an uploaded PDF is scanned/image-based with no text layer.

    Triggered when extracted character count < 50.
    """
    def __init__(self, filename: str = ""):
        super().__init__(
            message=(
                "Scanned or image-based PDF detected. "
                "Please upload a text-based digital PDF. "
                "Tip: Re-export your resume from its source application (e.g., Word, Google Docs)."
            ),
            filename=filename,
        )


class InvalidFileException(ResumeProcessingError):
    """Raised when a file fails MIME type, extension, or size validation."""
    pass


class EmptyResumeException(ResumeProcessingError):
    """Raised when parsing produces no usable text content."""
    pass
