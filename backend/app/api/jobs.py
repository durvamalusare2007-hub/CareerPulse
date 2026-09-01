from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from app.db.database import get_db
from app.nlp.skill_extractor import extract_skills_from_text
from app.ml.matcher import rank_candidates_for_job

router = APIRouter(tags=["jobs & companies"])

class CreateJobRequest(BaseModel):
    company_id: str
    title: str
    description: str
    location: Optional[str] = "Remote"
    experience_required: Optional[str] = "2+ years"
    salary_range: Optional[str] = "$90,000 - $130,000"
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None

class ExtractSkillsFromTextRequest(BaseModel):
    text: str

@router.post("/jobs/extract-skills")
async def extract_skills_api(req: ExtractSkillsFromTextRequest):
    """NLP endpoint that extracts skills from job description text in real-time."""
    extracted = extract_skills_from_text(req.text)
    return extracted

@router.get("/jobs")
async def list_jobs(company_id: Optional[str] = None):
    """Lists active job postings, optionally filtered by company."""
    db = get_db()
    query = {"company_id": company_id} if company_id else {}
    cursor = await db.get_collection("jobs").find(query)
    jobs = await cursor.to_list(length=100)
    
    # Enrich with match counts
    cand_cursor = await db.get_collection("candidates").find({})
    candidates = await cand_cursor.to_list(length=100)

    enriched_jobs = []
    for j in jobs:
        job_copy = dict(j)
        ranked = rank_candidates_for_job(j, candidates)
        high_matches = [c for c in ranked if c["match_score"] >= 60]
        job_copy["matched_candidates_count"] = len(ranked)
        job_copy["high_fit_candidates_count"] = len(high_matches)
        job_copy["top_match_score"] = ranked[0]["match_score"] if ranked else 0
        enriched_jobs.append(job_copy)

    return enriched_jobs

@router.post("/jobs")
async def create_job(req: CreateJobRequest):
    """
    Creates a new job requirement.
    If required_skills are not explicitly provided, uses NLP to auto-extract them from description!
    """
    db = get_db()
    comp = await db.get_collection("companies").find_one({"id": req.company_id})
    if not comp:
        raise HTTPException(status_code=404, detail="Company not found.")

    req_skills = req.required_skills or []
    pref_skills = req.preferred_skills or []

    # Auto-extract from description if empty
    if not req_skills:
        extracted = extract_skills_from_text(req.description)
        all_ext = extracted.get("skills", [])
        # Take top 5 as required, rest as preferred
        req_skills = all_ext[:5]
        pref_skills = all_ext[5:10]

    job_id = f"job-{uuid.uuid4().hex[:8]}"
    new_job = {
        "id": job_id,
        "company_id": req.company_id,
        "company_name": comp.get("name"),
        "title": req.title,
        "description": req.description,
        "location": req.location,
        "experience_required": req.experience_required,
        "salary_range": req.salary_range,
        "required_skills": req_skills,
        "preferred_skills": pref_skills,
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }

    await db.get_collection("jobs").insert_one(new_job)
    return {"success": True, "job": new_job}

@router.get("/jobs/{job_id}")
async def get_job_detail(job_id: str):
    """Fetches job details by ID."""
    db = get_db()
    job = await db.get_collection("jobs").find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.get("/jobs/{job_id}/candidates")
async def get_matched_candidates_for_job(job_id: str):
    """
    COMPANY CORE REQUIREMENT:
    Matches all registered job seekers against the job's required skills.
    Ranks candidates by skill-match percentage.
    """
    db = get_db()
    job = await db.get_collection("jobs").find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidates_cursor = await db.get_collection("candidates").find({})
    candidates = await candidates_cursor.to_list(length=100)

    ranked_candidates = rank_candidates_for_job(job, candidates)

    return {
        "job": job,
        "total_candidates_evaluated": len(candidates),
        "matched_candidates": ranked_candidates
    }

@router.get("/candidates/{candidate_id}")
async def get_candidate_dossier(candidate_id: str):
    """
    Shows candidate profile, skills, education, projects, experience, and resume.
    """
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return cand
