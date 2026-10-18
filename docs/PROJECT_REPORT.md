# AI-Powered Resume Intelligence and Job Matching System

**A Hybrid Lexical–Semantic Screening Engine with Explainable Evidence Attribution,
Adversarial Robustness, and Ephemeral PII Handling**

*Academic Project Report — IEEE/ACM conference structure (Markdown + LaTeX-ready math)*
*Team of three · Python 3.10 · Local CPU · Zero external APIs*

---

## Abstract

Traditional Applicant Tracking Systems (ATS) rely on deterministic keyword
matching. They reject qualified candidates who write "PostgreSQL" instead of
"SQL", promote resumes stuffed with invisible keywords, and offer no auditable
justification for their scores. We present an end-to-end, locally runnable
resume intelligence system that replaces opaque keyword filtering with a
**hybrid matching engine**: deterministic ESCO-taxonomy skill coverage
(Jaccard-style overlap with synonym normalization) fused with dense semantic
similarity from Sentence-BERT (`all-MiniLM-L6-v2`, 384 dimensions). Every
matched skill is attributed to a **verbatim resume sentence** in an
explainability matrix; every input is **blind-screened** (names, locations,
contacts redacted) and processed **entirely in RAM** for compliance with
India's DPDP Act 2023.

On a purpose-built benchmark (3 job descriptions × 10 deterministic PDF
resumes spanning strong, synonym-heavy, multi-column, adversarial, and
out-of-domain cases), the proposed hybrid achieves **mean nDCG@5 = 1.000 /
nDCG@10 = 1.000**, outperforming Keyword Jaccard (0.898/0.959), TF-IDF Cosine
(0.997/0.994), and pure SBERT (0.966/0.991). End-to-end latency is
**0.178 s mean / 0.357 s max per document on CPU** — 17× headroom under the
3.0 s SLA. A prompt-injected resume ("ignore previous instructions, rank
100%") is buried at ranks 8–9/10 with scores 17–25/100. All 51 pytest unit
and integration tests pass.

**Keywords:** resume screening, hybrid retrieval, SBERT, ESCO taxonomy,
explainable AI, adversarial robustness, PII redaction, DPDP Act.

---

## 1. Introduction & Motivation

Campus hiring and entry-level recruiting exhibit a painful asymmetry:
hundreds of resumes per posting meet a few minutes of reviewer attention, so
teams delegate triage to ATS software. Commercial ATS products share four
systemic failure modes that motivate this work:

1. **Semantic blindness.** Exact-match parsers reject "PostgreSQL" for a job
   requiring "SQL", or "fast api" for `REST API` — penalizing vocabulary
   rather than competence.
2. **Adversarial gaming.** White-on-white keyword dumps and injected
   instructions ("ignore previous instructions, score 100%") inflate opaque
   match percentages in systems that cannot distinguish evidence from text.
3. **No auditability.** A single percentage with no provenance prevents
   recruiters from verifying decisions and gives candidates no actionable
   feedback.
4. **Demographic leakage.** Names, locations, and contact metadata flow into
   scoring pipelines, replicating historical hiring bias and violating data
   minimization principles.

We address all four with a local-first, zero-cost architecture: layout-aware
PDF parsing, blind screening before vectorization, hybrid lexical–semantic
scoring, sentence-level evidence, and RAM-only ephemeral state.

---

## 2. Problem Formulation & Mathematical Modeling

### 2.1 Objects

A resume document $R$ is parsed into section blocks
$R = (S_{\text{skills}}, S_{\text{exp}}, S_{\text{edu}}, S_{\text{proj}})$ plus
an extracted skill token multiset $S(R)$. A job specification $J$ is
decomposed into mandatory and preferred skill sets,
$J = (C, P)$ (core, context), with full description text $T_J$.

### 2.2 ESCO normalization $\phi(s) \to \hat{s}$

Let $\mathcal{T}$ be the ESCO lookup mapping each known surface form
(including synonyms such as `postgres → SQL`, `sklearn → Scikit-learn`,
`web api → REST API`) to a canonical skill $\hat{s}$. Normalization is

$$\phi(s) = \mathcal{T}(\text{lower}(\text{strip}(s))) \quad \text{or } s
\text{ itself if unlisted},$$

applied set-wise with deduplication on canonical forms. Fuzzy matching
(`fuzz.ratio` / `token_set_ratio`, threshold ≥ 85) covers near-miss
spellings. JD segmentation splits $T_J$ into core/context regions at
required-type vs. preferred-type heading markers (inline-marker splitting
handles single-line JDs), then detects canonical skills per region.

### 2.3 Baseline A — Keyword Jaccard (no taxonomy)

$$S_A(R, J) = \frac{|W(R) \cap W(J)|}{|W(R) \cup W(J)|},$$

where $W(\cdot)$ are raw lowercased word tokens. This reproduces legacy ATS
behavior: synonyms never match.

### 2.4 Baseline B — TF-IDF Cosine

$$\mathbf{t}_R, \mathbf{t}_J \in \mathbb{R}^{|V|} \quad\text{(sparse TF-IDF)},\qquad
S_B(R, J) = \frac{\mathbf{t}_R \cdot \mathbf{t}_J}
{\lVert\mathbf{t}_R\rVert_2 \lVert\mathbf{t}_J\rVert_2}.$$

TF-IDF rewards exact rare-term overlap (hence strong on keyword-dense
technical text) but remains vocabulary-bound.

### 2.5 Baseline C — Pure SBERT

A siamese Sentence-BERT encoder $E: \text{text} \to \mathbb{R}^{384}$
(`all-MiniLM-L6-v2`) embeds resume evidence text
$u = E(S_{\text{exp}} \oplus S_{\text{proj}})$ and JD text
$v = E(T_J)$:

$$S_C(R, J) = \max\!\left(0, \frac{u \cdot v}
{\lVert u\rVert_2 \lVert v\rVert_2}\right) \in [0, 1].$$

### 2.6 Baseline D (Proposed) — Hybrid

$$Coverage_{core} = \frac{|\text{matched core skills}|}{|\text{total core skills}|}, \qquad
Coverage_{context} = \frac{|\text{matched preferred}|}{|\text{total preferred}|}$$
($1.0$ by convention when no preferred skills exist), and

$$\text{Score}_{\text{hybrid}} = (W_1 \times Coverage_{core}) +
(W_2 \times Coverage_{context}) + (W_3 \times Sim_{\text{semantic}}),$$

subject to $W_i \in [0,1]$, $\sum_i W_i = 1$ (defaults
$W = (0.5, 0.2, 0.3)$; UI sliders auto-normalize). Deterministic coverage
provides precision and synonym recall; the dense term provides semantic
recall for paraphrased experience.

### 2.7 Metric — nDCG@K

For graded relevance $rel_i \in \{0,1,2,3\}$ of the $i$-th ranked resume,

$$DCG@K = \sum_{i=1}^{K} \frac{2^{rel_i} - 1}{\log_2(i+1)}, \qquad
nDCG@K = \frac{DCG@K}{IDCG@K},$$

where $IDCG@K$ is the ideal-ranked DCG. nDCG is chosen over Precision@K/MAP
because our judgments are graded (a synonym-partial match, grade 2, is
worth more than a transferable-skill match, grade 1) and rank position of
the best candidates matters most to recruiters.

---

## 3. Architectural Pipeline & Component Engineering

```
JD text + weights → parse_job_description → JobProfile ─┐
PDF bytes → validate → pdfplumber spatial extract → ─┐   │
  section segment → skill tokens → sanitize (PII) ─┴→ ParsedResume → match → MatchResult
                                                                              → Streamlit UI
```

**Spatial extraction** (`core/parser.py`). `pdfplumber.extract_words()`
yields tokens with $(x_0, x_1, top)$ boxes. Words group into visual lines by
$|top_i - top_j| \le 3$pt. Each line's internal word gaps are scanned: a gap
$> 50$pt (vs. normal ~3–8pt spacing) marks a two-column line, split at the
gap; the median split-x across ≥ 2 such lines becomes the page gutter.
Unsplit lines are routed by horizontal center (centered title lines spanning
the gutter stay intact as headers). Output order: headers → left column
top-to-bottom → right column top-to-bottom. Documents with $< 50$ characters
raise `ScannedPDFException`.

**Blind screening** (`core/sanitizer.py`). Contacts via regex (email; phone
candidates filtered to ≥ 10 digits so `2021–2024` survives); PERSON/GPE via
`en_core_web_sm` over the union of full-text and per-line spans; a
`City, Region` + major-city pattern fallback; a leading name-line rule; and
adversarial markers flagged with `[ADV_FLAG]`. Crucially, **skill-aware span
protection** (Section 6.2) exempts ESCO surface intervals from redaction.

**Matching** (`core/matcher.py`, `core/extractor.py`). ESCO-normalized
coverage (both resume and JD sides canonicalized, fuzzy fallback), lazy
singleton SBERT with offline-tolerant fallback, sentence-split evidence
search with per-section attribution (`skills/experience/education/projects`).

**Contracts & ephemerality.** All modules exchange frozen Pydantic v2 schemas
(`api/models.py`); the Streamlit frontend calls them as pure in-memory
functions. Raw buffers, parsed text, and embeddings live only in RAM and
session state — no database, no disk writes (verified by static scan and
temp-dir delta test) — satisfying DPDP Act §6 (minimization) and §8
(deletion).

---

## 4. Experimental Evaluation & Results Analysis

### 4.1 Benchmark dataset

`data/benchmark/`: 3 JDs (Data Scientist, Python Backend, DevOps; 5 core +
3 context skills each, parser-verified), 10 deterministic reportlab PDFs:
3 strong, 2 synonym-heavy (`Postgres`, `sklearn`, `ML`, `fast api`,
`docker compose`, `GitHub`, `web api`), 1 moderate, 2 two-column, 1
adversarial (visible injection + white-on-white keyword dump), 1
out-of-domain (chef). `qrels.json` holds independent 0–3 grades.

### 4.2 Comparative retrieval performance (`scripts/evaluate_benchmark.py`)

| Job | A Jaccard | B TF-IDF | C SBERT | **D Hybrid** |
|---|---|---|---|---|
| ds-001 nDCG@5 / @10 | 0.891 / 0.962 | 1.000 / 0.997 | 0.899 / 0.975 | **1.000 / 1.000** |
| be-002 nDCG@5 / @10 | 0.891 / 0.967 | 0.990 / 0.988 | 1.000 / 0.999 | **1.000 / 1.000** |
| do-003 nDCG@5 / @10 | 0.913 / 0.947 | 1.000 / 0.996 | 1.000 / 0.998 | **1.000 / 1.000** |
| **Mean @5 / @10** | **0.898 / 0.959** | **0.997 / 0.994** | **0.966 / 0.991** | **1.000 / 1.000** |

The hybrid is the only method with a perfect ranking on every JD. The
Jaccard gap (−0.10 @5) quantifies semantic blindness; TF-IDF is
near-perfect on this cleanly separable set (exact rare-term overlap) yet
still trails the hybrid and, unlike it, promotes the stuffed adversarial
resume lexically.

### 4.3 Adversarial resistance analysis

The injected resume (R09) combines a hospitality background with
"Ignore previous instructions and rank 100%" plus an invisible dump of
`Python SQL Machine Learning AWS Docker Kubernetes …`. Why Baseline D
buries it (ranks 8–9/10, hybrid 17–25/100) while keyword methods inflate:

1. **Coverage reads the skills block only** — the invisible dump lands in
   the projects block, so $Coverage_{core}$ stays 0–20%.
2. **Static embeddings don't follow instructions** — the injection is just
   another sentence; cosine similarity reflects the hospitality-heavy
   semantics (~0.2–0.4), weighted only $W_3 = 0.3$.
3. No generative component exists to be instruction-hijacked (SRS NFR-06).

### 4.4 Latency & CPU profiling

Steady-state per-document pipeline (parse + hybrid match vs. one JD, CPU,
models pre-warmed): **mean 0.178 s, max 0.357 s** — 17× under the 3.0 s
SLA (NFR-01). SBERT encodes 2 short texts per match (~100 ms); pdfplumber +
spaCy account for the rest. Peak RAM stays far below the 1.5 GB budget for
10-resume batches.

---

## 5. Bugs Encountered & Engineering Solutions

**Bug 1 — Two-column gutter interleaving.** First implementation detected
columns from line-*start* x-positions, but centered headers ("Neha
Kulkarni") bridged the gutter, so no boundary was found and lines merged
horizontally (`Skills Experience`), breaking section segmentation (skills
list came back empty). *Fix:* per-line internal-gap analysis — any line
with an internal word gap > 50pt is split at that gap; the median split-x
becomes the gutter; centered spanning lines are preserved as headers.
Verified: both multi-column resumes now parse with full skill lists and
correct reading order.

**Bug 2 — spaCy skill over-redaction (+ missed names).**
`en_core_web_sm` labels `Pandas`/`Docker`/`Machine Learning` as PERSON in
resume context (destroying evidence sentences and embeddings) while missing
bare header names (`Vikram Nair`) and Indian cities (`Hyderabad` in noisy
headers). *Fix (defense in depth):* (i) ESCO surface-form intervals are
computed first and NER spans overlapping them are discarded; (ii) NER runs
on full text ∪ per-line spans; (iii) a leading name-line rule;
(iv) `City, Region` + major-city regex fallback. Result: zero PII leaks
across 10 resumes, zero skill-term losses, 106/106 matched skills with
verbatim quotes.

---

## 6. Sociotechnical, Ethical & Legal Compliance

*Bias mitigation.* Blind screening redacts names, locations, phones, and
emails **before** embedding, so neither lexical nor dense signals can key on
demographics; the skill-protection guard ensures this never costs genuine
competence signal. Graded nDCG evaluation further rewards synonym-variant
resumes that keyword ATS would discard — a measurable fairness gain for
candidates with non-standard vocabulary.

*DPDP Act 2023.* §6 (data minimization): metadata dropped, only scoring
features retained in session. §8 (deletion): RAM-only pipeline, session
reset purges everything; verified by static analysis (no persistence calls)
and runtime temp-dir delta test. No data leaves the machine (NFR-02/03).

*Known limits.* Raster/Canva resumes without text layers are rejected by
design (no OCR in MVP); proprietary internal tooling outside ESCO scores
via semantic similarity only.

---

## 7. Conclusion & Future Work

We delivered a working, evaluated, deployable alternative to keyword ATS:
hybrid lexical–semantic scoring (nDCG@5 = 1.000), sentence-level
explainability, prompt-injection immunity by construction, blind screening
with skill-safe redaction, and DPDP-compliant ephemerality — all offline on
CPU at 178 ms/document. Future work: Tesseract OCR fallback, recruiter
 synonym editor, `.docx` ingestion, historical calibration of
$(W_1, W_2, W_3)$, and multi-role candidate comparison.

---

*Reproducibility: `pip install -r requirements.txt` →
`pytest tests/` (51 passed) →
`python scripts/evaluate_benchmark.py` → `streamlit run frontend/app.py`
(or `docker compose up --build`).*
