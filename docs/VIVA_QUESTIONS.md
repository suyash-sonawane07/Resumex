# Viva Voce Defense Guide — 25 Questions & Answers

## A. NLP & Embeddings

**1. Why `all-MiniLM-L6-v2` over standard BERT?**
Standard BERT emits token embeddings with no native sentence vector (the
`[CLS]` token is a classification artifact, not a similarity space) and
costs 110M+ parameters. MiniLM-L6-v2 is a 22M-parameter distilled model
producing 384-d sentence vectors explicitly trained for semantic similarity —
~5× faster on CPU (~100 ms/encode here), 80 MB cached, with negligible
quality loss at our text lengths. It is the standard price/performance
choice for local-first retrieval.

**2. How does SBERT's siamese architecture cut pairwise comparison from
$\mathcal{O}(n^2)$ to $\mathcal{O}(n)$?**
Cross-encoder BERT must jointly encode every $(resume, JD)$ pair: 10 resumes
× 3 JDs = 30 full transformer passes, and every new resume re-encodes
against all JDs. SBERT's siamese/shared-weight encoder produces
*independent* embeddings, so each document is encoded once
($\mathcal{O}(n)$) and all comparisons become cheap cosine dot products.
Adding resume #11 costs one encode, not 3 joint passes.

**3. Why cosine similarity rather than Euclidean distance?**
Embedding magnitudes vary with text length and term repetition; cosine
measures *direction* (semantic content), making a terse and a verbose resume
with the same meaning score identically. It is also length-invariant and
maps cleanly to $[0,1]$ after clamping, matching the hybrid formula's scale.

**4. What does the 384-dimensional vector actually capture?**
Distributional semantics from contrastive training on 1B+ sentence pairs:
paraphrases ("built backend services" / "owned Python services") land
nearby; unrelated domains (ML engineering vs. culinary work, measured
0.70 vs. 0.11 in our checks) separate. Dimensions are latent — individual
axes are uninterpretable, which is exactly why the lexical coverage term and
evidence matrix exist alongside it.

**5. When does the semantic term hurt, and how do you contain it?**
Dense similarity can reward fluent-but-irrelevant text. Containment:
$W_3 = 0.3$ caps its influence; coverage terms ($W_1 + W_2 = 0.7$) anchor the
score to verifiable skills; and the adversarial resume proves the bound —
semantic ~0.3–0.4 on stuffed text yields hybrid 17–25, never a promotion.

## B. Information Retrieval

**6. Why nDCG instead of Precision@K or MAP?**
Our judgments are *graded* (3 = strong, 2 = synonym-partial, 1 =
transferable, 0 = irrelevant). Precision@K and MAP binarize relevance,
treating a synonym match equal to a perfect one. nDCG's $2^{rel}-1$ gain
rewards highly relevant candidates exponentially and discounts by rank —
matching how recruiters actually scan shortlists top-down.

**7. Why does TF-IDF (0.997) beat pure SBERT (0.966) here?**
Technical hiring vocabulary is keyword-dense: rare exact terms (`Kubernetes`,
`Tableau`) dominate TF-IDF weights, and our corpus is cleanly separable, so
lexical overlap nearly suffices. SBERT trades some keyword precision for
paraphrase recall. The hybrid takes both — deterministic precision plus
semantic recall — hence 1.000.

**8. Isn't a perfect 1.000 nDCG suspicious?**
It is *expected*, not suspicious, given the design: 10 documents with
well-separated grades and a hybrid that resolves the only two ranking
threats (synonyms via ESCO, stuffing via block-scoped coverage). All three
JDs independently hit 1.000, and weaker baselines on identical data do not —
the metric discriminates; the hybrid simply clears this benchmark. Harder
corpora (paraphrased skills, borderline grades) would separate further.

**9. Why does Keyword Jaccard fail most on synonyms and stuffing?**
No normalization: `postgres ∩ sql = ∅`, so R04/R05 sink; no structure: the
white-text dump counts equally with the skills block, so R09 floats. Both
are structural, not tuning, failures — no threshold fixes them.

**10. How did you validate the metric implementation?**
Hand-computed DCG on a toy ranking, cross-checked `ndcg_at_k` against
`sklearn.metrics.ndcg_score` during development, and verified degenerate
cases (all-zero grades → 0.0, no division by zero via the $IDCG = 0$ guard).

## C. Parsing & Edge Cases

**11. Why did naive PyPDF-style extraction fail on two-column resumes?**
Character-stream extractors emit text in content order, interleaving columns
horizontally (`Skills Experience` on one line), which destroys section
headings. Our extractor sorts `pdfplumber` words by $(top, x_0)$, groups
visual lines ($|Δtop| ≤ 3$pt), splits lines with internal gaps > 50pt, takes
the median split-x as the gutter, and reads left-then-right — verified by
the spatial-isolation test and R07/R08 parsing fully.

**12. How are white-on-white / invisible texts neutralized?**
`pdfplumber` discards color/opacity metadata, so hidden text arrives as plain
strings — it *cannot* execute, only pollute. Pollution is contained: (a)
markers (`ignore previous instructions`, `rank 100%`, …) are flagged
`[ADV_FLAG]` by `detect_adversarial_markers`; (b) dumped keywords land
outside the skills block, so coverage ignores them; (c) scoring is
deterministic + static-embedding, with no instruction-following component.

**13. How are scanned/image PDFs handled?**
Character count < 50 after extraction → `ScannedPDFException` with an
actionable message ("re-export from Word/Google Docs"), surfaced as a UI
banner. OCR is explicitly deferred (CPU cost) per the SRS.

**14. How does section segmentation work?**
Whole-line regex over alias sets (skills/technical skills/…, experience/work
history/…, education/…, projects/…), longest-alias-first; heading-less text
falls back to the experience block. Verified per-resume in acceptance.

## D. AI Safety & Adversarial Attacks

**15. Why are static embeddings structurally immune to prompt injection vs.
GPT-4/Gemini?**
Generative LLMs are instruction-followers: injected text enters the same
context window as system instructions and can redirect behavior. Our SBERT
call is a *pure function* text → vector with no instruction channel, no
tool use, no hidden state — "rank 100%" shifts an embedding slightly at
most. There is Between prompt and score no agent that *obeys*.

**16. Could keyword stuffing still inflate the hybrid?**
Only the semantic term ($W_3 = 0.3$), bounded: R09's dump sits in projects
text, lifting cosine modestly. Coverage — 70% of the score — requires
skills-block terms, which stuffing cannot reach without being visible (and
thus flaggable). Measured: hybrid 17–25 vs. Jaccard-inflated ranks.

**17. What attacks remain out of scope?**
Visible lying (fake experience claims — needs background verification, not
NLP), rasterized text (rejected, no OCR), and corpus-poisoning of the ESCO
file itself (mitigated by freezing `esco_skills.csv` under review).

## E. Fairness & Privacy

**18. How do you stop spaCy redacting `Pandas`/`Docker` as PERSON?**
Skill-aware span protection: all ESCO surface intervals are computed first
(word-boundary, case-insensitive), and any PERSON/GPE span overlapping them
is discarded before replacement. Result: zero skill-term losses, 106/106
evidence quotes intact.

**19. …and still catch real PII the small model misses?**
Layered fallback: full-text ∪ per-line NER spans, a leading name-line rule
(`Vikram Nair`), `City, Region` + major-city patterns (`Hyderabad, India`),
and digit-count-gated phone regex (≥10 digits, so `2021–2024` survives).
Acceptance: zero name/location/contact leaks across 10 resumes.

**20. How does blind screening reduce demographic bias?**
Redaction precedes *both* signals — coverage tokens and embeddings — so
names, locations, and contact artifacts cannot influence any score. Plus,
synonym normalization removes the vocabulary bias that punishes
non-standard phrasing. Fairness is architectural, not aspirational.

**21. Prove DPDP Act §8 (deletion) compliance.**
The pipeline has zero persistence primitives — verified by static grep for
`open(w)`, `to_csv/json/pickle`, `write_text`, `.save()` across
`core/`, `frontend/`, `api/` (clean) plus a runtime temp-dir delta test
(no files created for 10 parses). Session reset drops all state; nothing
can be recovered because nothing was written.

## F. Architecture & System Design

**22. Why decouple Streamlit from core via Pydantic contracts?**
`api/models.py` is a frozen, versioned interface: Member 1 produces
`ParsedResume`, Member 2 consumes it and produces `MatchResult`, Member 3
renders. Teams developed in parallel against mocks; schema violations fail
at validation time with clear errors instead of silent UI corruption. The
zero-touch schema rule prevented all integration drift.

**23. How is cold-start model loading handled?**
Lazy singletons for SBERT and spaCy (first call pays, rest reuse);
benchmark warmup excludes load from latency figures; the Dockerfile
pre-caches both models at build time so first *request* is already warm and
the container runs offline.

**24. Why Streamlit + in-process calls instead of FastAPI microservices?**
NFR-01 (≤3 s) and NFR-04 (<1.5 GB): in-process calls avoid serialization and
a second model copy in memory. FastAPI (`api/main.py`) ships as an optional
decoupled router if placement-cell deployment later needs it.

**25. What is the single strongest limitation, honestly?**
Corpus difficulty: our benchmark is cleanly separable, so 1.000 nDCG
demonstrates correctness, not SOTA dominance on noisy real-world data. Next
steps that would stress it: paraphrased skill mentions without ESCO
coverage, scanned resumes (needs OCR), and recruiter-weighted calibration
of $(W_1, W_2, W_3)$ on historical outcomes.
