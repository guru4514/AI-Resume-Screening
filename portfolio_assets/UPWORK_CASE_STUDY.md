# TalentRank Studio - AI Resume Screening for Tech Hiring

## Project Summary

TalentRank Studio is an AI-powered resume screening and analysis system focused on technical roles. It helps recruiters and hiring managers shortlist candidates faster with explainable scoring, semantic skill matching, and profile extraction from uploaded resumes.

## Problem

Tech hiring teams often spend too much time manually reviewing resumes. Traditional keyword filters miss strong candidates with adjacent skills, while black-box AI tools provide little explanation for rankings.

## Solution

I built a recruiter-facing system that:

- Supports JD-driven candidate evaluation for backend, frontend, data/AI, DevOps, and fullstack roles.
- Parses PDF, DOCX, and TXT resumes directly.
- Auto-extracts candidate name and years of experience from resume content.
- Uses hybrid scoring with:
  - required skills
  - must-have skills
  - nice-to-have skills
  - experience depth
  - semantic skill adjacency
- Produces explainable outputs: matched skills, missing skills, semantic evidence, strengths, and concerns.

## Core Features

- Role-family weighted ranking engine
- Hard-constraint handling for must-have skills
- Semantic partial-credit matching for related technologies
- Drag-and-drop upload UI with parse-status and profile preview cards
- Candidate leaderboard and side-by-side comparison panel

## Technical Stack

- Python, FastAPI, Pydantic
- Resume parsing: pypdf, python-docx
- Frontend: HTML/CSS/JS dashboard
- Testing: pytest

## Business Value

- Faster shortlist generation for technical hiring pipelines
- More transparent and defensible screening decisions
- Better candidate recall through semantic matching
- Demo-ready workflow suitable for startups, agencies, and HR teams

## Demo Narrative (Short)

1. Upload a backend engineering job description.
2. Drop multiple resumes in PDF/DOCX/TXT format.
3. Review auto-parsed candidate profiles before running analysis.
4. Generate leaderboard and compare top candidates.
5. Inspect explainability fields (matched, missing, semantic evidence).

## Scope Extension Options

- ATS integrations
- Auth, projects, and audit history
- CSV/PDF shortlist export
- Recruiter notes and collaboration
- Fine-tuned scoring profiles by organization
