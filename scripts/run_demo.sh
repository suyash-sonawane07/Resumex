#!/usr/bin/env bash
# run_demo.sh — one-command local demo: env check → tests → benchmark → app.
# Usage: ./scripts/run_demo.sh
set -euo pipefail

cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"

echo "==> 1/4 Python environment"
$PY --version
$PY -c "import streamlit, pdfplumber, spacy, sentence_transformers, sklearn" \
  || { echo "Missing deps. Run: pip install -r requirements.txt"; exit 1; }
$PY -c "import spacy; spacy.load('en_core_web_sm')" \
  || { echo "spaCy model missing. Run: python -m spacy download en_core_web_sm"; exit 1; }
echo "Dependencies OK."

echo "==> 2/4 Test suite (51 tests)"
$PY -m pytest tests/ -q

echo "==> 3/4 Benchmark evaluation (nDCG + latency SLA)"
$PY scripts/evaluate_benchmark.py

echo "==> 4/4 Launching Streamlit app on http://localhost:8501"
exec streamlit run frontend/app.py
