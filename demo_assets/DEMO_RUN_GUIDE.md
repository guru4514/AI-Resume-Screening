# Demo Run Guide

## Files Created

- Job Description:
  - `demo_assets/job_descriptions/backend_python_senior_jd.txt`
- Resumes:
  - `demo_assets/resumes_pdf/01_aman_sharma_strong_fit.pdf`
  - `demo_assets/resumes_pdf/02_riya_verma_good_fit.pdf`
  - `demo_assets/resumes_pdf/03_nikhil_saxena_partial_fit.pdf`
  - `demo_assets/resumes_pdf/04_priya_nair_data_heavy_fit.pdf`
  - `demo_assets/resumes_pdf/05_karan_malhotra_devops_fit.pdf`
  - `demo_assets/resumes_pdf/06_megha_kapoor_low_fit.pdf`
  - (Source TXT files are in `demo_assets/resumes/`)

## Regenerate PDFs (optional)

```powershell
Set-Location "c:\Users\pytorch\Desktop\AI Resume Screening & Analysis System"
.\.venv\Scripts\python.exe .\scripts\generate_demo_resume_pdfs.py
```

- Generator script: `scripts/generate_demo_resume_pdfs.py`

## Legacy text resumes

  - `demo_assets/resumes/01_aman_sharma_strong_fit.txt`
  - `demo_assets/resumes/02_riya_verma_good_fit.txt`
  - `demo_assets/resumes/03_nikhil_saxena_partial_fit.txt`
  - `demo_assets/resumes/04_priya_nair_data_heavy_fit.txt`
  - `demo_assets/resumes/05_karan_malhotra_devops_fit.txt`
  - `demo_assets/resumes/06_megha_kapoor_low_fit.txt`

## Expected ranking pattern

1. Aman (strong backend fit)
2. Riya (good backend fit)
3. Karan / Priya (strong adjacent fit, role-dependent)
4. Nikhil (partial fit from Java-heavy background)
5. Megha (low fit for backend role)

## Recommended Dashboard Demo Flow

1. Start app and open `http://127.0.0.1:8001/`
2. Paste the JD content from the job description file.
3. Select `Upload Resume Files` mode.
4. Upload all resume files from `demo_assets/resumes_pdf/`.
5. Run screening and show leaderboard + comparison panel.
6. Highlight semantic evidence for near-miss candidates.
