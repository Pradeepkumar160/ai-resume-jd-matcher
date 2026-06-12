# 🤖 AI Resume ↔ JD Matcher

A production-grade NLP application that compares resumes against job descriptions using semantic similarity, skill extraction, and gap analysis.

## ✨ Features  
 
| Feature | Details |
|---|---|
| Resume Parsing | PDF and DOCX support |
| Semantic Matching | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Skill Extraction | 80+ skills across languages, frameworks, cloud, ML |
| Gap Analysis | Matched vs missing skills with visual breakdown |
| Recommendations | Actionable, skill-specific improvement tips |
| Match History | Stored in PostgreSQL, viewable in dashboard |
| Interactive UI | Streamlit with Plotly gauge + pie charts |
| REST API | FastAPI with auto-generated `/docs` |
| Docker | One-command deployment with Docker Compose |

## 🚀 Quick Start (Docker — Recommended)

### Windows (PowerShell)

```powershell
# Right-click run_app.ps1 → "Run with PowerShell"
# OR in PowerShell terminal:
.\run_app.ps1
```

> **Note:** The first run downloads a ~90MB NLP model and builds images — allow 5–10 minutes.

### Any platform

```bash
docker compose up --build
```

## 🌐 Access

| Service | URL |
|---|---|
| Streamlit Dashboard | http://localhost:8501 |
| FastAPI Interactive Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

## 🛑 Stop the Application

```bash
docker compose down
# To also remove the database volume:
docker compose down -v
```   

## 🏗️ Project Structure

```
ai-resume-jd-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, DB init, startup
│   │   ├── config.py         # Environment settings (pydantic-settings)
│   │   ├── database.py       # SQLAlchemy engine & session
│   │   ├── models.py         # DB model (MatchResult)
│   │   ├── schemas.py        # Pydantic response schemas
│   │   ├── routes/
│   │   │   ├── match_routes.py   # POST /api/match, GET /api/history
│   │   │   └── health_routes.py  # GET /health
│   │   └── utils/
│   │       ├── parser.py         # PDF/DOCX text extraction
│   │       ├── extractor.py      # Skill keyword extraction
│   │       ├── embeddings.py     # Sentence-Transformers wrapper
│   │       ├── matcher.py        # Cosine similarity calculation
│   │       ├── scorer.py         # Skill gap analysis
│   │       └── recommendations.py # Actionable suggestions
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── streamlit_app.py      # Full Streamlit UI
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── run_app.ps1               # One-click Windows launcher
└── README.md
```

## 🔧 API Reference

### `POST /api/match`
Upload a resume and get an analysis.

**Form fields:**
- `resume` (file) — PDF or DOCX
- `job_description` (string) — full JD text
- `candidate_name` (string, optional)

**Response:**
```json
{
  "score": 72.5,
  "matched_skills": ["python", "docker", "fastapi"],
  "missing_skills": ["kubernetes", "aws"],
  "recommendations": ["📌 Kubernetes: Study Kubernetes with Minikube..."]
}
```

### `GET /api/history`
Returns recent match results from the database.

### `GET /health`
Returns API and database status.

## 🔑 Environment Variables (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:password@db:5432/resume_matcher` | PostgreSQL connection string |
| `SECRET_KEY` | `mysupersecretkey...` | JWT signing key — **change in production!** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token TTL |

## 🐛 Troubleshooting   

| Problem | Solution |
|---|---|
| Backend not starting | Run `docker compose logs backend` to check model download progress |
| DB connection error | Run `docker compose logs db` — wait for `ready to accept connections` |
| Port 8501 already in use | Stop other Streamlit instances or change port in `docker-compose.yml` |
| `docker compose` not found | Update Docker Desktop — `compose` is bundled in recent versions |
| Score is always 0 | Resume text could not be extracted — check the file isn't password-protected |
