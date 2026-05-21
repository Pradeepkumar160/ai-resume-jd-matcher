def skill_gap_analysis(
    resume_skills: list[str],
    jd_skills: list[str],
) -> tuple[list[str], list[str]]:
    """
    Compare resume skills against job description skills.

    Returns:
        matched_skills: skills present in both resume and JD
        missing_skills: skills required by JD but absent from resume
    """
    resume_set = set(s.lower() for s in resume_skills)
    matched = []
    missing = []

    for skill in jd_skills:
        if skill.lower() in resume_set:
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing
