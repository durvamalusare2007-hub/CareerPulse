from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid

from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

class UserLoginRequest(BaseModel):
    email: str
    role_type: str  # "job_seeker" or "company"

class JobSeekerRegisterRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    title: Optional[str] = "Job Seeker"

class CompanyRegisterRequest(BaseModel):
    name: str
    email: str
    industry: Optional[str] = "Technology"
    location: Optional[str] = "Remote"
    description: Optional[str] = ""

@router.post("/login")
async def login(req: UserLoginRequest):
    """Logs in an existing Job Seeker or Company by email."""
    email_clean = req.email.strip().lower()
    db = get_db()

    if req.role_type == "job_seeker":
        cand_col = db.get_collection("candidates")
        candidates = await (await cand_col.find({})).to_list(length=500)
        user = next((c for c in candidates if c.get("email", "").strip().lower() == email_clean), None)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"No Job Seeker account found with email '{req.email}'. Please sign up first."
            )
        return {"success": True, "type": "job_seeker", "profile": user}
    
    elif req.role_type == "company":
        comp_col = db.get_collection("companies")
        companies = await (await comp_col.find({})).to_list(length=500)
        comp = next((c for c in companies if c.get("email", "").strip().lower() == email_clean), None)
        if not comp:
            raise HTTPException(
                status_code=404,
                detail=f"No Company account found with email '{req.email}'. Please sign up first."
            )
        return {"success": True, "type": "company", "profile": comp}
    
    raise HTTPException(status_code=400, detail="Invalid role_type. Must be 'job_seeker' or 'company'.")

@router.post("/register/job-seeker")
async def register_job_seeker(req: JobSeekerRegisterRequest):
    """Registers a new Job Seeker profile."""
    email_clean = req.email.strip().lower()
    if not req.name.strip() or not email_clean:
        raise HTTPException(status_code=400, detail="Name and Email are required.")

    db = get_db()
    cand_col = db.get_collection("candidates")
    candidates = await (await cand_col.find({})).to_list(length=500)
    existing = next((c for c in candidates if c.get("email", "").strip().lower() == email_clean), None)
    if existing:
        return {"success": True, "type": "job_seeker", "profile": existing, "message": "Account already exists. Logged in."}

    cand_id = f"cand-{uuid.uuid4().hex[:8]}"
    new_cand = {
        "id": cand_id,
        "name": req.name.strip(),
        "email": email_clean,
        "phone": req.phone.strip() if req.phone else "",
        "title": req.title.strip() if req.title else "Job Seeker",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "resume_filename": None
    }
    await cand_col.insert_one(new_cand)
    return {"success": True, "type": "job_seeker", "profile": new_cand}

@router.post("/register/company")
async def register_company(req: CompanyRegisterRequest):
    """Registers a new Company profile."""
    email_clean = req.email.strip().lower()
    if not req.name.strip() or not email_clean:
        raise HTTPException(status_code=400, detail="Company Name and Email are required.")

    db = get_db()
    comp_col = db.get_collection("companies")
    companies = await (await comp_col.find({})).to_list(length=500)
    existing = next((c for c in companies if c.get("email", "").strip().lower() == email_clean), None)
    if existing:
        return {"success": True, "type": "company", "profile": existing, "message": "Company account already exists. Logged in."}

    comp_id = f"comp-{uuid.uuid4().hex[:8]}"
    logo_text = "".join([w[0].upper() for w in req.name.strip().split()[:2]]) or "CO"
    new_comp = {
        "id": comp_id,
        "name": req.name.strip(),
        "email": email_clean,
        "industry": req.industry.strip() if req.industry else "Technology",
        "location": req.location.strip() if req.location else "Remote",
        "description": req.description.strip() if req.description else f"Company profile for {req.name.strip()}.",
        "logo_text": logo_text
    }
    await comp_col.insert_one(new_comp)
    return {"success": True, "type": "company", "profile": new_comp}

@router.get("/profile/{user_id}")
async def get_profile(user_id: str):
    """Fetches candidate or company profile by ID."""
    db = get_db()
    if user_id.startswith("cand-"):
        cand = await db.get_collection("candidates").find_one({"id": user_id})
        if cand:
            return {"type": "job_seeker", "profile": cand}
    elif user_id.startswith("comp-"):
        comp = await db.get_collection("companies").find_one({"id": user_id})
        if comp:
            return {"type": "company", "profile": comp}

    # Search in both collections
    cand = await db.get_collection("candidates").find_one({"id": user_id})
    if cand:
        return {"type": "job_seeker", "profile": cand}

    comp = await db.get_collection("companies").find_one({"id": user_id})
    if comp:
        return {"type": "company", "profile": comp}

    raise HTTPException(status_code=404, detail="Profile not found.")
