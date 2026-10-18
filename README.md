# 📄 AI-Powered Resume Intelligence and Job Matching System

An explainable, privacy-compliant resume screening system that combines deterministic skill coverage with dense semantic similarity to produce transparent, auditable candidate rankings.

> **Status:** MVP Development — Module placeholders are active. Core algorithms under development.

---

## 🏗️ Project Architecture

```
NLP_Mini_Project/
├── api/                          # Shared contracts & optional REST API
│   ├── __init__.py
│   ├── models.py                 # 🔒 FROZEN — Pydantic data contracts
│   └── main.py                   # FastAPI REST interface (Member 3)
├── core/                         # Backend processing modules
│   ├── __init__.py
│   ├── parser.py                 # PDF ingestion & section segmentation (Member 1)
│   ├── sanitizer.py              # PII redaction & adversarial defense (Member 1)
│   ├── extractor.py              # JD parsing & ESCO normalization (Member 2)
│   └── matcher.py                # Hybrid scoring & explainability (Member 2)
├── frontend/                     # Streamlit UI
│   ├── __init__.py
│   ├── app.py                    # Main application entry point (Member 3)
│   └── components.py             # Plotly charts & display widgets (Member 3)
├── data/
│   └── esco_skills.csv           # ESCO skill taxonomy (Member 2)
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures & mock data
│   ├── test_parser.py            # Member 1 unit tests
│   ├── test_matcher.py           # Member 2 unit tests
│   └── test_ui_integration.py    # Member 3 integration tests
├── .gitignore
├── .env.example                  # Sample environment configuration
├── requirements.txt              # Python dependencies
├── MVP_REQUIREMENTS.md           # Full requirements specification
└── README.md                     # This file
```

---

## 🚀 Quick Start (pick one)

| I want to... | Command |
|---|---|
| **Use the app** (dashboard) | `./run.sh` → opens at http://localhost:8501 |
| **See it work in 60 sec** (no browser) | `./run.sh demo` |
| **Prove it to my professor** (scores + speed) | `./run.sh benchmark` |
| **Check everything still works** | `./run.sh test` |

> First time only: `pip install -r requirements.txt` then
> `python -m spacy download en_core_web_sm`.

### Manual setup (if you prefer step-by-step)

### Prerequisites
- **Python 3.10+**
- **pip** (package manager)
- ~500 MB disk space (for ML models on first run)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "NLP Mini Project"
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Run the Application
```bash
streamlit run frontend/app.py
```
The dashboard opens at **http://localhost:8501**.

### 6. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_parser.py -v       # Member 1 tests
pytest tests/test_matcher.py -v      # Member 2 tests
pytest tests/test_ui_integration.py -v  # Member 3 tests

# Run with coverage
pytest tests/ --cov=core --cov=api --cov=frontend --cov-report=term-missing
```

### 🎓 Explain it to your professor in 60 seconds

> "A recruiter pastes a job description and uploads resumes. The system
> (1) extracts text keeping two-column layouts in reading order,
> (2) redacts names and contacts **before** scoring, so hiring is blind,
> (3) maps synonyms like PostgreSQL → SQL through a skill dictionary, then
> (4) scores each resume with one transparent formula:
> **Score = 0.5 × mandatory-skill coverage + 0.2 × preferred-skill coverage + 0.3 × semantic similarity.**
> Every matched skill shows the **exact resume sentence** it came from, and
> every missing skill is flagged as a gap. An injected resume saying
> *'rank me 100%'* still scores ~22/100, because static embeddings can't
> follow instructions. All in memory, no cloud, ~178 ms per resume."

Full 5-minute walkthrough: [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md).
Expected viva questions: [`docs/VIVA_QUESTIONS.md`](docs/VIVA_QUESTIONS.md).

---

## 👥 Team Responsibilities

### File Ownership Matrix

| Member | Owned Files | Scope |
|--------|------------|-------|
| **Member 1** | `core/parser.py`, `core/sanitizer.py`, `tests/test_parser.py` | PDF parsing, text extraction, PII redaction, adversarial defense |
| **Member 2** | `core/extractor.py`, `core/matcher.py`, `data/esco_skills.csv`, `tests/test_matcher.py` | JD parsing, ESCO normalization, SBERT matching, hybrid scoring, explainability |
| **Member 3** | `frontend/app.py`, `frontend/components.py`, `api/main.py`, `tests/test_ui_integration.py` | Streamlit UI, Plotly charts, API routing, integration orchestration |

### 🔒 Shared / Frozen Files (Require All-Member Approval)
- `api/models.py` — Pydantic data contracts
- `tests/conftest.py` — Shared test fixtures
- `requirements.txt` — Project dependencies
- `README.md` — Project documentation

> ⚠️ **Rule:** Never modify `api/models.py` on a feature branch. Schema changes require consensus and must be committed to `develop` directly.

---

## 🌿 Git Branching Convention

```
main                    ← Production-ready release
└── develop             ← Integration staging branch
    ├── feature/m1-resume-parser      ← Member 1 work
    ├── feature/m2-matching-engine    ← Member 2 work
    └── feature/m3-ui-integration     ← Member 3 work
```

### Branch Rules
1. Create your feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/m1-resume-parser   # Your branch
   ```
2. Only modify files you own (see ownership matrix above).
3. Run your module's tests before pushing:
   ```bash
   pytest tests/test_parser.py -v   # Member 1
   pytest tests/test_matcher.py -v  # Member 2
   pytest tests/test_ui_integration.py -v  # Member 3
   ```
4. Open a Pull Request to `develop` — requires at least 1 peer review.
5. After merge to `develop`, Member 3 runs the full integration test suite.

---

## 🔌 Module Contracts

All inter-module communication uses Pydantic schemas from `api/models.py`.

### Data Flow
```
[PDF bytes] → parse_resume() → ParsedResume → match_resume_to_job() → MatchResult → UI
```

### Key Interfaces

**Member 1 exports:**
```python
# core/parser.py
def parse_resume(file_bytes: bytes, filename: str, redact_pii: bool = True) -> ParsedResume
```

**Member 2 exports:**
```python
# core/extractor.py
def parse_job_description(jd_text: str, job_id: str, title: str) -> JobProfile

# core/matcher.py
def match_resume_to_job(resume: ParsedResume, job: JobProfile, weights: ScoringWeights) -> MatchResult
```

**Member 3 orchestrates:**
```python
# frontend/app.py
parsed = parse_resume(file_bytes, filename)
result = match_resume_to_job(parsed, job_profile, weights)
render_leaderboard([result])
```

### Custom Exceptions (defined in `api/models.py`)
| Exception | Trigger | Owner |
|-----------|---------|-------|
| `InvalidFileException` | Wrong format, too large, empty | Member 1 |
| `ScannedPDFException` | Image-only PDF (< 50 chars extracted) | Member 1 |
| `EmptyResumeException` | No usable text content | Member 1 |

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and adjust if needed:
```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `SBERT_MODEL_NAME` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `SPACY_MODEL_NAME` | `en_core_web_sm` | spaCy NER model |
| `MAX_FILE_SIZE_BYTES` | `5242880` (5MB) | Max upload size per file |
| `MAX_BATCH_SIZE` | `10` | Max resumes per batch |

---

## 🧪 Testing Strategy

### Test Isolation
Each member has an independent test file that can run without other modules being complete:
- Tests use mock data from `tests/conftest.py`
- Placeholder implementations return safe defaults
- No test depends on external services or network access

### Running Tests
```bash
# Quick smoke test (all modules import correctly)
python -c "from api.models import *; from core.parser import parse_resume; from core.matcher import match_resume_to_job; print('All imports OK')"

# Full test suite
pytest tests/ -v --tb=short
```

---

## 📋 Merge Checklist

Before merging your feature branch:

- [ ] All your unit tests pass (`pytest tests/test_<your_module>.py -v`)
- [ ] You only modified files you own
- [ ] No changes to `api/models.py` without team approval
- [ ] No new dependencies added without updating `requirements.txt`
- [ ] Code has docstrings and follows existing conventions
- [ ] No hardcoded file paths or environment-specific assumptions

---

## 📜 License

Internal project — NLP Mini Project. Not for distribution.
