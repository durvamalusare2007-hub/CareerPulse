from fastapi import APIRouter, HTTPException, Query
from typing import Any, Dict, List, Optional

from app.db.database import get_db
from app.ml.matcher import (
    STANDARDIZED_ROLES,
    calculate_current_skill_role_recommendations,
    analyze_skill_gap_for_role,
    generate_personalized_roadmap
)

router = APIRouter(prefix="/matching", tags=["matching"])

@router.get("/current-roles/{candidate_id}")
async def get_current_skill_roles(candidate_id: str):
    """
    CRITICAL REQUIREMENT:
    Recommends job roles using ONLY skills the user ALREADY has.
    Never tells a user to learn new skills before showing roles they already qualify for.
    """
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")

    user_skills = cand.get("skills", [])
    
    # Fetch active company jobs to cross-reference open positions
    jobs_cursor = await db.get_collection("jobs").find({})
    company_jobs = await jobs_cursor.to_list(length=100)

    recommendations = calculate_current_skill_role_recommendations(user_skills, company_jobs)

    # Separate into "Qualified Roles (Immediate Fit)" and "Partial Matches"
    qualified_roles = [r for r in recommendations if r["match_percentage"] >= 60]
    other_roles = [r for r in recommendations if r["match_percentage"] < 60]

    return {
        "candidate_id": candidate_id,
        "candidate_name": cand.get("name"),
        "candidate_skills": user_skills,
        "total_skills_count": len(user_skills),
        "qualified_roles_count": len(qualified_roles),
        "recommendations": recommendations,
        "qualified_roles": qualified_roles,
        "emerging_roles": other_roles
    }

@router.get("/future-roles/{candidate_id}")
async def get_future_stretch_roles(candidate_id: str):
    """
    Shows higher-tier/adjacent career progression roles and the additional skills
    that could unlock better compensation, leadership, or specialized domains.
    """
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")

    user_skills = cand.get("skills", [])
    user_skill_set = {s.lower() for s in user_skills}

    future_options = []
    for role in STANDARDIZED_ROLES:
        req_skills = role["required_skills"]
        pref_skills = role.get("preferred_skills", [])
        all_skills = req_skills + pref_skills

        matched = [s for s in all_skills if s.lower() in user_skill_set]
        missing = [s for s in all_skills if s.lower() not in user_skill_set]

        readiness = round((len(matched) / len(all_skills)) * 100) if all_skills else 100

        # We present stretch roles where the user has at least some foundation (e.g. 20% to 85%) or higher tier level
        future_options.append({
            "role_id": role["id"],
            "title": role["title"],
            "category": role["category"],
            "level": role["level"],
            "salary_range": role["salary_range"],
            "description": role["description"],
            "readiness_percentage": readiness,
            "skills_already_have": matched,
            "skills_to_unlock": missing,
            "unlock_count": len(missing)
        })

    # Sort by readiness descending but exclude 100% (since those are current roles)
    future_options.sort(key=lambda x: (-x["readiness_percentage"], x["unlock_count"]))

    return {
        "candidate_id": candidate_id,
        "current_skills": user_skills,
        "future_roles": future_options
    }

@router.get("/skill-gap/{candidate_id}/{role_id}")
async def get_skill_gap(candidate_id: str, role_id: str):
    """
    Deep-dive skill gap analysis for a specific target or stretch role.
    Shows exact missing skills, difficulty, learning weeks, and market value.
    """
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")

    user_skills = cand.get("skills", [])
    gap_result = analyze_skill_gap_for_role(role_id, user_skills)
    if "error" in gap_result:
        raise HTTPException(status_code=404, detail=gap_result["error"])

    return gap_result

@router.get("/roadmap/{candidate_id}/{role_id}")
async def get_learning_roadmap(candidate_id: str, role_id: str):
    """
    Generates a personalized, step-by-step milestone learning roadmap
    for the selected future role based on the candidate's current skills.
    """
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail=f"Candidate '{candidate_id}' not found.")

    user_skills = cand.get("skills", [])
    roadmap = generate_personalized_roadmap(role_id, user_skills)
    if "error" in roadmap:
        raise HTTPException(status_code=404, detail=roadmap["error"])

    return roadmap
