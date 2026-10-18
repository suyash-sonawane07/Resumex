"""
UI Components — BoardUI Visual Widgets & Data Transformers
===========================================================
Owner: Member 3

Adapts the official BoardUI component library (MIT, React + Tailwind v4
at https://github.com/BoardUI/boardui) into Streamlit-compatible HTML
widgets and Plotly charts.

Responsibilities:
  - BoardUI Stat Cards (footer variant with icon tile and caption band)
  - BoardUI Status Chips (lime, yellow, rose, blue, neutral)
  - BoardUI Halo Status Dots (green, yellow, rose, blue)
  - Plotly Skill Gap Donut Chart (BoardUI chart-1..5 color tokens)
  - Evidence Table & Leaderboard Data formatters
  - File upload card widgets

Tested APIs preserved:
  - render_skill_gap_chart(explainability)
  - format_evidence_table(explainability)
  - format_leaderboard_row(result)
  - format_leaderboard(results)
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import List, Optional, Tuple

from api.models import MatchResult, ExplainabilityMatrix, SkillEvidence


# ─── BoardUI Status Indicators ────────────────────────────────────────

def status_dot_html(kind: str = "green") -> str:
    """BoardUI 12x12 status indicator: 6px solid dot centered on a tinted halo.

    Color variants:
      - green  → verified / high match
      - yellow → partial match / warning
      - rose   → missing core skill / adversarial / danger
      - blue   → info / staged
    """
    valid = {"green", "yellow", "rose", "blue"}
    dot_kind = kind if kind in valid else "green"
    return (
        f'<span class="bui-status-dot bui-dot-{dot_kind}" aria-hidden="true">'
        f'<span class="bui-status-dot-inner"></span>'
        f'</span>'
    )


def chip_html(label: str, kind: str = "neutral") -> str:
    """BoardUI status chip pill (bold/subtle recipe from Figma).

    Color variants: success (lime), warning (yellow), danger (rose),
    info (blue), neutral (gray).
    """
    safe_kinds = {"success", "warning", "danger", "info", "neutral"}
    if kind not in safe_kinds:
        kind = "neutral"
    return f'<span class="bui-chip bui-chip-{kind}">{label}</span>'


def score_chip(hybrid_score: float) -> str:
    """Status chip for a candidate's hybrid compatibility score."""
    from frontend.service import status_for_score

    kind = status_for_score(hybrid_score)
    label = (
        "Strong match" if kind == "success"
        else "Partial match" if kind == "warning"
        else "Weak match"
    )
    return chip_html(f"{label} · {hybrid_score:.1f}%", kind)


# ─── BoardUI KPI Stat Cards (Footer Variant) ─────────────────────────

def stat_card_html(
    label: str,
    value: str,
    sub: str = "",
    tone: str = "blue",
    delta: str = "",
    delta_color: str = "lime",
) -> str:
    """BoardUI KPI Stat Card (footer variant matching Figma node 3731:3160).

    Features:
      - Top tile: Tinted icon tile beside uppercase category label
      - Body: Large display-size KPI value
      - Footer band: Secondary background band with comparison caption + status chip
    """
    tone_class = f"bui-icon-{tone}" if tone in {"blue", "purple", "emerald", "amber"} else "bui-icon-blue"

    # Tone icon glyphs
    glyph_map = {
        "blue": "📄",
        "purple": "📊",
        "emerald": "🏆",
        "amber": "⚠️",
    }
    icon_glyph = glyph_map.get(tone, "📈")

    delta_chip = ""
    if delta:
        chip_kind = "success" if delta_color == "lime" else ("danger" if delta_color == "rose" else "neutral")
        delta_chip = chip_html(delta, chip_kind)

    footer_content = f"<span>{sub}</span>{delta_chip}" if sub or delta else "<span>Verified against current role</span>"

    return f"""
<div class="bui-stat-card">
  <div class="bui-stat-body">
    <div class="bui-stat-header">
      <div class="bui-stat-icon-tile {tone_class}">{icon_glyph}</div>
      <p class="bui-kpi-label">{label}</p>
    </div>
    <p class="bui-kpi">{value}</p>
  </div>
  <div class="bui-stat-footer">
    {footer_content}
  </div>
</div>
"""


# ─── BoardUI File Row Card ───────────────────────────────────────────

def file_card_html(filename: str, size_str: str, status_text: str = "Staged for analysis") -> str:
    """BoardUI file card showing file icon, name, size, and status chip."""
    return f"""
<div class="bui-file-card">
  <div class="bui-file-info">
    <div class="bui-file-icon-box">PDF</div>
    <div>
      <div class="bui-file-name">{filename}</div>
      <div class="bui-file-meta">Digital PDF · {size_str}</div>
    </div>
  </div>
  <div>
    {chip_html(status_text, "info")}
  </div>
</div>
"""


# ─── Resumex Brand & Intro Components ─────────────────────────────────

def resumex_logo_svg(size: int = 32) -> str:
    """Official Resumex brand emblem: crisp geometric badge with RX monogram."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 36 36" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:inline-block; vertical-align:middle; flex-shrink:0;">'
        f'<rect width="36" height="36" rx="9" fill="#121317"/>'
        f'<path d="M10 10H16C18.2 10 19.5 11.1 19.5 12.8C19.5 14.2 18.5 15.2 17.1 15.5L20.2 24H16.8L14 16.4H12.5V24H10V10ZM12.5 14.2H15.6C16.5 14.2 17 13.7 17 12.8C17 12 16.5 11.5 15.6 11.5H12.5V14.2Z" fill="#FFFFFF"/>'
        f'<path d="M20.5 13.5L23.8 18.4L20 24H23.4L25.4 20.8L27.4 24H30.8L27 18.4L30.3 13.5H27L25.4 16.2L23.8 13.5H20.5Z" fill="#3B82F6"/>'
        f'<circle cx="28.5" cy="10.5" r="2.2" fill="#10B981"/>'
        f'</svg>'
    )


def antigravity_logo_svg(size: int = 26) -> str:
    """Backward-compatible alias pointing to resumex_logo_svg."""
    return resumex_logo_svg(size)


def simple_intro_html() -> str:
    """Simplest modern Resumex intro header banner."""
    logo = resumex_logo_svg(36)
    return (
        f'<div class="rx-intro-container">'
        f'  <div class="rx-intro-header">'
        f'    <div class="rx-intro-brand">'
        f'      {logo}'
        f'      <div>'
        f'        <div class="rx-brand-name">Resumex</div>'
        f'        <div class="rx-brand-sub">AI-Powered Resume Intelligence & Candidate Matching System</div>'
        f'      </div>'
        f'    </div>'
        f'    <div class="rx-intro-tags">'
        f'      <span class="rx-tag rx-tag-sla">⚡ SLA: 178ms</span>'
        f'      <span class="rx-tag rx-tag-dpdp">🛡️ RAM Only · DPDP Compliant</span>'
        f'      <span class="rx-tag rx-tag-explain">🎯 100% Explainable</span>'
        f'    </div>'
        f'  </div>'
        f'  <p class="rx-intro-desc">'
        f'    Layout-aware spatial PDF extraction, canonical ESCO competencies, and dense semantic matching — evaluated with 100% explainability strictly in volatile memory.'
        f'  </p>'
        f'</div>'
    )


def particle_burst_svg() -> str:
    return ""


def hero_announcement_capsule_html() -> str:
    return ""


def hero_nav_html(active_nav: str = "Resume Analysis") -> str:
    return ""


def hero_centerpiece_html() -> str:
    return ""


def dot_matrix_html(cols: int = 5, rows: int = 5) -> str:
    """Subtle Antigravity orbital particle pattern."""
    return """
<div style="position:relative; width:90px; height:90px; display:flex; align-items:center; justify-content:center;">
  <div style="position:absolute; width:80px; height:80px; border:1px dashed rgba(66, 133, 244, 0.25); border-radius:50%;"></div>
  <div style="position:absolute; width:52px; height:52px; border:1px dashed rgba(234, 67, 53, 0.2); border-radius:50%;"></div>
  <div style="width:7px; height:7px; border-radius:50%; background:#4285f4;"></div>
</div>
"""


def spotlight_card_html(
    role_title: str,
    badge_gold: str,
    route_text: str,
    track_left: str = "●",
    track_right: str = "⏱ 178ms",
) -> str:
    """Antigravity capability card with clean typography and subtle orbital track."""
    dot_color = "#4285f4" if "Data" in role_title or "Rank 1" in role_title else (
        "#34a853" if "Backend" in role_title or "Rank 2" in role_title else "#fbbc04"
    )
    return f"""
<div class="bui-spotlight-card agy-spotlight-card">
  <div class="bui-card-top-row">
    <div class="bui-card-role-title">
      <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{dot_color};"></span>
      {role_title}
    </div>
    <div class="agy-card-badge">{badge_gold}</div>
  </div>
  <div class="bui-card-route">{route_text}</div>
  <div class="bui-flight-track">
    <span style="color:{dot_color}; font-size:0.75rem;">{track_left}</span>
    <div class="bui-flight-track-dots"></div>
    <span style="font-size:0.74rem; font-weight:500;">{track_right}</span>
  </div>
</div>
"""


def pagination_dots_html(total: int = 4, active_idx: int = 0) -> str:
    """Minimal pill pagination indicator."""
    dots = []
    for i in range(total):
        cls = "bui-pag-dot bui-pag-dot-active" if i == active_idx else "bui-pag-dot"
        dots.append(f'<span class="{cls}"></span>')
    dots_str = "".join(dots)
    return f"""
<div class="bui-pagination-dots">
  {dots_str}
</div>
"""



# ─── Plotly Donut Chart (Google Antigravity Quad-Color Tokens) ───────

def render_skill_gap_chart(explainability: ExplainabilityMatrix) -> Optional[object]:
    """Render a Plotly donut chart showing fulfilled vs. missing skills.

    Uses Google Antigravity tokens:
      - Core Matched: #34A853 (Google Green)
      - Context Matched: #4285F4 (Google Blue)
      - Core Missing: #EA4335 (Google Red)
      - Context Missing: #E5E7EB (Neutral Track)
    """
    total_core = len(explainability.core_evidence)
    matched_core = sum(1 for e in explainability.core_evidence if e.matched)
    missing_core = total_core - matched_core

    total_context = len(explainability.context_evidence)
    matched_context = sum(1 for e in explainability.context_evidence if e.matched)
    missing_context = total_context - matched_context

    total_skills = total_core + total_context

    if total_skills == 0:
        return None

    try:
        import plotly.graph_objects as go

        labels = []
        values = []
        colors = []

        if matched_core > 0:
            labels.append(f"Core Matched ({matched_core})")
            values.append(matched_core)
            colors.append("#34a853")  # Google Green

        if missing_core > 0:
            labels.append(f"Core Missing ({missing_core})")
            values.append(missing_core)
            colors.append("#ea4335")  # Google Red

        if matched_context > 0:
            labels.append(f"Preferred Matched ({matched_context})")
            values.append(matched_context)
            colors.append("#4285f4")  # Google Blue

        if missing_context > 0:
            labels.append(f"Preferred Missing ({missing_context})")
            values.append(missing_context)
            colors.append("#e5e7eb")  # Neutral Track


        # Calculate fulfillment percentage for center hole
        pct_fulfilled = round((matched_core / total_core * 100), 1) if total_core > 0 else 100.0

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
            textinfo="percent",
            hoverinfo="label+value",
            sort=False,
        )])

        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=11, family="Inter, sans-serif"),
            ),
            margin=dict(l=10, r=10, t=25, b=50),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<b>{pct_fulfilled:.0f}%</b><br><span style='font-size:11px;color:#737373'>Core Met</span>",
                x=0.5, y=0.5,
                font=dict(size=20, family="Inter, sans-serif"),
                showarrow=False,
            )],
        )
        return fig
    except ImportError:
        return None


# ─── Data Formatters for Tables and Leaderboards ──────────────────────

def format_evidence_table(explainability: ExplainabilityMatrix) -> List[dict]:
    """Format the explainability matrix as a list of table rows.

    Maintains contract tested by tests/test_ui_integration.py.
    """
    rows = []

    for evidence in explainability.core_evidence:
        rows.append({
            "Skill": evidence.skill,
            "Type": "Core (Required)",
            "Status": "✅ Matched" if evidence.matched else "❌ Missing",
            "Matched Term": evidence.matched_term or "—",
            "Evidence": evidence.source_sentence or "—",
            "Section": evidence.section or "—",
        })

    for evidence in explainability.context_evidence:
        rows.append({
            "Skill": evidence.skill,
            "Type": "Context (Preferred)",
            "Status": "✅ Matched" if evidence.matched else "⚠️ Missing",
            "Matched Term": evidence.matched_term or "—",
            "Evidence": evidence.source_sentence or "—",
            "Section": evidence.section or "—",
        })

    return rows


def format_leaderboard_row(result: MatchResult) -> dict:
    """Format a single MatchResult into a leaderboard table row."""
    return {
        "Candidate": result.filename,
        "Hybrid Score": f"{result.hybrid_score:.1f}%",
        "Core Match": f"{result.core_coverage_pct:.1f}%",
        "Context Match": f"{result.context_coverage_pct:.1f}%",
        "Semantic Similarity": f"{result.semantic_similarity_pct:.1f}%",
        "Processing Time": f"{result.processing_time_ms:.0f}ms",
    }


def format_leaderboard(results: List[MatchResult]) -> List[dict]:
    """Format ranked results into leaderboard display rows sorted descending."""
    sorted_results = sorted(results, key=lambda r: r.hybrid_score, reverse=True)
    return [format_leaderboard_row(r) for r in sorted_results]


def ranked_table_data(results: List[MatchResult]) -> List[dict]:
    """Numeric leaderboard rows for sortable/searchable display."""
    rows = []
    for rank, r in enumerate(
        sorted(results, key=lambda x: x.hybrid_score, reverse=True), start=1
    ):
        matched = sum(1 for e in r.explainability.core_evidence if e.matched)
        total = len(r.explainability.core_evidence)
        rows.append({
            "Rank": rank,
            "Candidate": r.filename,
            "Hybrid %": round(r.hybrid_score, 1),
            "Core %": round(r.core_coverage_pct, 1),
            "Preferred %": round(r.context_coverage_pct, 1),
            "Semantic %": round(r.semantic_similarity_pct, 1),
            "Core skills": f"{matched}/{total}" if total else "—",
            "candidate_id": r.candidate_id,
        })
    return rows


def evidence_items(explainability: ExplainabilityMatrix) -> Tuple[
        List[SkillEvidence], List[SkillEvidence]]:
    """Split evidence into (verified matches, missing/unconfirmed)."""
    matched, missing = [], []
    for e in list(explainability.core_evidence) + list(
            explainability.context_evidence):
        (matched if e.matched else missing).append(e)
    return matched, missing
