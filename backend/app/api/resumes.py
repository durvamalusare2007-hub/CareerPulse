from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from pathlib import Path
import uuid

from app.core.config import RESUMES_DIR, UPLOADS_DIR
from app.db.database import get_db
from app.nlp.parser import parse_resume
from app.nlp.skill_extractor import extract_skills_from_text, get_all_taxonomy_skills

router = APIRouter(prefix="/resumes", tags=["resumes"])

class SkillUpdateRequest(BaseModel):
    candidate_id: str
    skills: List[str]

class AddCustomSkillRequest(BaseModel):
    candidate_id: str
    skill_name: str

@router.get("/taxonomy")
async def get_taxonomy():
    """Returns the standardized skills taxonomy."""
    return get_all_taxonomy_skills()

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: Optional[str] = Form(None)
):
    """
    Uploads a PDF resume, extracts text and finds skills genuinely present in the resume,
    and updates the candidate profile.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Save to uploads directory
    saved_filename = f"{uuid.uuid4().hex[:10]}_{file.filename}"
    saved_path = UPLOADS_DIR / saved_filename
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    # Parse with PyMuPDF & NLP
    parsed_data = parse_resume(file_bytes)
    extracted_skills = parsed_data.get("skills", [])

    db = get_db()
    cand_col = db.get_collection("candidates")

    if candidate_id:
        cand = await cand_col.find_one({"id": candidate_id})
        if cand:
            update_fields = {
                "skills": extracted_skills,
                "summary": parsed_data.get("summary") or cand.get("summary", ""),
                "resume_filename": saved_filename
            }
            if parsed_data.get("name") and parsed_data["name"] != "Candidate":
                update_fields["name"] = parsed_data["name"]
            if parsed_data.get("email") and not cand.get("email"):
                update_fields["email"] = parsed_data["email"]
            if parsed_data.get("phone"):
                update_fields["phone"] = parsed_data["phone"]
            if parsed_data.get("experience"):
                update_fields["experience"] = parsed_data["experience"]
            if parsed_data.get("education"):
                update_fields["education"] = parsed_data["education"]

            await cand_col.update_one({"id": candidate_id}, {"$set": update_fields})
            updated_cand = await cand_col.find_one({"id": candidate_id})
            return {
                "success": True,
                "candidate": updated_cand,
                "parsed_data": parsed_data,
                "message": f"Resume analyzed successfully! {len(extracted_skills)} skills identified."
            }

    # Create new candidate profile if no candidate_id provided
    new_id = f"cand-{uuid.uuid4().hex[:8]}"
    new_cand = {
        "id": new_id,
        "name": parsed_data.get("name", "New Candidate"),
        "email": parsed_data.get("email", f"user_{new_id}@example.com"),
        "phone": parsed_data.get("phone", ""),
        "linkedin": parsed_data.get("linkedin"),
        "github": parsed_data.get("github"),
        "title": "Software Candidate",
        "summary": parsed_data.get("summary", ""),
        "skills": extracted_skills,
        "experience": parsed_data.get("experience", []),
        "education": parsed_data.get("education", []),
        "resume_filename": saved_filename
    }
    await cand_col.insert_one(new_cand)

    return {
        "success": True,
        "candidate": new_cand,
        "parsed_data": parsed_data,
        "message": f"Resume analyzed successfully! {len(extracted_skills)} skills identified."
    }

@router.post("/update-skills")
async def update_skills(req: SkillUpdateRequest):
    """Updates candidate skills list (add/remove skills)."""
    db = get_db()
    cand_col = db.get_collection("candidates")
    cand = await cand_col.find_one({"id": req.candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    clean_skills = []
    seen = set()
    for s in req.skills:
        clean = s.strip()
        if clean and clean.lower() not in seen:
            seen.add(clean.lower())
            clean_skills.append(clean)

    await cand_col.update_one({"id": req.candidate_id}, {"$set": {"skills": clean_skills}})
    updated_cand = await cand_col.find_one({"id": req.candidate_id})
    return {"success": True, "skills": clean_skills, "candidate": updated_cand}

@router.get("/file/{filename}")
async def get_resume_file(filename: str):
    """Serves the PDF resume file for viewing or downloading."""
    upload_path = UPLOADS_DIR / filename
    if upload_path.exists():
        return FileResponse(path=str(upload_path), media_type="application/pdf", filename=filename)
    
    sample_path = RESUMES_DIR / filename
    if sample_path.exists():
        return FileResponse(path=str(sample_path), media_type="application/pdf", filename=filename)

    raise HTTPException(status_code=404, detail="Resume file not found.")
