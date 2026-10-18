"""
Pytest Fixtures & Shared Test Utilities
========================================
Provides reusable mock data and fixtures for all test modules.
"""

import pytest
from api.models import (
    ParsedResume,
    JobProfile,
    ScoringWeights,
    MatchResult,
    ExplainabilityMatrix,
    SkillEvidence,
)


# ─── Sample Resume Fixtures ─────────────────────────────────────────

SAMPLE_RESUME_TEXT = """
John Smith
Bangalore, India
john.smith@email.com | +91-9876543210

Skills:
Python, PostgreSQL, Data Visualization, Pandas, NumPy, FastAPI

Experience:
Software Engineer at TechCorp (2021-2024)
- Built backend services and data transformation scripts using Python and Pandas.
- Architected database schemas and optimized indexing in PostgreSQL.
- Deployed containerized workloads to AWS ECS using Docker.

Education:
B.Tech in Computer Science, IIT Delhi (2021)

Projects:
- Built a sentiment analysis pipeline using spaCy and scikit-learn.
- Developed a REST API for data ingestion using FastAPI.
"""

SAMPLE_JD_TEXT = """
Software Engineer

Required Skills:
- Python
- SQL
- Machine Learning

Preferred Skills:
- AWS
- Docker
- REST API development
"""


@pytest.fixture
def sample_resume_text():
    """Raw resume text for testing."""
    return SAMPLE_RESUME_TEXT


@pytest.fixture
def sample_jd_text():
    """Raw job description text for testing."""
    return SAMPLE_JD_TEXT


@pytest.fixture
def mock_parsed_resume():
    """A fully populated ParsedResume for testing downstream modules."""
    return ParsedResume(
        resume_id="res-test123abc",
        filename="John_Smith_Resume.pdf",
        raw_text=SAMPLE_RESUME_TEXT,
        sanitized_text=SAMPLE_RESUME_TEXT.replace(
            "John Smith", "[REDACTED_NAME]"
        ).replace(
            "Bangalore, India", "[REDACTED_LOCATION]"
        ).replace(
            "john.smith@email.com", "[REDACTED_CONTACT]"
        ).replace(
            "+91-9876543210", "[REDACTED_CONTACT]"
        ),
        skills_extracted=["python", "postgresql", "data visualization", "pandas", "numpy", "fastapi"],
        skills_block="Python, PostgreSQL, Data Visualization, Pandas, NumPy, FastAPI",
        experience_block=(
            "Software Engineer at TechCorp (2021-2024)\n"
            "- Built backend services and data transformation scripts using Python and Pandas.\n"
            "- Architected database schemas and optimized indexing in PostgreSQL.\n"
            "- Deployed containerized workloads to AWS ECS using Docker."
        ),
        education_block="B.Tech in Computer Science, IIT Delhi (2021)",
        projects_block=(
            "- Built a sentiment analysis pipeline using spaCy and scikit-learn.\n"
            "- Developed a REST API for data ingestion using FastAPI."
        ),
        is_blind_screened=True,
        char_count=450,
    )


@pytest.fixture
def mock_job_profile():
    """A fully populated JobProfile for testing matching logic."""
    return JobProfile(
        job_id="job-test-001",
        title="Software Engineer",
        raw_jd_text=SAMPLE_JD_TEXT,
        core_skills=["Python", "SQL", "Machine Learning"],
        context_skills=["AWS", "Docker", "REST API"],
    )


@pytest.fixture
def mock_scoring_weights():
    """Default scoring weights for testing."""
    return ScoringWeights(
        w_core=0.5,
        w_context=0.2,
        w_semantic=0.3,
    )


@pytest.fixture
def mock_match_result():
    """A fully populated MatchResult for testing UI rendering."""
    return MatchResult(
        candidate_id="res-test123abc",
        filename="John_Smith_Resume.pdf",
        core_coverage_pct=66.67,
        context_coverage_pct=50.00,
        semantic_similarity_pct=72.00,
        hybrid_score=64.93,
        explainability=ExplainabilityMatrix(
            core_evidence=[
                SkillEvidence(
                    skill="Python",
                    matched=True,
                    matched_term="python",
                    source_sentence="Built backend services and data transformation scripts using Python and Pandas.",
                    section="experience",
                ),
                SkillEvidence(
                    skill="SQL",
                    matched=True,
                    matched_term="postgresql",
                    source_sentence="Architected database schemas and optimized indexing in PostgreSQL.",
                    section="experience",
                ),
                SkillEvidence(
                    skill="Machine Learning",
                    matched=False,
                    matched_term=None,
                    source_sentence=None,
                    section=None,
                ),
            ],
            context_evidence=[
                SkillEvidence(
                    skill="AWS",
                    matched=True,
                    matched_term="aws",
                    source_sentence="Deployed containerized workloads to AWS ECS using Docker.",
                    section="experience",
                ),
                SkillEvidence(
                    skill="Docker",
                    matched=True,
                    matched_term="docker",
                    source_sentence="Deployed containerized workloads to AWS ECS using Docker.",
                    section="experience",
                ),
                SkillEvidence(
                    skill="REST API",
                    matched=False,
                    matched_term=None,
                    source_sentence=None,
                    section=None,
                ),
            ],
            core_missing_skills=["Machine Learning"],
            context_missing_skills=["REST API"],
        ),
        processing_time_ms=342.5,
    )


@pytest.fixture
def mock_batch_results(mock_match_result):
    """A list of multiple MatchResults for testing leaderboard rendering."""
    result_1 = mock_match_result

    result_2 = MatchResult(
        candidate_id="res-test456def",
        filename="Alice_Johnson_Resume.pdf",
        core_coverage_pct=100.00,
        context_coverage_pct=33.33,
        semantic_similarity_pct=85.00,
        hybrid_score=82.17,
        explainability=ExplainabilityMatrix(
            core_evidence=[
                SkillEvidence(skill="Python", matched=True, matched_term="python"),
                SkillEvidence(skill="SQL", matched=True, matched_term="sql"),
                SkillEvidence(skill="Machine Learning", matched=True, matched_term="ml"),
            ],
            context_evidence=[
                SkillEvidence(skill="AWS", matched=True, matched_term="aws"),
                SkillEvidence(skill="Docker", matched=False),
                SkillEvidence(skill="REST API", matched=False),
            ],
            core_missing_skills=[],
            context_missing_skills=["Docker", "REST API"],
        ),
        processing_time_ms=310.1,
    )

    result_3 = MatchResult(
        candidate_id="res-test789ghi",
        filename="Bob_Lee_Resume.pdf",
        core_coverage_pct=33.33,
        context_coverage_pct=0.00,
        semantic_similarity_pct=45.00,
        hybrid_score=30.17,
        explainability=ExplainabilityMatrix(
            core_evidence=[
                SkillEvidence(skill="Python", matched=True, matched_term="python"),
                SkillEvidence(skill="SQL", matched=False),
                SkillEvidence(skill="Machine Learning", matched=False),
            ],
            context_evidence=[
                SkillEvidence(skill="AWS", matched=False),
                SkillEvidence(skill="Docker", matched=False),
                SkillEvidence(skill="REST API", matched=False),
            ],
            core_missing_skills=["SQL", "Machine Learning"],
            context_missing_skills=["AWS", "Docker", "REST API"],
        ),
        processing_time_ms=290.8,
    )

    return [result_1, result_2, result_3]
