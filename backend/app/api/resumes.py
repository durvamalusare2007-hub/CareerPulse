from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from pathlib import Path
import uuid
import shutil

from app.core.config import RESUMES_DIR, UPLOADS_DIR
from app.db.database import get_db
from app.nlp.parser import parse_resume, parse_experience_blocks, parse_education_blocks
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

@router.get("/sample-list")
async def list_sample_resumes():
    """Returns list of pre-generated sample resumes available for testing."""
    samples = [
        {
            "id": "alex_rivera_resume.pdf",
            "name": "Alex Rivera",
            "role": "Frontend Developer",
            "primary_skills": ["React", "JavaScript", "HTML/CSS", "Tailwind CSS", "Redux"],
            "filename": "alex_rivera_resume.pdf"
        },
        {
            "id": "priya_sharma_resume.pdf",
            "name": "Priya Sharma",
            "role": "Data Analyst",
            "primary_skills": ["Python", "SQL", "Pandas", "Data Visualization", "NumPy"],
            "filename": "priya_sharma_resume.pdf"
        },
        {
            "id": "marcus_chen_resume.pdf",
            "name": "Marcus Chen",
            "role": "Cloud & DevOps Engineer",
            "primary_skills": ["Linux", "Docker", "AWS", "CI/CD", "Kubernetes"],
            "filename": "marcus_chen_resume.pdf"
        },
        {
            "id": "devon_brooks_resume.pdf",
            "name": "Devon Brooks",
            "role": "Python Backend Developer",
            "primary_skills": ["Python", "FastAPI", "PostgreSQL", "RESTful APIs", "Docker"],
            "filename": "devon_brooks_resume.pdf"
        }
    ]
    return samples

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: Optional[str] = Form(None)
):
    """
    Uploads a PDF resume, parses text via PyMuPDF, extracts skills with NLP,
    and stores/updates the candidate profile.
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

    db = get_db()
    cand_col = db.get_collection("candidates")

    # If candidate_id is provided, update that candidate; otherwise create or match
    if candidate_id:
        cand = await cand_col.find_one({"id": candidate_id})
        if cand:
            # Merge skills
            existing_skills = set(cand.get("skills", []))
            extracted_skills = set(parsed_data.get("skills", []))
            all_skills = list(existing_skills.union(extracted_skills))

            update_fields = {
                "skills": all_skills if all_skills else parsed_data.get("skills", []),
                "summary": parsed_data.get("summary") or cand.get("summary"),
                "resume_filename": saved_filename
            }
            if parsed_data.get("name") and parsed_data["name"] != "Candidate":
                update_fields["name"] = parsed_data["name"]
            if parsed_data.get("email"):
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
                "message": f"Resume parsed! {len(parsed_data.get('skills', []))} skills extracted successfully."
            }

    # Create a new candidate profile from parsed resume
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
        "skills": parsed_data.get("skills", []),
        "experience": parsed_data.get("experience", []),
        "education": parsed_data.get("education", []),
        "resume_filename": saved_filename
    }
    await cand_col.insert_one(new_cand)

    return {
        "success": True,
        "candidate": new_cand,
        "parsed_data": parsed_data,
        "message": f"Resume uploaded and parsed! {len(parsed_data.get('skills', []))} skills extracted."
    }

@router.post("/parse-sample/{filename}")
async def parse_sample_resume(filename: str, candidate_id: Optional[str] = None):
    """Parses one of the preloaded sample PDF resumes on the server."""
    pdf_path = RESUMES_DIR / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample resume '{filename}' not found.")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    parsed_data = parse_resume(pdf_bytes)

    db = get_db()
    cand_col = db.get_collection("candidates")

    if candidate_id:
        await cand_col.update_one(
            {"id": candidate_id},
            {"$set": {
                "skills": parsed_data.get("skills", []),
                "summary": parsed_data.get("summary", ""),
                "experience": parsed_data.get("experience", []),
                "education": parsed_data.get("education", []),
                "resume_filename": filename
            }}
        )
        cand = await cand_col.find_one({"id": candidate_id})
        return {"success": True, "candidate": cand, "parsed_data": parsed_data}

    return {"success": True, "parsed_data": parsed_data}

@router.post("/update-skills")
async def update_skills(req: SkillUpdateRequest):
    """Updates candidate skills list (add/remove skills)."""
    db = get_db()
    cand_col = db.get_collection("candidates")
    cand = await cand_col.find_one({"id": req.candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    # Deduplicate while preserving order
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
    # Check uploads dir first, then sample resumes dir
    upload_path = UPLOADS_DIR / filename
    if upload_path.exists():
        return FileResponse(path=str(upload_path), media_type="application/pdf", filename=filename)
    
    sample_path = RESUMES_DIR / filename
    if sample_path.exists():
        return FileResponse(path=str(sample_path), media_type="application/pdf", filename=filename)

    raise HTTPException(status_code=404, detail="Resume file not found.")
