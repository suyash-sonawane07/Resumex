"""
Unit Tests — Matching Engine Module (Member 2)
================================================
Tests for: core/matcher.py and core/extractor.py

Run: pytest tests/test_matcher.py -v
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
from core.extractor import (
    load_esco_taxonomy,
    normalize_skill,
    normalize_skills_list,
    parse_job_description,
    fuzzy_match_skill,
)
from core.matcher import (
    compute_coverage,
    compute_semantic_similarity,
    calculate_hybrid_score,
    build_explainability_matrix,
    match_resume_to_job,
)


class TestESCOTaxonomy:
    """Tests for ESCO skill taxonomy loading and normalization."""

    def test_taxonomy_loads_without_error(self):
        """ESCO taxonomy CSV should load successfully."""
        taxonomy = load_esco_taxonomy()
        assert isinstance(taxonomy, dict)

    def test_taxonomy_contains_common_skills(self):
        """Taxonomy should include mappings for common technical skills."""
        taxonomy = load_esco_taxonomy()
        # At minimum, canonical forms should map to themselves
        assert "python" in taxonomy
        assert "javascript" in taxonomy

    def test_synonym_maps_to_canonical(self):
        """ESCO synonyms should resolve to canonical skill names."""
        taxonomy = load_esco_taxonomy()
        # postgresql should map to SQL
        assert taxonomy.get("postgresql") == "SQL"
        assert taxonomy.get("react.js") == "React"

    def test_normalize_skill_resolves_synonym(self):
        """normalize_skill should return canonical form for known synonyms."""
        result = normalize_skill("PostgreSQL")
        assert result == "SQL"

    def test_normalize_skill_preserves_unknown(self):
        """Unknown skills should be returned cleaned but not transformed."""
        result = normalize_skill("SomeObscureFramework")
        assert result == "SomeObscureFramework"

    def test_normalize_skills_list_deduplicates(self):
        """Duplicate canonical forms should be deduplicated."""
        skills = ["Python", "python3", "py"]
        result = normalize_skills_list(skills)
        assert len(result) == 1
        assert result[0] == "Python"


class TestCoverage:
    """Tests for deterministic skill coverage calculation."""

    def test_full_coverage(self):
        """All skills matched should produce 100% coverage."""
        cov, matched, missing = compute_coverage(
            ["python", "sql"], ["python", "sql"]
        )
        assert cov == 1.0
        assert len(missing) == 0

    def test_partial_coverage(self):
        """2 of 3 skills should produce ~66.67% coverage."""
        cov, matched, missing = compute_coverage(
            ["python", "sql"], ["python", "sql", "machine learning"]
        )
        assert abs(cov - 2/3) < 0.01
        assert "machine learning" in [m.lower() for m in missing]

    def test_zero_coverage(self):
        """No matching skills should produce 0% coverage."""
        cov, matched, missing = compute_coverage(
            ["java", "kotlin"], ["python", "sql"]
        )
        assert cov == 0.0
        assert len(missing) == 2

    def test_empty_target_returns_full_coverage(self):
        """Empty target skills list should default to 100% coverage."""
        cov, matched, missing = compute_coverage(
            ["python"], []
        )
        assert cov == 1.0


class TestSemanticSimilarity:
    """Tests for SBERT semantic similarity placeholder."""

    def test_returns_float_in_range(self):
        """Similarity score should be a float in [0.0, 1.0]."""
        sim = compute_semantic_similarity(
            "Experienced Python developer",
            "Looking for Python engineer",
        )
        assert isinstance(sim, float)
        assert 0.0 <= sim <= 1.0


class TestHybridScore:
    """Tests for hybrid score calculation."""

    def test_default_weights(self):
        """Default weights should produce correct composite score."""
        weights = ScoringWeights()
        score = calculate_hybrid_score(
            core_coverage=0.6667,
            context_coverage=0.5,
            semantic_similarity=0.72,
            weights=weights,
        )
        # Expected: 0.5*0.6667 + 0.2*0.5 + 0.3*0.72 = 0.3334 + 0.1 + 0.216 = 0.6494
        assert abs(score - 0.6494) < 0.01

    def test_all_zeros(self):
        """Zero inputs should produce zero score."""
        weights = ScoringWeights()
        score = calculate_hybrid_score(0.0, 0.0, 0.0, weights)
        assert score == 0.0

    def test_all_ones(self):
        """Perfect inputs should produce score of 1.0."""
        weights = ScoringWeights()
        score = calculate_hybrid_score(1.0, 1.0, 1.0, weights)
        assert score == 1.0

    def test_score_clamped_to_range(self):
        """Score should always be between 0.0 and 1.0."""
        weights = ScoringWeights()
        score = calculate_hybrid_score(1.0, 1.0, 1.0, weights)
        assert 0.0 <= score <= 1.0


class TestExplainabilityMatrix:
    """Tests for evidence matrix construction."""

    def test_matched_skills_have_correct_flag(self):
        """Matched skills should have matched=True."""
        matrix = build_explainability_matrix(
            candidate_skills=["python", "sql"],
            core_skills=["Python", "SQL"],
            context_skills=[],
            resume_text="Experienced in Python and SQL development.",
        )
        for evidence in matrix.core_evidence:
            assert evidence.matched is True
        assert len(matrix.core_missing_skills) == 0

    def test_missing_skills_flagged_correctly(self):
        """Unmatched skills should appear in missing list."""
        matrix = build_explainability_matrix(
            candidate_skills=["python"],
            core_skills=["Python", "Machine Learning"],
            context_skills=[],
            resume_text="Python developer.",
        )
        assert "Machine Learning" in matrix.core_missing_skills

    def test_empty_skills_produce_empty_matrix(self):
        """No required skills should produce empty evidence lists."""
        matrix = build_explainability_matrix(
            candidate_skills=["python"],
            core_skills=[],
            context_skills=[],
            resume_text="Text.",
        )
        assert len(matrix.core_evidence) == 0
        assert len(matrix.context_evidence) == 0


class TestMatchResumeContract:
    """Tests for the match_resume_to_job function contract."""

    def test_returns_match_result(self, mock_parsed_resume, mock_job_profile, mock_scoring_weights):
        """match_resume_to_job should return a valid MatchResult."""
        result = match_resume_to_job(
            resume=mock_parsed_resume,
            job=mock_job_profile,
            weights=mock_scoring_weights,
        )
        assert isinstance(result, MatchResult)
        assert 0.0 <= result.hybrid_score <= 100.0
        assert result.candidate_id == mock_parsed_resume.resume_id
        assert result.processing_time_ms >= 0

    def test_result_has_explainability(self, mock_parsed_resume, mock_job_profile, mock_scoring_weights):
        """MatchResult should include populated explainability matrix."""
        result = match_resume_to_job(
            resume=mock_parsed_resume,
            job=mock_job_profile,
            weights=mock_scoring_weights,
        )
        assert isinstance(result.explainability, ExplainabilityMatrix)
