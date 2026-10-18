"""
Resumex — Resume Intelligence & Matching Engine
===============================================
Owner: Member 3

Single-page app with a 3-step flow anyone can use with zero training:

    Step 1. Describe the role (pick a sample or paste a JD)
    Step 2. Add resumes (upload PDFs or load benchmark set)
    Step 3. Read the results (ranked table + per-candidate evidence)

Design rules: one page, no navigation, no settings screens, no dead
controls. Everything visible fits the task; everything else was removed.
"""

import sys
from pathlib import Path

# Automatically ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import streamlit as st

from frontend import components as C
from frontend.service import (
    build_job_profile,
    load_benchmark_resumes,
    load_sample_jds,
    normalize_weights,
    run_analysis,
    summarize_batch,
    validate_uploads,
)
from frontend.theme import get_theme_css

# ─── Page config & session defaults ─────────────────────────────
st.set_page_config(
    page_title="Resumex — Resume Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

_samples = load_sample_jds()
_default_jd = _samples[0] if _samples else {
    "title": "Data Scientist", "raw_jd_text": "", "job_id": "ds-001"}

_DEFAULTS = {
    "jd_title": _default_jd["title"],
    "jd_text": _default_jd["raw_jd_text"],
    "last_sample": f"{_default_jd['job_id']} — {_default_jd['title']} (sample)",
    "w_core": 0.5,
    "w_context": 0.2,
    "w_semantic": 0.3,
    "blind": True,
    "batch": None,
    "errors": [],
    "removed": set(),
    "benchmark_files": [],
    "selected_candidate": None,
}
for _key, _value in _DEFAULTS.items():
    st.session_state.setdefault(_key, _value)

st.markdown(get_theme_css("light"), unsafe_allow_html=True)


# ─── Sidebar: scoring weights + privacy only ────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.6rem;">'
        f'{C.resumex_logo_svg(26)}'
        f'<div><div style="font-weight:700;">Resumex</div>'
        f'<div style="font-size:0.75rem;color:#6b7280;">Resume Intelligence</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.subheader("Scoring weights")
    st.slider("Mandatory skills", 0.0, 1.0, key="w_core",
              help="Share of the score from must-have skill coverage.")
    st.slider("Preferred skills", 0.0, 1.0, key="w_context",
              help="Share of the score from nice-to-have skill coverage.")
    st.slider("Semantic similarity", 0.0, 1.0, key="w_semantic",
              help="Share of the score from overall meaning match (SBERT).")
    _w = normalize_weights(
        st.session_state.w_core, st.session_state.w_context,
        st.session_state.w_semantic)
    st.caption(
        f"Normalized → {_w.w_core:.2f} + {_w.w_context:.2f} + "
        f"{_w.w_semantic:.2f} = 1.00")
    st.divider()
    st.toggle("Blind screening (hide names & contacts)", key="blind",
              help="Redact names, locations, emails and phone numbers before scoring.")
    st.caption(
        "🔒 Private by design: files live in memory only and vanish on reset. "
        "DPDP Act 2023 compliant.")


# ─── Header: slim brand bar, no hero clutter ────────────────────
st.markdown(
    f'<div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.2rem;">'
    f'{C.resumex_logo_svg(34)}'
    f'<div><div style="font-size:1.5rem;font-weight:700;letter-spacing:-0.02em;">'
    f"Resumex</div>"
    f'<div style="color:#6b7280;font-size:0.9rem;">'
    f"Paste a job description, add resumes, get ranked candidates — "
    f"every score backed by a resume quote.</div></div></div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div style='margin:0.4rem 0 1.2rem 0;display:flex;gap:0.4rem;'>"
    f"{C.chip_html('⚡ ~178 ms / resume', 'success')}"
    f"{C.chip_html('🛡️ RAM only', 'info')}"
    f"{C.chip_html('🎯 100% explainable', 'neutral')}"
    f"</div>",
    unsafe_allow_html=True,
)

with st.expander("How is the score calculated?"):
    st.markdown(
        "**Score = 0.5 × mandatory coverage + 0.2 × preferred coverage + "
        "0.3 × semantic similarity** (adjustable in the sidebar).\n\n"
        "- **Mandatory / preferred coverage** — fraction of required skills "
        "found in the resume. Synonyms count fully "
        "(`PostgreSQL` → `SQL`, `sklearn` → `Scikit-learn`).\n"
        "- **Semantic similarity** — overall meaning match between the "
        "resume and the job description (SBERT embeddings).\n"
        "- **Evidence** — every matched skill cites the exact resume "
        "sentence; missing skills are listed as gaps.\n"
        "- **Fairness** — names, locations and contacts are redacted "
        "*before* scoring, and injected instructions like “rank me 100%” "
        "are ignored because embeddings can't follow orders.")


# ═══ Step 1 — Describe the role ═════════════════════════════════
with st.container(border=True):
    st.markdown("### ① Describe the role")
    samples = load_sample_jds()
    options = ["Write my own"] + [
        f"{s['job_id']} — {s['title']} (sample)" for s in samples]

    c_pick, c_title = st.columns([1.4, 2.6])
    with c_pick:
        choice = st.selectbox("Start from a sample", options,
                              index=1 if len(options) > 1 else 0,
                              help="Samples are clearly labeled presets you can edit freely.")
        if choice != st.session_state.last_sample:
            st.session_state.last_sample = choice
            if choice != "Write my own":
                picked = next((s for s in samples if choice.startswith(s["job_id"])), None)
                if picked:
                    st.session_state.jd_title = picked["title"]
                    st.session_state.jd_text = picked["raw_jd_text"]
                    st.rerun()
    with c_title:
        st.session_state.jd_title = st.text_input(
            "Job title", value=st.session_state.jd_title)

    st.session_state.jd_text = st.text_area(
        "Job description — list must-haves under “Required”, nice-to-haves under “Preferred”",
        value=st.session_state.jd_text, height=170,
        placeholder=("Required Skills:\n- Python\n- SQL\n- Machine Learning\n\n"
                     "Preferred Skills:\n- AWS\n- Docker"),
    )


# ═══ Step 2 — Add resumes ═══════════════════════════════════════
with st.container(border=True):
    st.markdown("### ② Add resumes")
    c_demo, c_clear = st.columns([2.2, 1.8])
    with c_demo:
        if st.button("⚡ Try with 10 sample resumes",
                     help="Loads the built-in evaluation set instantly — nothing is uploaded anywhere."):
            st.session_state.benchmark_files = load_benchmark_resumes()
            st.session_state.removed = set()
            st.toast("10 sample resumes loaded — press “Match resumes” below.")
            st.rerun()
    with c_clear:
        if st.session_state.benchmark_files and st.button("Clear samples"):
            st.session_state.benchmark_files = []
            st.session_state.removed = set()
            st.rerun()

    uploaded = st.file_uploader(
        "Drop your PDF resumes here (up to 10, 5 MB each)",
        type=["pdf"], accept_multiple_files=True,
        label_visibility="visible",
    ) or []

    combined = list(st.session_state.benchmark_files) + list(uploaded)
    active = [f for f in combined if f.name not in st.session_state.removed]

    if active:
        st.markdown(f"**{len(active)} resume(s) ready** — all in memory, nothing saved.")
        for f in active:
            size_kb = (getattr(f, "size", 0) or 0) / 1024
            size = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(C.file_card_html(f.name, size, "Ready"), unsafe_allow_html=True)
            with cols[1]:
                if st.button("Remove", key=f"rm-{f.name}"):
                    st.session_state.removed.add(f.name)
                    st.rerun()
    else:
        st.markdown(
            '<div class="bui-empty">No resumes yet.<br>'
            "Drag & drop PDFs above, or press <strong>“⚡ Try with 10 sample "
            "resumes”</strong> for an instant demo.</div>",
            unsafe_allow_html=True,
        )

pre_errors = validate_uploads(active)
for _msg in pre_errors:
    st.error(_msg)
if not st.session_state.jd_text.strip() and active:
    st.warning("Describe the role in Step ① before matching.")

can_run = bool(active and st.session_state.jd_text.strip() and not pre_errors)
if st.button("③ Match resumes ⚡", type="primary", disabled=not can_run,
             help="Score every resume against this role."):
    weights = normalize_weights(st.session_state.w_core,
                                st.session_state.w_context,
                                st.session_state.w_semantic)
    with st.status("Reading resumes and scoring…", expanded=True) as status:
        job = build_job_profile(st.session_state.jd_text.strip(),
                                st.session_state.jd_title.strip())
        if not job.core_skills and not job.context_skills:
            st.warning("No skills found under Required/Preferred headings — "
                       "ranking will use meaning similarity only.")
        batch, errors = run_analysis(
            active, job, weights,
            blind_screening=st.session_state.blind,
            progress_cb=lambda frac, text: status.update(
                label=f"Scoring… {text}"),
        )
        status.update(label="Done.", state="complete")
    st.session_state.batch = batch
    st.session_state.errors = errors
    st.session_state.selected_candidate = None
    st.rerun()

for _msg in st.session_state.errors:
    st.error(_msg)


# ═══ Step 3 — Results (same page, appears after a run) ═════════
batch = st.session_state.batch
if batch is not None and batch.ranked_results:
    st.divider()
    st.markdown("### ③ Results — ranked best match first")
    summary = summarize_batch(batch)
    top = summary["strongest"]
    gap = summary["missing_core"][0] if summary["missing_core"] else None
    st.markdown(
        f"**{summary['total']} candidates** · average "
        f"{summary['average']:.1f}% · top match **{top.filename}** "
        f"({top.hybrid_score:.1f}%)"
        + (f" · most common gap: **{gap[0]}** (missing in {gap[1]}/{summary['total']})"
           if gap else " · no shared skill gaps 🎉"),
    )

    rows = C.ranked_table_data(batch.ranked_results)
    df = pd.DataFrame(rows).drop(columns=["candidate_id"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("Clear results (keep my files & role)"):
        st.session_state.batch = None
        st.session_state.errors = []
        st.session_state.selected_candidate = None
        st.rerun()

    # — Candidate deep dive —
    options = [r["Candidate"] for r in rows]
    current = st.session_state.selected_candidate
    if current not in options:
        current = options[0]
    st.session_state.selected_candidate = st.selectbox(
        "Inspect a candidate — every score links to proof", options,
        index=options.index(current))
    result = next(r for r in batch.ranked_results
                  if r.filename == st.session_state.selected_candidate)
    matched, missing = C.evidence_items(result.explainability)

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:0.75rem;margin-top:0.5rem;">'
        f'<h3 style="margin:0;">{result.filename}</h3>'
        f"{C.score_chip(result.hybrid_score)}</div>",
        unsafe_allow_html=True,
    )
    m1, m2, m3 = st.columns(3)
    m1.metric("Mandatory skills", f"{result.core_coverage_pct:.0f}%",
              help="Share of must-have skills found in this resume.")
    m2.metric("Preferred skills", f"{result.context_coverage_pct:.0f}%",
              help="Share of nice-to-have skills found in this resume.")
    m3.metric("Meaning match", f"{result.semantic_similarity_pct:.0f}%",
              help="Overall semantic similarity between resume and job description.")
    st.caption(
        f"Score = 0.5×{result.core_coverage_pct:.0f} + "
        f"0.2×{result.context_coverage_pct:.0f} + "
        f"0.3×{result.semantic_similarity_pct:.0f} = "
        f"**{result.hybrid_score:.1f}%** · analyzed in "
        f"{result.processing_time_ms:.0f} ms")

    left, right = st.columns([1, 2])
    with left:
        st.subheader("At a glance")
        fig = C.render_skill_gap_chart(result.explainability)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No required skills to visualize.")
        st.markdown(
            f"✅ **{len(matched)}** skills proven with quotes<br>"
            f"❌ **{len(missing)}** gaps to discuss with the candidate",
            unsafe_allow_html=True,
        )
    with right:
        st.subheader("Proof — exact resume quotes")
        tabs = st.tabs([f"✅ Proven ({len(matched)})",
                        f"❌ Gaps ({len(missing)})"])
        with tabs[0]:
            if not matched:
                st.info("No verified skill matches for this candidate.")
            for e in matched:
                kind = "Must-have" if e in result.explainability.core_evidence else "Nice-to-have"
                quote = (f'<div class="bui-evidence-quote">“{e.source_sentence}”</div>'
                         if e.source_sentence else "")
                st.markdown(
                    f'<div class="bui-evidence-card">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:center;gap:0.5rem;">'
                    f'<span style="font-weight:600;">{e.skill}</span>'
                    f"{C.chip_html(kind, 'neutral')}</div>"
                    f'<div style="font-size:0.8rem;color:#6b7280;">'
                    f"Found as <code>{e.matched_term or '—'}</code></div>"
                    f"{quote}</div>",
                    unsafe_allow_html=True,
                )
        with tabs[1]:
            if not missing:
                st.success("Full coverage — this candidate meets every requirement. 🎉")
            for e in missing:
                must = e in result.explainability.core_evidence
                st.markdown(
                    f'<div class="bui-evidence-card" '
                    f'style="border-left:3px solid #ea4335;">'
                    f'<div style="display:flex;justify-content:space-between;'
                    f'align-items:center;gap:0.5rem;">'
                    f'<span style="font-weight:600;">{e.skill}</span>'
                    f"{C.chip_html('must-have gap' if must else 'nice-to-have gap', 'danger' if must else 'warning')}</div>"
                    f'<div style="font-size:0.82rem;color:#6b7280;margin-top:4px;">'
                    f"Not found in this resume — "
                    f"{'ask about it in the interview.' if must else 'optional, not a blocker.'}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

st.divider()
st.caption("Resumex · scores explain themselves · files never leave this session")
