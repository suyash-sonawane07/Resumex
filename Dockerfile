# syntax=docker/dockerfile:1
# ─── Stage 1: builder — install deps + pre-cache ML models ──────────────
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=0

WORKDIR /app

# System deps for tokenizers/HF hub downloads (curl + CA certs).
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Pre-cache Sentence-BERT so the runtime container is 100% offline.
ENV SBERT_MODEL_NAME=all-MiniLM-L6-v2 \
    HF_HOME=/root/.cache/huggingface
RUN PYTHONPATH=/install/lib/python3.10/site-packages \
    python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('all-MiniLM-L6-v2')"

# ─── Stage 2: runtime — slim, offline, headless ─────────────────────────
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    SBERT_MODEL_NAME=all-MiniLM-L6-v2 \
    SPACY_MODEL_NAME=en_core_web_sm \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ENABLE_CORS=false

WORKDIR /app

# curl is required by the docker-compose healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface
COPY --from=builder /usr/local/lib/python3.10/site-packages/en_core_web_sm \
    /usr/local/lib/python3.10/site-packages/en_core_web_sm

COPY api/ ./api/
COPY core/ ./core/
COPY frontend/ ./frontend/
COPY data/esco_skills.csv ./data/esco_skills.csv
COPY data/benchmark/ ./data/benchmark/
COPY requirements.txt .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", \
     "--server.headless=true", "--server.port=8501", "--server.address=0.0.0.0"]
