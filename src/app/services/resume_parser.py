from io import BytesIO
from pathlib import Path
import re

from docx import Document
from pypdf import PdfReader


class ResumeParsingError(ValueError):
    pass


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_resume_bytes(file_name: str, content: bytes) -> str:
    extension = Path(file_name).suffix.lower()

    if extension == ".pdf":
        return _parse_pdf(content)
    if extension == ".docx":
        return _parse_docx(content)
    if extension == ".txt":
        return _parse_txt(content)

    raise ResumeParsingError(
        f"Unsupported resume format '{extension}'. Use PDF, DOCX, or TXT."
    )


def _parse_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = _clean_text(" ".join(pages))
    except Exception as exc:
        raise ResumeParsingError("Could not parse PDF resume. The file appears corrupted.") from exc

    if not text:
        raise ResumeParsingError("Could not extract text from PDF resume.")
    return text


def _parse_docx(content: bytes) -> str:
    try:
        document = Document(BytesIO(content))
        text = _clean_text(" ".join(paragraph.text for paragraph in document.paragraphs))
    except Exception as exc:
        raise ResumeParsingError("Could not parse DOCX resume. The file appears corrupted.") from exc

    if not text:
        raise ResumeParsingError("Could not extract text from DOCX resume.")
    return text


def _parse_txt(content: bytes) -> str:
    text = _clean_text(content.decode("utf-8", errors="ignore"))
    if not text:
        raise ResumeParsingError("Could not extract text from TXT resume.")
    return text


def extract_candidate_profile(resume_text: str, fallback_file_name: str) -> tuple[str, float]:
    name = _extract_name(resume_text, fallback_file_name)
    years_experience = _extract_years_experience(resume_text)
    return name, years_experience


def _extract_name(resume_text: str, fallback_file_name: str) -> str:
    text = _clean_text(resume_text)

    name_patterns = [
        r"\bname\b\s*[:\-]\s*([a-zA-Z][a-zA-Z\s.'-]{1,60}?)(?=\s+(?:email|phone|mobile|years?\s+of\s+experience)\b|$)",
        r"\bfull\s+name\b\s*[:\-]\s*([a-zA-Z][a-zA-Z\s.'-]{1,60}?)(?=\s+(?:email|phone|mobile|years?\s+of\s+experience)\b|$)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _titlecase_name(match.group(1))

    email_match = re.search(r"([a-zA-Z0-9_.+-]+)@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if email_match:
        local_part = email_match.group(1).replace(".", " ").replace("_", " ").replace("-", " ")
        candidate = re.sub(r"\d+", "", local_part).strip()
        if candidate:
            return _titlecase_name(candidate)

    return _fallback_name_from_file(fallback_file_name)


def _extract_years_experience(resume_text: str) -> float:
    text = _clean_text(resume_text)
    year_values: list[float] = []

    patterns = [
        r"years?\s+of\s+experience\s*[:\-]\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+of\s+(?:professional\s+)?experience",
        r"experience\s*[:\-]\s*(\d+(?:\.\d+)?)\+?\s*years?",
        r"(\d+(?:\.\d+)?)\+?\s*years?\s+experience",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        for value in matches:
            year_values.append(float(value))

    if year_values:
        return round(max(year_values), 1)

    return 0.0


def _titlecase_name(value: str) -> str:
    return " ".join(part.capitalize() for part in value.split() if part)


def _fallback_name_from_file(file_name: str) -> str:
    stem = Path(file_name).stem
    normalized = re.sub(r"[_\-.]+", " ", stem).strip()
    if not normalized:
        return "Candidate"
    return _titlecase_name(normalized)
