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

class UpdateJobRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None

class ApplyJobRequest(BaseModel):
    candidate_id: str
    candidate_name: Optional[str] = "Candidate"

class CandidateStatusRequest(BaseModel):
    status: str  # "interview" or "rejected"
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    required_documents: Optional[str] = None
    reason: Optional[str] = None

class ExtractSkillsFromTextRequest(BaseModel):
    text: str

@router.post("/jobs/extract-skills")
async def extract_skills_api(req: ExtractSkillsFromTextRequest):
    """Extracts skills from job description text in real-time."""
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
    """Creates a new job requirement."""
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

@router.put("/jobs/{job_id}")
async def update_job(job_id: str, req: UpdateJobRequest):
    """Updates an existing job requisition."""
    db = get_db()
    job_col = db.get_collection("jobs")
    job = await job_col.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job requisition not found.")

    update_fields = {}
    if req.title is not None:
        update_fields["title"] = req.title
    if req.description is not None:
        update_fields["description"] = req.description
    if req.location is not None:
        update_fields["location"] = req.location
    if req.experience_required is not None:
        update_fields["experience_required"] = req.experience_required
    if req.salary_range is not None:
        update_fields["salary_range"] = req.salary_range
    if req.required_skills is not None:
        update_fields["required_skills"] = req.required_skills
    if req.preferred_skills is not None:
        update_fields["preferred_skills"] = req.preferred_skills

    if update_fields:
        await job_col.update_one({"id": job_id}, {"$set": update_fields})

    updated_job = await job_col.find_one({"id": job_id})
    return {"success": True, "job": updated_job}

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Deletes a job requisition."""
    db = get_db()
    job_col = db.get_collection("jobs")
    job = await job_col.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job requisition not found.")

    await job_col.delete_one({"id": job_id})
    return {"success": True, "message": "Job requisition deleted successfully."}

@router.post("/jobs/{job_id}/apply")
async def apply_to_job(job_id: str, req: ApplyJobRequest):
    """Allows a job seeker to apply for a job requisition."""
    db = get_db()
    job = await db.get_collection("jobs").find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    cand = await db.get_collection("candidates").find_one({"id": req.candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    app_col = db.get_collection("applications")
    existing = await app_col.find_one({"job_id": job_id, "candidate_id": req.candidate_id})
    if existing:
        return {"success": True, "message": "Already applied.", "application": existing}

    app_id = f"app-{uuid.uuid4().hex[:8]}"
    application_doc = {
        "id": app_id,
        "job_id": job_id,
        "job_title": job.get("title"),
        "company_id": job.get("company_id"),
        "company_name": job.get("company_name"),
        "candidate_id": req.candidate_id,
        "candidate_name": cand.get("name"),
        "applied_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "applied"
    }
    await app_col.insert_one(application_doc)
    return {"success": True, "message": "Application submitted successfully!", "application": application_doc}

@router.get("/jobs/applications/candidate/{candidate_id}")
async def get_candidate_applications(candidate_id: str):
    """Returns all applications made by a candidate."""
    db = get_db()
    cursor = await db.get_collection("applications").find({"candidate_id": candidate_id})
    apps = await cursor.to_list(length=100)
    return apps

@router.post("/jobs/{job_id}/candidates/{candidate_id}/status")
async def update_candidate_status(job_id: str, candidate_id: str, req: CandidateStatusRequest):
    """
    Updates candidate interview or rejection status for a job,
    and sends a structured notification to the candidate.
    """
    db = get_db()
    job = await db.get_collection("jobs").find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    app_col = db.get_collection("applications")
    app_doc = await app_col.find_one({"job_id": job_id, "candidate_id": candidate_id})
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    notif_col = db.get_collection("notifications")
    notif_id = f"notif-{uuid.uuid4().hex[:8]}"

    if req.status == "interview":
        status_data = {
            "status": "interview",
            "interview_details": {
                "location": req.location or "Online Video Conference",
                "date": req.date or datetime.now().strftime("%Y-%m-%d"),
                "time": req.time or "10:00 AM",
                "required_documents": req.required_documents or "Resume, Portfolio samples, Identification"
            },
            "updated_at": timestamp
        }
        
        notification_doc = {
            "id": notif_id,
            "user_id": candidate_id,
            "type": "interview_invitation",
            "title": f"Interview Invitation: {job.get('title')} at {job.get('company_name')}",
            "company_name": job.get("company_name"),
            "job_title": job.get("title"),
            "location": req.location or "Online Video Conference",
            "date": req.date or datetime.now().strftime("%Y-%m-%d"),
            "time": req.time or "10:00 AM",
            "required_documents": req.required_documents or "Resume, Portfolio samples, Identification",
            "created_at": timestamp,
            "is_read": False
        }
        await notif_col.insert_one(notification_doc)

    elif req.status == "rejected":
        status_data = {
            "status": "rejected",
            "rejection_reason": req.reason or "Does not meet the minimum required skill criteria at this time.",
            "updated_at": timestamp
        }

        notification_doc = {
            "id": notif_id,
            "user_id": candidate_id,
            "type": "application_update",
            "title": f"Application Status Update: {job.get('title')} at {job.get('company_name')}",
            "company_name": job.get("company_name"),
            "job_title": job.get("title"),
            "message": f"Thank you for your interest in the {job.get('title')} position at {job.get('company_name')}. After careful review, we have decided to pursue other candidates whose current skill profile more closely aligns with our current requirements.",
            "created_at": timestamp,
            "is_read": False
        }
        await notif_col.insert_one(notification_doc)
    else:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'interview' or 'rejected'.")

    if app_doc:
        await app_col.update_one({"id": app_doc["id"]}, {"$set": status_data})
    else:
        # Create application entry if not present
        new_app = {
            "id": f"app-{uuid.uuid4().hex[:8]} ",
            "job_id": job_id,
            "job_title": job.get("title"),
            "company_id": job.get("company_id"),
            "company_name": job.get("company_name"),
            "candidate_id": candidate_id,
            "candidate_name": cand.get("name"),
            "applied_at": timestamp,
            **status_data
        }
        await app_col.insert_one(new_app)

    return {"success": True, "status": req.status, "message": f"Candidate status updated to '{req.status}' and notification sent."}

@router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str):
    """Retrieves all notifications for a given user/candidate."""
    db = get_db()
    cursor = await db.get_collection("notifications").find({"user_id": user_id})
    notifs = await cursor.to_list(length=50)
    notifs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return notifs

@router.get("/news")
async def get_industry_news():
    """Returns compact industry news headlines with time and date."""
    news_items = [
        {
            "id": "news-1",
            "headline": "Tech Hiring Shifts Toward Verified Skill-First Assessment in 2026",
            "category": "Industry Trends",
            "date_time": "Sep 11, 2026 • 09:30 AM",
            "source": "TechCareers Daily"
        },
        {
            "id": "news-2",
            "headline": "Cloud Infrastructure & Containerization Skills See 45% Surge in Demand",
            "category": "Market Insights",
            "date_time": "Sep 10, 2026 • 02:15 PM",
            "source": "Cloud Insights"
        },
        {
            "id": "news-3",
            "headline": "Full-Stack Engineers with FastAPI and React Experience Lead Software Openings",
            "category": "Hiring Report",
            "date_time": "Sep 09, 2026 • 11:00 AM",
            "source": "Developer Pulse"
        },
        {
            "id": "news-4",
            "headline": "AI & Machine Learning Engineers Command Premium in Global Remote Roles",
            "category": "Salary Trends",
            "date_time": "Sep 08, 2026 • 04:45 PM",
            "source": "Global Workforce"
        },
        {
            "id": "news-5",
            "headline": "Modern DevOps Practices Emphasize Automated Observability and CI/CD Security",
            "category": "Tech News",
            "date_time": "Sep 07, 2026 • 10:20 AM",
            "source": "Engineering Wire"
        }
    ]
    return news_items

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
    Matches registered job seekers against the job's required skills.
    Ranks candidates by skill-match percentage.
    """
    db = get_db()
    job = await db.get_collection("jobs").find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidates_cursor = await db.get_collection("candidates").find({})
    candidates = await candidates_cursor.to_list(length=100)

    # Fetch applications to enrich with status
    app_cursor = await db.get_collection("applications").find({"job_id": job_id})
    apps = await app_cursor.to_list(length=100)
    app_map = {a["candidate_id"]: a for a in apps}

    ranked_candidates = rank_candidates_for_job(job, candidates)

    for c in ranked_candidates:
        cand_id = c["candidate_id"]
        if cand_id in app_map:
            c["application_status"] = app_map[cand_id].get("status", "applied")
            c["interview_details"] = app_map[cand_id].get("interview_details")
            c["rejection_reason"] = app_map[cand_id].get("rejection_reason")
        else:
            c["application_status"] = "not_applied"

    return {
        "job": job,
        "total_candidates_evaluated": len(candidates),
        "matched_candidates": ranked_candidates
    }

@router.get("/candidates/{candidate_id}")
async def get_candidate_dossier(candidate_id: str):
    """Shows candidate profile, skills, education, projects, experience, and resume."""
    db = get_db()
    cand = await db.get_collection("candidates").find_one({"id": candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return cand
