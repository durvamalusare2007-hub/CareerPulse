from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

class UserRegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    role_type: str  # "job_seeker" or "company"
    title_or_company: Optional[str] = None
    skills: Optional[List[str]] = []

@router.get("/personas")
async def get_demo_personas():
    """Returns available sample personas for quick 1-click switching."""
    db = get_db()
    candidates_cursor = await db.get_collection("candidates").find({})
    candidates = await candidates_cursor.to_list(length=10)
    
    companies_cursor = await db.get_collection("companies").find({})
    companies = await companies_cursor.to_list(length=10)

    return {
        "job_seekers": [
            {
                "id": c["id"],
                "name": c["name"],
                "title": c.get("title", "Job Seeker"),
                "email": c["email"],
                "skills_count": len(c.get("skills", [])),
                "skills_preview": c.get("skills", [])[:4],
                "resume_filename": c.get("resume_filename")
            }
            for c in candidates
        ],
        "companies": [
            {
                "id": comp["id"],
                "name": comp["name"],
                "industry": comp.get("industry"),
                "location": comp.get("location"),
                "logo_text": comp.get("logo_text", "CO")
            }
            for comp in companies
        ]
    }

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Fetches candidate or company profile by ID."""
    db = get_db()
    if user_id.startswith("cand-") or "candidate" in user_id or "@" in user_id:
        cand = await db.get_collection("candidates").find_one({"id": user_id})
        if cand:
            return {"type": "job_seeker", "profile": cand}
    
    comp = await db.get_collection("companies").find_one({"id": user_id})
    if comp:
        return {"type": "company", "profile": comp}

    # Search in both if prefix didn't match
    cand = await db.get_collection("candidates").find_one({"id": user_id})
    if cand:
        return {"type": "job_seeker", "profile": cand}

    raise HTTPException(status_code=404, detail="Profile not found")

@router.post("/register")
async def register_profile(req: UserRegisterRequest):
    """Registers a new job seeker or company."""
    db = get_db()
    if req.role_type == "job_seeker":
        cand_id = f"cand-{uuid.uuid4().hex[:8]}"
        new_cand = {
            "id": cand_id,
            "name": req.name,
            "email": req.email,
            "phone": req.phone or "",
            "title": req.title_or_company or "Software Professional",
            "summary": "Profile created on CareerPulse AI.",
            "skills": req.skills or [],
            "experience": [],
            "education": [],
            "resume_filename": None
        }
        await db.get_collection("candidates").insert_one(new_cand)
        return {"success": True, "type": "job_seeker", "profile": new_cand}
    else:
        comp_id = f"comp-{uuid.uuid4().hex[:8]}"
        new_comp = {
            "id": comp_id,
            "name": req.name,
            "industry": req.title_or_company or "Technology",
            "location": "Remote / Global",
            "website": f"https://{req.name.lower().replace(' ', '')}.com",
            "description": f"Company profile for {req.name}.",
            "logo_text": "".join([w[0].upper() for w in req.name.split()[:2]]) or "CO"
        }
        await db.get_collection("companies").insert_one(new_comp)
        return {"success": True, "type": "company", "profile": new_comp}
