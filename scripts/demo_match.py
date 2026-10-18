"""demo_match.py — the simplest possible end-to-end demo.

Picks one sample resume + one sample job, runs the FULL pipeline
(parse -> match -> explain), and prints the result in plain English
suitable for explaining to a professor in ~60 seconds.

Usage:
    python scripts/demo_match.py                  # default: synonym resume vs Data Scientist JD
    python scripts/demo_match.py --resume resume_09_adversarial.pdf
    python scripts/demo_match.py --job be-002
    python scripts/demo_match.py --list            # show available resumes + jobs
"""
import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from api.models import ScoringWeights
from core.extractor import parse_job_description
from core.matcher import match_resume_to_job
from core.parser import parse_resume

BENCH = os.path.join(REPO_ROOT, "data", "benchmark")
RESUME_DIR = os.path.join(BENCH, "resumes")


def load_jobs():
    with open(os.path.join(BENCH, "sample_jds.json")) as f:
        return json.load(f)["jobs"]


def main():
    jobs = load_jobs()
    parser = argparse.ArgumentParser(description="Simple end-to-end resume match demo.")
    parser.add_argument("--resume", default="resume_04_ds_synonym.pdf")
    parser.add_argument("--job", default="ds-001")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        print("Resumes:")
        for f in sorted(os.listdir(RESUME_DIR)):
            print(f"  {f}")
        print("Jobs:")
        for j in jobs:
            print(f"  {j['job_id']} — {j['title']}")
        return 0

    entry = next((j for j in jobs if j["job_id"] == args.job), jobs[0])
    resume_path = os.path.join(RESUME_DIR, args.resume)
    if not os.path.exists(resume_path):
        print(f"Resume not found: {resume_path}")
        return 1

    with open(resume_path, "rb") as f:
        file_bytes = f.read()

    # --- THE ENTIRE PIPELINE: 3 function calls ---
    parsed = parse_resume(file_bytes, args.resume)          # 1. PDF -> clean text + sections
    job = parse_job_description(entry["raw_jd_text"],      # 2. JD text -> core vs preferred skills
                                job_id=entry["job_id"], title=entry["title"])
    weights = ScoringWeights()                             #    defaults: core 0.5 / preferred 0.2 / semantic 0.3
    result = match_resume_to_job(parsed, job, weights)     # 3. score + explain

    # --- Professor-friendly explanation ---
    print("=" * 64)
    print(f"RESUME: {args.resume}")
    print(f"ROLE:   {job.title} ({job.job_id})")
    print("=" * 64)
    print(f"\nFINAL SCORE: {result.hybrid_score:.1f}%  "
          f"(Core {result.core_coverage_pct:.0f}% | "
          f"Preferred {result.context_coverage_pct:.0f}% | "
          f"Semantic {result.semantic_similarity_pct:.0f}%)")
    print(f"\nFormula: Score = 0.5 x Core + 0.2 x Preferred + 0.3 x Semantic")
    print(f"       = 0.5 x {result.core_coverage_pct/100:.2f} + "
          f"0.2 x {result.context_coverage_pct/100:.2f} + "
          f"0.3 x {result.semantic_similarity_pct/100:.2f}")
    print("\n--- WHY this score? (every point is backed by a quote) ---")
    for e in result.explainability.core_evidence:
        if e.matched:
            print(f"  [MATCH]   {e.skill}: found as '{e.matched_term}'")
            print(f"            \"{e.source_sentence}\"")
        else:
            print(f"  [MISSING] {e.skill}: not found anywhere in the resume")
    for e in result.explainability.context_evidence:
        mark = "[match]" if e.matched else "[gap]  "
        print(f"  {mark} (preferred) {e.skill}" +
              (f": '{e.matched_term}'" if e.matched else ": missing"))
    if result.explainability.core_missing_skills:
        print(f"\nSKILL GAPS to tell the candidate: "
              f"{', '.join(result.explainability.core_missing_skills)}")
    else:
        print("\nNo gaps — candidate covers every mandatory skill.")
    print(f"\nTime: {result.processing_time_ms:.0f} ms | "
          f"Privacy: names/contacts redacted before scoring "
          f"({'ON' if parsed.is_blind_screened else 'OFF'})")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
