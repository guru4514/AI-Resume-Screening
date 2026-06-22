import re
from typing import Literal, cast

RoleFamily = Literal["backend", "frontend", "data_ai", "devops", "fullstack"]

# Curated for common software engineering and data roles.
TECH_SKILLS = {
    "programming": [
        "python",
        "java",
        "javascript",
        "typescript",
        "c++",
        "c#",
        "go",
        "sql",
    ],
    "frameworks": [
        "fastapi",
        "django",
        "flask",
        "spring",
        "react",
        "node",
        "dotnet",
        "pytorch",
        "tensorflow",
    ],
    "cloud_devops": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "terraform",
        "ci/cd",
        "jenkins",
        "github actions",
    ],
    "data_ai": [
        "machine learning",
        "computer vision",
        "nlp",
        "llm",
        "rag",
        "pandas",
        "numpy",
        "scikit-learn",
        "postgresql",
        "mongodb",
    ],
}

SKILL_ALIASES = {
    "py": "python",
    "nodejs": "node",
    "node.js": "node",
    "node js": "node",
    ".net": "dotnet",
    "dotnet": "dotnet",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "fast api": "fastapi",
    "machine-learning": "machine learning",
    "k8s": "kubernetes",
    "tf": "terraform",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machine learning",
    "cv": "computer vision",
    "ci cd": "ci/cd",
    "genai": "llm",
    "large language model": "llm",
    "large language models": "llm",
    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",
    "amazon web services": "aws",
    "google cloud": "gcp",
}

RELATED_SKILL_GRAPH = {
    "python": {"django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"},
    "javascript": {"typescript", "react", "node"},
    "typescript": {"javascript", "react", "node"},
    "sql": {"postgresql", "mongodb"},
    "postgresql": {"sql"},
    "machine learning": {"pytorch", "tensorflow", "scikit-learn", "numpy", "pandas", "llm", "nlp"},
    "computer vision": {"pytorch", "tensorflow", "numpy", "pandas"},
    "llm": {"nlp", "rag", "machine learning"},
    "nlp": {"llm", "machine learning"},
    "aws": {"docker", "kubernetes", "terraform", "github actions", "jenkins"},
    "azure": {"docker", "kubernetes", "terraform", "github actions", "jenkins"},
    "gcp": {"docker", "kubernetes", "terraform", "github actions", "jenkins"},
    "kubernetes": {"docker", "terraform", "aws", "azure", "gcp"},
    "terraform": {"kubernetes", "aws", "azure", "gcp"},
    "ci/cd": {"jenkins", "github actions"},
}

ROLE_KEYWORDS = {
    "backend": ["backend", "api", "microservice", "server-side"],
    "frontend": ["frontend", "ui", "ux", "web", "react"],
    "data_ai": ["data", "ml", "ai", "machine learning", "nlp", "llm"],
    "devops": ["devops", "sre", "platform", "infra", "kubernetes"],
    "fullstack": ["full stack", "fullstack"],
}

ROLE_PROFILE_WEIGHTS = {
    "backend": {"required": 0.30, "must_have": 0.25, "nice": 0.05, "experience": 0.15, "role_fit": 0.25},
    "frontend": {"required": 0.30, "must_have": 0.25, "nice": 0.05, "experience": 0.15, "role_fit": 0.25},
    "data_ai": {"required": 0.25, "must_have": 0.25, "nice": 0.05, "experience": 0.15, "role_fit": 0.30},
    "devops": {"required": 0.25, "must_have": 0.30, "nice": 0.05, "experience": 0.10, "role_fit": 0.30},
    "fullstack": {"required": 0.30, "must_have": 0.20, "nice": 0.10, "experience": 0.15, "role_fit": 0.25},
}

# Core skills expected for each role family.  These are injected into the
# evaluation regardless of what the job description says, so that changing
# the role family actually changes which candidates score highest.
ROLE_BASELINE_SKILLS: dict[str, set[str]] = {
    "backend": {
        "python", "java", "go", "sql", "fastapi", "django", "flask",
        "spring", "node", "dotnet", "postgresql", "docker", "aws",
    },
    "frontend": {
        "javascript", "typescript", "react", "node", "c#", "dotnet",
    },
    "data_ai": {
        "python", "machine learning", "nlp", "llm", "rag", "pytorch",
        "tensorflow", "pandas", "numpy", "scikit-learn", "sql",
    },
    "devops": {
        "docker", "kubernetes", "terraform", "aws", "azure", "gcp",
        "ci/cd", "jenkins", "github actions", "python", "go",
    },
    "fullstack": {
        "python", "javascript", "typescript", "react", "node", "sql",
        "fastapi", "django", "docker", "postgresql", "aws",
    },
}

CANONICAL_SKILLS = {skill for group in TECH_SKILLS.values() for skill in group}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_term(text: str, term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text) is not None


def _separator_normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _contains_flexible_phrase(text: str, term: str) -> bool:
    normalized_term = _separator_normalize(term)
    if not normalized_term or " " not in normalized_term:
        return False

    normalized_text = _separator_normalize(text)
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def normalize_skill_name(skill: str) -> str:
    normalized = normalize_text(skill)
    return SKILL_ALIASES.get(normalized, normalized)


def extract_skills(text: str) -> set[str]:
    normalized = normalize_text(text)
    found: set[str] = set()

    for skill in CANONICAL_SKILLS:
        if _contains_term(normalized, skill) or _contains_flexible_phrase(normalized, skill):
            found.add(skill)

    for alias, canonical in SKILL_ALIASES.items():
        if _contains_term(normalized, alias) or _contains_flexible_phrase(normalized, alias):
            found.add(canonical)

    return found


def infer_role_family(job_title: str, job_description: str) -> RoleFamily:
    text = normalize_text(f"{job_title} {job_description}")

    scores: dict[str, int] = {role: 0 for role in ROLE_KEYWORDS}
    for role, keywords in ROLE_KEYWORDS.items():
        for keyword in keywords:
            if _contains_term(text, keyword):
                scores[role] += 1

    inferred = max(scores, key=lambda role: scores[role])
    if scores[inferred] == 0:
        return "backend"
    return cast(RoleFamily, inferred)


def normalize_skill_list(skills: list[str]) -> list[str]:
    cleaned = {
        normalize_skill_name(skill)
        for skill in skills
        if normalize_skill_name(skill)
    }
    return sorted(cleaned)


def get_semantic_skill_matches(required_skills: list[str], resume_skills: set[str]) -> dict[str, list[str]]:
    semantic_matches: dict[str, list[str]] = {}
    for skill in required_skills:
        normalized_skill = normalize_skill_name(skill)
        if normalized_skill in resume_skills:
            continue

        related = RELATED_SKILL_GRAPH.get(normalized_skill, set())
        supports = sorted(resume_skills.intersection(related))
        if supports:
            semantic_matches[normalized_skill] = supports

    return semantic_matches
