"""
Integration Tests — UI Components & End-to-End Pipeline (Member 3)
===================================================================
Tests for: frontend/components.py and module integration

Run: pytest tests/test_ui_integration.py -v
"""

import pytest
from api.models import (
    BatchMatchResponse,
    MatchResult,
    ScoringWeights,
    ExplainabilityMatrix,
    SkillEvidence,
)
from frontend.components import (
    format_leaderboard,
    format_leaderboard_row,
    format_evidence_table,
    render_skill_gap_chart,
)


class TestLeaderboardFormatting:
    """Tests for candidate leaderboard rendering."""

    def test_leaderboard_sorted_descending(self, mock_batch_results):
        """Leaderboard should sort candidates descending by hybrid score."""
        rows = format_leaderboard(mock_batch_results)
        scores = []
        for row in rows:
            # Extract numeric value from formatted string like "82.2%"
            score_str = row["Hybrid Score"].rstrip("%")
            scores.append(float(score_str))
        # Verify descending order
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], (
                f"Leaderboard not sorted: {scores[i]} < {scores[i+1]}"
            )

    def test_leaderboard_row_has_required_keys(self, mock_match_result):
        """Each row should contain all expected display fields."""
        row = format_leaderboard_row(mock_match_result)
        assert "Candidate" in row
        assert "Hybrid Score" in row
        assert "Core Match" in row
        assert "Context Match" in row
        assert "Semantic Similarity" in row
        assert "Processing Time" in row

    def test_empty_results_produce_empty_leaderboard(self):
        """Empty results list should produce empty leaderboard."""
        rows = format_leaderboard([])
        assert rows == []


class TestEvidenceTable:
    """Tests for explainability evidence table formatting."""

    def test_evidence_table_has_rows(self, mock_match_result):
        """Evidence table should have rows for each skill."""
        rows = format_evidence_table(mock_match_result.explainability)
        assert len(rows) > 0

    def test_core_skills_labeled_correctly(self, mock_match_result):
        """Core skills should be labeled as 'Core (Required)'."""
        rows = format_evidence_table(mock_match_result.explainability)
        core_rows = [r for r in rows if r["Type"] == "Core (Required)"]
        assert len(core_rows) == len(mock_match_result.explainability.core_evidence)

    def test_matched_skills_show_checkmark(self, mock_match_result):
        """Matched skills should display checkmark status."""
        rows = format_evidence_table(mock_match_result.explainability)
        matched_rows = [r for r in rows if "✅" in r["Status"]]
        assert len(matched_rows) > 0

    def test_missing_skills_show_cross_or_warning(self, mock_match_result):
        """Missing skills should display cross or warning status."""
        rows = format_evidence_table(mock_match_result.explainability)
        missing_rows = [r for r in rows if "❌" in r["Status"] or "⚠️" in r["Status"]]
        assert len(missing_rows) > 0

    def test_empty_explainability_produces_empty_table(self):
        """Empty explainability matrix should produce empty table."""
        empty_matrix = ExplainabilityMatrix()
        rows = format_evidence_table(empty_matrix)
        assert rows == []


class TestSkillGapChart:
    """Tests for Plotly donut chart generation."""

    def test_chart_with_valid_data(self, mock_match_result):
        """Chart should be generated for valid explainability data."""
        fig = render_skill_gap_chart(mock_match_result.explainability)
        # May be None if plotly not installed, but should not raise
        # If plotly is available, should return a figure object
        if fig is not None:
            assert hasattr(fig, 'data')  # Plotly figure has .data attribute

    def test_chart_with_empty_data(self):
        """Empty data should return None (no chart to display)."""
        empty_matrix = ExplainabilityMatrix()
        fig = render_skill_gap_chart(empty_matrix)
        assert fig is None


class TestBatchMatchResponseContract:
    """Tests for the BatchMatchResponse data contract."""

    def test_batch_response_valid(self, mock_batch_results, mock_scoring_weights):
        """BatchMatchResponse should accept valid result data."""
        batch = BatchMatchResponse(
            job_id="job-test-001",
            total_candidates=len(mock_batch_results),
            ranked_results=mock_batch_results,
            scoring_weights_used=mock_scoring_weights,
        )
        assert batch.total_candidates == 3
        assert len(batch.ranked_results) == 3


class TestEndToEndPipeline:
    """Integration test: mock data through the complete pipeline."""

    def test_full_pipeline_mock(
        self, mock_parsed_resume, mock_job_profile, mock_scoring_weights
    ):
        """Full pipeline should execute without errors using mock data."""
        from core.matcher import match_resume_to_job

        result = match_resume_to_job(
            resume=mock_parsed_resume,
            job=mock_job_profile,
            weights=mock_scoring_weights,
        )

        # Verify result structure
        assert isinstance(result, MatchResult)
        assert result.candidate_id == mock_parsed_resume.resume_id
        assert result.filename == mock_parsed_resume.filename

        # Verify scores are reasonable
        assert 0.0 <= result.hybrid_score <= 100.0
        assert 0.0 <= result.core_coverage_pct <= 100.0
        assert 0.0 <= result.context_coverage_pct <= 100.0
        assert 0.0 <= result.semantic_similarity_pct <= 100.0

        # Verify explainability exists
        assert isinstance(result.explainability, ExplainabilityMatrix)

        # Verify leaderboard formatting works
        rows = format_leaderboard([result])
        assert len(rows) == 1
