import pytest

from app.services.resume_parser import (
    ResumeParsingError,
    extract_candidate_profile,
    parse_resume_bytes,
)


def test_extract_candidate_profile_from_name_and_experience_lines():
    text = "Name: Prashant Singh Email: prashant@gmail.com Years of Experience: 3"
    name, years = extract_candidate_profile(text, "resume.pdf")

    assert name == "Prashant Singh"
    assert years == 3.0


def test_extract_candidate_profile_from_email_and_fallback():
    text = "Contact: ananya.verma98@example.com Built backend APIs with Python."
    name, years = extract_candidate_profile(text, "candidate_profile.docx")

    assert name == "Ananya Verma"
    assert years == 0.0


def test_parse_resume_bytes_rejects_corrupted_pdf():
    with pytest.raises(ResumeParsingError, match="Could not parse PDF resume"):
        parse_resume_bytes("broken.pdf", b"not a real pdf file")


def test_parse_resume_bytes_rejects_corrupted_docx():
    with pytest.raises(ResumeParsingError, match="Could not parse DOCX resume"):
        parse_resume_bytes("broken.docx", b"not a zip docx")
