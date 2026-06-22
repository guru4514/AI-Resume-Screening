from typing import Literal

from pydantic import BaseModel, Field

from app.services.skill_taxonomy import RoleFamily


class CandidateInput(BaseModel):
    name: str = Field(..., min_length=1)
    resume_text: str = Field(..., min_length=30)
    years_experience: float = Field(0, ge=0)


class AnalyzeRequest(BaseModel):
    job_title: str = Field(..., min_length=2)
    job_description: str = Field(..., min_length=50)
    candidates: list[CandidateInput] = Field(..., min_length=1)
    role_family: RoleFamily | None = None
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)


class CandidateScore(BaseModel):
    name: str
    total_score: float
    role_family: RoleFamily
    skill_score: float
    must_have_match_rate: float
    nice_to_have_match_rate: float
    experience_score: float
    role_fit_score: float
    hard_constraint_passed: bool
    matched_skills: list[str]
    missing_skills: list[str]
    semantic_matches: dict[str, list[str]]
    strengths: list[str]
    concerns: list[str]


class AnalyzeResponse(BaseModel):
    job_title: str
    role_family: RoleFamily
    required_skills: list[str]
    must_have_skills: list[str]
    nice_to_have_skills: list[str]
    ranked_candidates: list[CandidateScore]


class UploadProfilePreview(BaseModel):
    file_name: str
    status: Literal["ok", "error"]
    candidate_name: str | None = None
    years_experience: float | None = None
    detected_skills: list[str] = Field(default_factory=list)
    message: str | None = None


class PreviewFilesResponse(BaseModel):
    previews: list[UploadProfilePreview]
