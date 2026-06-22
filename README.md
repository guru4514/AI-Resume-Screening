<div align="center">


### AI Resume Screening for Tech Hiring

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pytest](https://img.shields.io/badge/Pytest-Tested-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Active%20Development-2E7D32?style=for-the-badge)](#)

**Explainable candidate ranking with semantic skill matching, drag-drop uploads, and recruiter-ready shortlist workflows.**

[Quick Start](#quick-start) •
[Features](#features) •
[Demo](#demo) •
[API](#api-documentation) •
[Project Structure](#project-structure)

</div>

## Why This Project

Manual resume screening is slow, inconsistent, and hard to explain to hiring stakeholders.

TalentRank Studio solves this with a practical workflow:

- Upload a job description and candidate resumes.
- Extract candidate profile signals automatically.
- Score with transparent logic (required, must-have, nice-to-have, experience).
- Recover near-miss talent with semantic matching.
- Compare candidates side-by-side before final shortlist.

## Features

| Capability | Description |
|---|---|
| Explainable Ranking | Returns matched skills, missing skills, strengths, concerns, and semantic evidence. |
| Role-Aware Scoring | Supports `backend`, `frontend`, `data_ai`, `devops`, and `fullstack` profiles. |
| Resume Parsing | Ingests `PDF`, `DOCX`, and `TXT` files. |
| Auto Profile Extraction | Infers candidate name and years of experience from resume text. |
| Drag-and-Drop Upload | Recruiter dashboard supports direct file drop and parse preview. |
| Comparison View | Compare two candidates with score components and evidence. |

## Demo

### Demo Video Placeholder

[Watch TalentRank Demo](https://github.com/user-attachments/assets/64074d0d-1661-4a3d-850b-2c2e09d17435)`

### Screenshot Placeholder

Replace this placeholder image path with your final screenshot:

[TalentRank Dashboard](docs/media/demo-screenshot.png)

## Architecture

<img width="4190" height="2218" alt="architecture (2)" src="https://github.com/user-attachments/assets/29f8d5de-d5de-4f73-8fd2-61c7bf2f80e7" />


## Quick Start

### Windows (PowerShell)

```powershell
Set-Location "c:\Users\pytorch\Desktop\AI Resume Screening & Analysis System"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Open:

- Dashboard: `http://127.0.0.1:8001/`
- API Docs: `http://127.0.0.1:8001/docs`

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
PYTHONPATH=src uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## API Documentation

Base URL:

`http://127.0.0.1:8001`

### Health Check

- `GET /v1/health`

### Analyze Text Candidates

- `POST /v1/analyze`
- Input: JSON payload with job context and candidate resume text blocks.

### Analyze Uploaded Resumes

- `POST /v1/analyze-files`
- Input: multipart form with `resumes`.

### Preview Uploaded Resume Profiles

- `POST /v1/preview-files`
- Input: multipart form with `resumes`.
- Output: per-file parse status, candidate name, years, and detected skills.

## Example Request Payload

```json
{
  "job_title": "Backend Python Engineer",
  "job_description": "Looking for Python, FastAPI, Docker, PostgreSQL, and AWS experience.",
  "role_family": "backend",
  "must_have_skills": ["python", "fastapi"],
  "nice_to_have_skills": ["aws"],
  "candidates": [
    {
      "name": "Alex",
      "resume_text": "Built Python APIs with FastAPI and Docker, deployed on AWS with PostgreSQL.",
      "years_experience": 4
    }
  ]
}
```

## Demo Data Included

- Job description: `demo_assets/job_descriptions/backend_python_senior_jd.txt`
- Realistic varied-size PDF resumes: `demo_assets/resumes_pdf/`
- Demo guide: `demo_assets/DEMO_RUN_GUIDE.md`

## Project Structure

```text
src/app/
  api/routes.py                # FastAPI endpoints
  services/scoring.py          # Ranking and weighted scoring logic
  services/skill_taxonomy.py   # Skill extraction + semantic adjacency
  services/resume_parser.py    # Resume parsing + profile extraction
  web/static/                  # Dashboard frontend
  schemas.py                   # Request/response models
  main.py                      # App entrypoint

demo_assets/
  job_descriptions/
  resumes/
  resumes_pdf/

portfolio_assets/              # Upwork case-study/demo/proposal assets
scripts/                       # Setup and demo utility scripts
tests/                         # Unit and endpoint tests
```

## Testing

```powershell
Set-Location "c:\Users\pytorch\Desktop\AI Resume Screening & Analysis System"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "src"
pytest -q
```

## Troubleshooting

### Error: Failed to fetch

- Ensure backend is running.
- Open dashboard from the same origin (`http://127.0.0.1:8001/`).
- If using another frontend origin, set API base in browser console:

```javascript
localStorage.setItem("talentrank_api_base", "http://127.0.0.1:8001");
```

## Roadmap

- Export shortlist reports (CSV/PDF)
- Authentication and recruiter workspaces
- Project-level history and audit trail
- Configurable scoring templates per company
- ATS integration hooks

## Contact

For collaboration or freelance implementation:

- LinkedIn: `https://www.linkedin.com/in/prashantsingh-ai/`
- Email: `prashantsingha96@gmail.com`

---

If this repository helps you, consider starring it.
