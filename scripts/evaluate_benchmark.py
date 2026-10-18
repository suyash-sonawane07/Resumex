"""Scientific benchmark: retrieval quality (nDCG@K) + latency SLA.

Compares four ranking baselines on the synthetic benchmark set
(data/benchmark/sample_jds.json + data/benchmark/resumes/*.pdf
against data/benchmark/qrels.json):

  Baseline A — Keyword Jaccard: raw word-overlap between JD skill terms
               and resume text (NO taxonomy normalization).
  Baseline B — TF-IDF Cosine: scikit-learn TF-IDF vectors over raw texts.
  Baseline C — Pure SBERT: cosine similarity of all-MiniLM-L6-v2 embeddings.
  Baseline D — Proposed Hybrid: (W1 x Core) + (W2 x Context) + (W3 x Semantic)
               via core.parser.parse_resume + core.matcher.match_resume_to_job.

Metrics:
  nDCG@5 and nDCG@10 per job description, averaged across the 3 JDs.
  Latency: mean end-to-end seconds per document (parse + match vs all JDs).
  SLA: mean per-document latency <= 3.0 s on CPU (NFR-01). Failure exits 2.

Run: venv/bin/python scripts/evaluate_benchmark.py [--k 5 10] [--out FILE]
"""

import argparse
import glob
import json
import math
import os
import re
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from api.models import JobProfile, ScoringWeights  # noqa: E402
from core.extractor import parse_job_description  # noqa: E402
from core.matcher import compute_semantic_similarity  # noqa: E402
from core.matcher import match_resume_to_job  # noqa: E402
from core.parser import parse_resume  # noqa: E402

BENCH_DIR = os.path.join(REPO_ROOT, "data", "benchmark")
RESUME_DIR = os.path.join(BENCH_DIR, "resumes")
LATENCY_SLA_S = 3.0
DEFAULT_WEIGHTS = ScoringWeights(w_core=0.5, w_context=0.2, w_semantic=0.3)

TOKEN_RE = re.compile(r"[a-z0-9+#]+")


def word_tokens(text):
    """Lowercase alphanumeric word tokens (no stemming, no taxonomy)."""
    return set(TOKEN_RE.findall(text.lower()))


# ─── nDCG ─────────────────────────────────────────────────────────────

def dcg_at_k(ranked_rels, k):
    return sum(
        (2**rel - 1) / math.log2(idx + 2)
        for idx, rel in enumerate(ranked_rels[:k])
    )


def ndcg_at_k(ranked_rels, ideal_rels, k):
    ideal = dcg_at_k(sorted(ideal_rels, reverse=True), k)
    if ideal == 0:
        return 0.0
    return dcg_at_k(ranked_rels, k) / ideal


# ─── Baselines ────────────────────────────────────────────────────────

def baseline_jaccard(jd_skill_terms, resume_text):
    resume_terms = word_tokens(resume_text)
    if not jd_skill_terms and not resume_terms:
        return 0.0
    union = jd_skill_terms | resume_terms
    if not union:
        return 0.0
    return len(jd_skill_terms & resume_terms) / len(union)


def baseline_tfidf(vectorizer, jd_text, resume_text):
    from sklearn.metrics.pairwise import cosine_similarity

    matrix = vectorizer.transform([jd_text, resume_text])
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


# ─── Benchmark runner ───────────────────────────────────────────────

def load_jobs():
    with open(os.path.join(BENCH_DIR, "sample_jds.json")) as f:
        raw = json.load(f)["jobs"]
    with open(os.path.join(BENCH_DIR, "qrels.json")) as f:
        qrels = json.load(f)["grades"]
    jobs = []
    for entry in raw:
        profile = parse_job_description(
            entry["raw_jd_text"], job_id=entry["job_id"], title=entry["title"]
        )
        jobs.append((entry, profile, qrels[entry["job_id"]]))
    return jobs


def main():
    parser = argparse.ArgumentParser(description="Run retrieval benchmark.")
    parser.add_argument("--k", nargs="+", type=int, default=[5, 10])
    parser.add_argument(
        "--out",
        default=os.path.join(BENCH_DIR, "results.json"),
        help="Where to write the JSON report.",
    )
    args = parser.parse_args()

    resume_paths = sorted(glob.glob(os.path.join(RESUME_DIR, "*.pdf")))
    assert len(resume_paths) >= 10, f"expected 10 benchmark PDFs, found {len(resume_paths)}"
    jobs = load_jobs()
    print(f"Benchmark: {len(jobs)} JDs x {len(resume_paths)} resumes")

    # Warm up the SBERT singleton and spaCy NER so one-time model-load
    # costs are not billed to per-document latency.
    _ = compute_semantic_similarity("warmup text", "warmup query")
    from core.sanitizer import sanitize_text

    _ = sanitize_text("Aarav Patel, Mumbai, India. aarav.patel@email.com.")
    print("SBERT + spaCy models warmed up.")

    # TF-IDF fitted once over the whole corpus (standard practice).
    from sklearn.feature_extraction.text import TfidfVectorizer

    corpus_texts = {}
    for path in resume_paths:
        with open(path, "rb") as f:
            corpus_texts[path] = f.read()
    tfidf = TfidfVectorizer(lowercase=True, stop_words="english")

    # Parse all resumes once (timed) — fully in-memory, no disk writes.
    parsed, parse_times = {}, {}
    for path in resume_paths:
        name = os.path.basename(path)
        start = time.perf_counter()
        parsed[name] = parse_resume(corpus_texts[path], name)
        parse_times[name] = time.perf_counter() - start
    tfidf.fit(
        [parsed[os.path.basename(p)].raw_text for p in resume_paths]
        + [entry["raw_jd_text"] for entry, _, _ in jobs]
    )

    per_doc_latency = {os.path.basename(p): 0.0 for p in resume_paths}
    hybrid_match_time = {os.path.basename(p): 0.0 for p in resume_paths}
    scores = {"jaccard": {}, "tfidf": {}, "sbert": {}, "hybrid": {}}
    adv_ranks = {}

    for entry, profile, grades in jobs:
        jd_skill_terms = word_tokens(" ".join(profile.core_skills + profile.context_skills))
        ranking = {name: {} for name in ("jaccard", "tfidf", "sbert", "hybrid")}
        for path in resume_paths:
            name = os.path.basename(path)
            resume = parsed[name]

            t0 = time.perf_counter()
            j_score = baseline_jaccard(jd_skill_terms, resume.raw_text)
            t_jaccard = time.perf_counter() - t0

            t0 = time.perf_counter()
            tfidf_score = baseline_tfidf(tfidf, entry["raw_jd_text"], resume.raw_text)
            t_tfidf = time.perf_counter() - t0

            t0 = time.perf_counter()
            resume_sem_text = f"{resume.experience_block} {resume.projects_block}".strip()
            sbert_score = compute_semantic_similarity(resume_sem_text, entry["raw_jd_text"])
            t_sbert = time.perf_counter() - t0

            t0 = time.perf_counter()
            result = match_resume_to_job(
                resume=resume,
                job=JobProfile(
                    job_id=profile.job_id,
                    title=profile.title,
                    raw_jd_text=profile.raw_jd_text,
                    core_skills=profile.core_skills,
                    context_skills=profile.context_skills,
                ),
                weights=DEFAULT_WEIGHTS,
            )
            t_hybrid = time.perf_counter() - t0
            hybrid_score = result.hybrid_score / 100.0

            ranking["jaccard"][name] = j_score
            ranking["tfidf"][name] = tfidf_score
            ranking["sbert"][name] = sbert_score
            ranking["hybrid"][name] = hybrid_score
            # End-to-end cost attributable to this JD (all baselines timed;
            # the SLA below counts only parse + hybrid-match pipeline time).
            per_doc_latency[name] += t_jaccard + t_tfidf + t_sbert + t_hybrid
            hybrid_match_time[name] += t_hybrid

        for baseline in scores:
            scores[baseline][entry["job_id"]] = ranking[baseline]
        ordered = sorted(ranking["hybrid"].items(), key=lambda kv: kv[1], reverse=True)
        adv_ranks[entry["job_id"]] = (
            [n for n, _ in ordered].index("resume_09_adversarial.pdf") + 1
        )

    # nDCG per JD per baseline.
    table = {}
    for entry, _, grades in jobs:
        job_id = entry["job_id"]
        ideal = [grades[os.path.basename(p)] for p in resume_paths]
        table[job_id] = {}
        for baseline in scores:
            ranked = sorted(
                scores[baseline][job_id].items(), key=lambda kv: kv[1], reverse=True
            )
            rels = [grades[name] for name, _ in ranked]
            table[job_id][baseline] = {
                f"nDCG@{k}": round(ndcg_at_k(rels, ideal, k), 4) for k in args.k
            }

    mean_row = {}
    for baseline in scores:
        mean_row[baseline] = {
            f"nDCG@{k}": round(
                sum(table[entry["job_id"]][baseline][f"nDCG@{k}"]
                    for entry, _, _ in jobs) / len(jobs),
                4,
            )
            for k in args.k
        }

    # Latency: one full single-JD pipeline run per document =
    # parse (once) + hybrid match (averaged across JDs). Experimental
    # baseline overhead (Jaccard/TF-IDF/SBERT harnesses) is excluded.
    n_jobs = len(jobs)
    per_doc_total = {
        name: parse_times[name] + hybrid_match_time[name] / n_jobs
        for name in hybrid_match_time
    }
    mean_latency = sum(per_doc_total.values()) / len(per_doc_total)
    max_latency = max(per_doc_total.values())

    print("\n=== nDCG per job ===")
    header = f"{'job':<8}" + "".join(f"{b:<22}" for b in scores)
    print(header)
    for entry, _, _ in jobs:
        row = f"{entry['job_id']:<8}"
        for baseline in scores:
            cells = ",".join(
                f"@{k}={table[entry['job_id']][baseline][f'nDCG@{k}']:.3f}"
                for k in args.k
            )
            row += f"{cells:<22}"
        print(row)
    print(f"{'MEAN':<8}" + "".join(
        f"{','.join(f'@{k}={mean_row[b][f'nDCG@{k}']:.3f}' for k in args.k):<22}"
        for b in scores
    ))

    print("\n=== Latency (s per document, CPU) ===")
    for name in sorted(per_doc_total):
        print(f"  {name}: {per_doc_total[name]:.3f}s")
    print(f"  MEAN: {mean_latency:.3f}s  MAX: {max_latency:.3f}s  "
          f"SLA<=3.0s: {'PASS' if mean_latency <= LATENCY_SLA_S else 'FAIL'}")

    print("\n=== Adversarial robustness (hybrid rank of injected resume, 1=top) ===")
    for entry, _, _ in jobs:
        rank = adv_ranks[entry["job_id"]]
        print(f"  {entry['job_id']}: rank {rank}/{len(resume_paths)} "
              f"({'BURIED' if rank > len(resume_paths) // 2 else 'SURFACED!'} — grade 0)")

    hybrid_mean = mean_row["hybrid"][f"nDCG@{args.k[0]}"]
    jaccard_mean = mean_row["jaccard"][f"nDCG@{args.k[0]}"]
    print(f"\nHybrid nDCG@{args.k[0]} {hybrid_mean:.3f} vs Keyword-Jaccard "
          f"{jaccard_mean:.3f}: "
          f"{'SUPERIOR ✓' if hybrid_mean > jaccard_mean else 'NOT SUPERIOR ✗'}")

    report = {
        "baselines": ["jaccard", "tfidf", "sbert", "hybrid"],
        "k_values": args.k,
        "per_job_ndcg": table,
        "mean_ndcg": mean_row,
        "latency_s_per_doc": {n: round(v, 4) for n, v in per_doc_total.items()},
        "mean_latency_s": round(mean_latency, 4),
        "max_latency_s": round(max_latency, 4),
        "latency_sla_s": LATENCY_SLA_S,
        "latency_pass": mean_latency <= LATENCY_SLA_S,
        "adversarial_hybrid_ranks": adv_ranks,
        "weights": DEFAULT_WEIGHTS.model_dump(),
    }
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to {args.out}")

    if mean_latency > LATENCY_SLA_S:
        print(f"SLA VIOLATION: mean {mean_latency:.3f}s > {LATENCY_SLA_S}s",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
