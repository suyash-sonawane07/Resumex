#!/usr/bin/env bash
# run.sh — simplest way to run the app. From the project folder:
#   ./run.sh            → launches the dashboard at http://localhost:8501
#   ./run.sh demo       → 60-second terminal demo (no browser needed)
#   ./run.sh test       → runs all 51 tests
#   ./run.sh benchmark  → nDCG + latency proof for your professor
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-app}" in
  demo)
    python3 scripts/demo_match.py "${@:2}" ;;
  test)
    python3 -m pytest tests/ -q ;;
  benchmark)
    python3 scripts/evaluate_benchmark.py ;;
  api)
    python3 -m uvicorn api.main:app --port 8000 ;;
  app|*)
    streamlit run frontend/app.py ;;
esac
