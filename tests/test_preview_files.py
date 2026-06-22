from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_preview_files_extracts_profile_data():
    client = TestClient(app)
    payload = b"Name: Prashant Singh\nYears of Experience: 3\nPython FastAPI AWS Docker"

    response = client.post(
        "/v1/preview-files",
        files={"resumes": ("prashant_resume.txt", BytesIO(payload), "text/plain")},
    )

    assert response.status_code == 200
    body = response.json()
    assert "previews" in body
    assert body["previews"][0]["status"] == "ok"
    assert body["previews"][0]["candidate_name"] == "Prashant Singh"
    assert body["previews"][0]["years_experience"] == 3.0


def test_preview_files_accepts_multiple_resumes():
    client = TestClient(app)
    payload_a = b"Name: Asha Rao\nYears of Experience: 2\nPython FastAPI PostgreSQL"
    payload_b = b"Name: Karan Mehta\nYears of Experience: 5\nJava Spring AWS"

    response = client.post(
        "/v1/preview-files",
        files=[
            ("resumes", ("asha_resume.txt", BytesIO(payload_a), "text/plain")),
            ("resumes", ("karan_resume.txt", BytesIO(payload_b), "text/plain")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["previews"]) == 2
    names = {preview["candidate_name"] for preview in body["previews"]}
    assert names == {"Asha Rao", "Karan Mehta"}


def test_analyze_files_accepts_multiple_resumes():
    client = TestClient(app)
    payload_a = b"Name: Asha Rao\nYears of Experience: 2\nPython FastAPI PostgreSQL"
    payload_b = b"Name: Karan Mehta\nYears of Experience: 5\nJava Spring AWS"

    response = client.post(
        "/v1/analyze-files",
        data={
            "job_title": "Backend Engineer",
            "job_description": "Need Python, FastAPI, cloud exposure, databases, and reliable API development ownership.",
            "role_family": "backend",
            "must_have_skills": "python,fastapi",
            "nice_to_have_skills": "aws,postgresql",
        },
        files=[
            ("resumes", ("asha_resume.txt", BytesIO(payload_a), "text/plain")),
            ("resumes", ("karan_resume.txt", BytesIO(payload_b), "text/plain")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["ranked_candidates"]) == 2
    names = {candidate["name"] for candidate in body["ranked_candidates"]}
    assert names == {"Asha Rao", "Karan Mehta"}


def test_preview_files_returns_error_for_corrupted_pdf():
    client = TestClient(app)

    response = client.post(
        "/v1/preview-files",
        files={"resumes": ("bad.pdf", BytesIO(b"not a real pdf"), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["previews"][0]["status"] == "error"
    assert "Could not parse PDF resume" in body["previews"][0]["message"]


def test_analyze_files_rejects_corrupted_pdf_with_400():
    client = TestClient(app)

    response = client.post(
        "/v1/analyze-files",
        data={
            "job_title": "Backend Engineer",
            "job_description": "Need Python, FastAPI, cloud exposure, databases, and reliable API development ownership.",
            "role_family": "backend",
            "must_have_skills": "python,fastapi",
            "nice_to_have_skills": "aws,postgresql",
        },
        files={"resumes": ("bad.pdf", BytesIO(b"not a real pdf"), "application/pdf")},
    )

    assert response.status_code == 400
    body = response.json()
    assert "Could not parse PDF resume" in body["detail"]
