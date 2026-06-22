from typing import cast

from app.services.skill_taxonomy import (
    ROLE_BASELINE_SKILLS,
    ROLE_PROFILE_WEIGHTS,
    RoleFamily,
    extract_skills,
    get_semantic_skill_matches,
    infer_role_family,
    normalize_skill_list,
)
from app.schemas import CandidateInput, CandidateScore


def build_skill_context(
    job_title: str,
    job_description: str,
    role_family: str | None,
    must_have_skills: list[str],
    nice_to_have_skills: list[str],
) -> tuple[RoleFamily, list[str], list[str], list[str]]:
    allowed_roles = set(ROLE_PROFILE_WEIGHTS.keys())
    selected_role = (role_family or "").strip().lower()
    if selected_role in allowed_roles:
        inferred_role = cast(RoleFamily, selected_role)
    else:
        inferred_role = infer_role_family(job_title, job_description)
    required = sorted(extract_skills(job_description))

    must_have = normalize_skill_list(must_have_skills)
    nice_to_have = normalize_skill_list(nice_to_have_skills)

    # Promote explicit must-have skills to required list for gap reporting.
    required = sorted(set(required).union(set(must_have)))

    return inferred_role, required, must_have, nice_to_have


def _experience_score(years: float) -> float:
    if years >= 8:
        return 100.0
    if years >= 5:
        return 85.0
    if years >= 3:
        return 70.0
    if years >= 1:
        return 50.0
    return 30.0


def _match_rate(found: list[str], total: list[str], empty_default: float) -> float:
    if not total:
        return empty_default
    return round((len(found) / len(total)) * 100, 2)


def _semantic_weighted_match_rate(
    total_skills: list[str],
    exact_matches: list[str],
    semantic_matches: list[str],
    *,
    semantic_weight: float,
    empty_default: float,
) -> float:
    if not total_skills:
        return empty_default

    # Exclude semantic matches that are already counted as exact matches.
    exact_set = set(exact_matches)
    unique_semantic = [s for s in semantic_matches if s not in exact_set]

    weighted_hits = len(exact_matches) + (semantic_weight * len(unique_semantic))
    rate = (weighted_hits / len(total_skills)) * 100
    return round(min(rate, 100.0), 2)


def score_candidate(
    candidate: CandidateInput,
    role_family: RoleFamily,
    required_skills: list[str],
    must_have_skills: list[str],
    nice_to_have_skills: list[str],
) -> CandidateScore:
    resume_skills = extract_skills(candidate.resume_text)
    req_set = set(required_skills)
    must_set = set(must_have_skills)
    nice_set = set(nice_to_have_skills)

    semantic_required_map = get_semantic_skill_matches(required_skills, resume_skills)
    semantic_must_map = get_semantic_skill_matches(must_have_skills, resume_skills)
    semantic_nice_map = get_semantic_skill_matches(nice_to_have_skills, resume_skills)

    exact_required = sorted(req_set.intersection(resume_skills))
    semantic_required = sorted(semantic_required_map.keys())
    matched = sorted(set(exact_required).union(set(semantic_required)))
    missing = sorted(req_set.difference(resume_skills))
    for semantic_skill in semantic_required:
        if semantic_skill in missing:
            missing.remove(semantic_skill)

    exact_must = sorted(must_set.intersection(resume_skills))
    semantic_must = sorted(semantic_must_map.keys())
    matched_must = sorted(set(exact_must).union(set(semantic_must)))
    missing_must = sorted(must_set.difference(resume_skills))
    for semantic_skill in semantic_must:
        if semantic_skill in missing_must:
            missing_must.remove(semantic_skill)

    exact_nice = sorted(nice_set.intersection(resume_skills))
    semantic_nice = sorted(semantic_nice_map.keys())
    matched_nice = sorted(set(exact_nice).union(set(semantic_nice)))

    skill_score = _semantic_weighted_match_rate(
        required_skills,
        exact_required,
        semantic_required,
        semantic_weight=0.6,
        empty_default=0.0,
    )
    must_have_match_rate = _semantic_weighted_match_rate(
        must_have_skills,
        exact_must,
        semantic_must,
        semantic_weight=0.7,
        empty_default=100.0,
    )
    exact_must_have_match_rate = _match_rate(exact_must, must_have_skills, empty_default=100.0)
    nice_to_have_match_rate = _semantic_weighted_match_rate(
        nice_to_have_skills,
        exact_nice,
        semantic_nice,
        semantic_weight=0.6,
        empty_default=0.0,
    )

    experience_score = _experience_score(candidate.years_experience)
    role_weights = ROLE_PROFILE_WEIGHTS[role_family]

    # --- Role Fit Score ---
    # Measures how many role-baseline skills the candidate has.
    # This is what makes different role families produce different rankings.
    baseline_skills = ROLE_BASELINE_SKILLS.get(role_family, set())
    if baseline_skills:
        baseline_matched = resume_skills.intersection(baseline_skills)
        role_fit_score = round((len(baseline_matched) / len(baseline_skills)) * 100, 2)
    else:
        role_fit_score = 0.0

    hard_constraint_passed = exact_must_have_match_rate >= 60.0

    total_score = (
        (role_weights["required"] * skill_score)
        + (role_weights["must_have"] * must_have_match_rate)
        + (role_weights["nice"] * nice_to_have_match_rate)
        + (role_weights["experience"] * experience_score)
        + (role_weights["role_fit"] * role_fit_score)
    )

    # Penalize severe must-have misses while still ranking all candidates.
    if not hard_constraint_passed:
        total_score -= 15.0

    total_score = round(max(total_score, 0.0), 2)

    strengths: list[str] = []
    concerns: list[str] = []

    if matched:
        strengths.append(f"Matched {len(matched)} key skills")
    if semantic_required:
        strengths.append(f"Semantic coverage for {len(semantic_required)} required skills")
    if matched_must:
        strengths.append(f"Covered {len(matched_must)} must-have skills")
    if role_fit_score >= 50:
        strengths.append(f"Strong {role_family} role fit ({role_fit_score:.0f}%)")
    if candidate.years_experience >= 3:
        strengths.append("Has practical experience depth")

    if missing:
        concerns.append(f"Missing {len(missing)} required skills")
    if missing_must:
        concerns.append(f"Missing must-have skills: {', '.join(missing_must)}")
    if semantic_must and not hard_constraint_passed:
        concerns.append("Must-have coverage is semantic-only and needs direct evidence")
    if role_fit_score < 30:
        concerns.append(f"Weak {role_family} role fit ({role_fit_score:.0f}%)")
    if candidate.years_experience < 1:
        concerns.append("Low proven experience for production delivery")

    return CandidateScore(
        name=candidate.name,
        total_score=total_score,
        role_family=role_family,
        skill_score=skill_score,
        must_have_match_rate=must_have_match_rate,
        nice_to_have_match_rate=nice_to_have_match_rate,
        experience_score=experience_score,
        role_fit_score=role_fit_score,
        hard_constraint_passed=hard_constraint_passed,
        matched_skills=matched,
        missing_skills=missing,
        semantic_matches=semantic_required_map,
        strengths=strengths,
        concerns=concerns,
    )


def rank_candidates(
    candidates: list[CandidateInput],
    role_family: RoleFamily,
    required_skills: list[str],
    must_have_skills: list[str],
    nice_to_have_skills: list[str],
) -> list[CandidateScore]:
    scored = [
        score_candidate(
            candidate,
            role_family,
            required_skills,
            must_have_skills,
            nice_to_have_skills,
        )
        for candidate in candidates
    ]
    return sorted(scored, key=lambda item: item.total_score, reverse=True)
