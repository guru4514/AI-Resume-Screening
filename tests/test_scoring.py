from app.schemas import CandidateInput
from app.services.skill_taxonomy import extract_skills
from app.services.scoring import build_skill_context, rank_candidates


def test_rank_candidates_prefers_skill_match():
    jd = (
        "We need a backend engineer with Python, FastAPI, Docker, PostgreSQL, "
        "and AWS experience."
    )

    role, required, must_have, nice_to_have = build_skill_context(
        job_title="Backend Engineer",
        job_description=jd,
        role_family=None,
        must_have_skills=["python", "fastapi"],
        nice_to_have_skills=["aws"],
    )

    candidates = [
        CandidateInput(
            name="Candidate A",
            years_experience=2,
            resume_text="Python FastAPI Docker PostgreSQL AWS CI/CD API integration",
        ),
        CandidateInput(
            name="Candidate B",
            years_experience=6,
            resume_text="Java Spring Kubernetes Terraform team leadership",
        ),
    ]

    ranked = rank_candidates(candidates, role, required, must_have, nice_to_have)
    assert ranked[0].name == "Candidate A"
    assert ranked[0].total_score > ranked[1].total_score


def test_must_have_constraints_reduce_score_when_missing():
    role, required, must_have, nice_to_have = build_skill_context(
        job_title="DevOps Engineer",
        job_description="Need AWS, Kubernetes, Docker, Terraform and CI/CD.",
        role_family="devops",
        must_have_skills=["kubernetes", "terraform"],
        nice_to_have_skills=["jenkins"],
    )

    candidates = [
        CandidateInput(
            name="Has Must Have",
            years_experience=3,
            resume_text="AWS Kubernetes Docker Terraform Jenkins automation",
        ),
        CandidateInput(
            name="Missing Must Have",
            years_experience=6,
            resume_text="AWS Docker CI/CD leadership operations",
        ),
    ]

    ranked = rank_candidates(candidates, role, required, must_have, nice_to_have)
    assert ranked[0].name == "Has Must Have"
    assert ranked[1].hard_constraint_passed is False


def test_semantic_matching_adds_partial_credit_and_evidence():
    role, required, must_have, nice_to_have = build_skill_context(
        job_title="ML Engineer",
        job_description="Need machine learning and llm experience.",
        role_family="data_ai",
        must_have_skills=["machine learning"],
        nice_to_have_skills=["llm"],
    )

    candidates = [
        CandidateInput(
            name="Semantic Candidate",
            years_experience=2,
            resume_text="Built NLP pipelines with PyTorch and RAG systems",
        )
    ]

    ranked = rank_candidates(candidates, role, required, must_have, nice_to_have)
    top = ranked[0]

    assert top.skill_score > 0
    assert "machine learning" in top.semantic_matches
    assert "pytorch" in top.semantic_matches["machine learning"]


def test_extract_skills_handles_common_resume_formatting_variants():
    text = "Worked with fast api, machine-learning, node.js, CI CD, and scikit learn"

    skills = extract_skills(text)

    assert "fastapi" in skills
    assert "machine learning" in skills
    assert "node" in skills
    assert "ci/cd" in skills
    assert "scikit-learn" in skills


def test_extract_skills_does_not_invent_symbol_skills_from_plain_text():
    text = "Aman Sharma was promoted after many project iterations and strong delivery results"

    skills = extract_skills(text)

    assert "c#" not in skills
    assert "c++" not in skills


def test_extract_skills_recognizes_computer_vision():
    text = "Built CV pipelines and worked on computer vision models with PyTorch"

    skills = extract_skills(text)

    assert "computer vision" in skills
    assert "pytorch" in skills
