import re
from typing import Any, Dict, List, Optional
from pathlib import Path
import pymupdf as fitz

from app.nlp.skill_extractor import extract_skills_from_text

# Common section header patterns in resumes
SECTION_PATTERNS = {
    "summary": re.compile(r"^\s*(professional\s+summary|summary|profile|about\s+me|objective)\b", re.IGNORECASE),
    "experience": re.compile(r"^\s*(experience|work\s+experience|employment\s+history|professional\s+experience|work\s+history)\b", re.IGNORECASE),
    "education": re.compile(r"^\s*(education|academic\s+background|qualifications|academic\s+history)\b", re.IGNORECASE),
    "skills": re.compile(r"^\s*(skills|technical\s+skills|core\s+competencies|technologies|expertise|skillset)\b", re.IGNORECASE),
    "projects": re.compile(r"^\s*(projects|key\s+projects|academic\s+projects|personal\s+projects|portfolio)\b", re.IGNORECASE),
    "certifications": re.compile(r"^\s*(certifications|certificates|licenses|accreditations)\b", re.IGNORECASE),
}

EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
LINKEDIN_PATTERN = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)', re.IGNORECASE)
GITHUB_PATTERN = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', re.IGNORECASE)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts clean full text from a PDF file using PyMuPDF (fitz)."""
    text_chunks = []
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text_chunks.append(page.get_text())
        doc.close()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""
    return "\n".join(text_chunks)


def extract_text_from_bytes(pdf_bytes: bytes) -> str:
    """Extracts text from raw PDF bytes."""
    text_chunks = []
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text_chunks.append(page.get_text())
        doc.close()
    except Exception as e:
        print(f"Error reading PDF bytes: {e}")
        return ""
    return "\n".join(text_chunks)


def segment_resume_sections(full_text: str) -> Dict[str, str]:
    """Segments resume text into standard sections based on detected headers."""
    lines = full_text.splitlines()
    sections: Dict[str, List[str]] = {
        "header": [],
        "summary": [],
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "other": []
    }

    current_section = "header"
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Check if line matches a section header (usually short, e.g. <= 40 chars)
        if len(stripped) <= 45:
            matched_sec = None
            for sec_name, pattern in SECTION_PATTERNS.items():
                if pattern.search(stripped):
                    matched_sec = sec_name
                    break
            if matched_sec:
                current_section = matched_sec
                continue

        sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items()}


def extract_contact_info(text: str, header_text: str) -> Dict[str, Optional[str]]:
    """Extracts candidate contact information (name, email, phone, links)."""
    emails = EMAIL_PATTERN.findall(text)
    phones = PHONE_PATTERN.findall(text)
    linkedin = LINKEDIN_PATTERN.search(text)
    github = GITHUB_PATTERN.search(text)

    # Name is typically the first non-empty line of the resume header
    name = "Candidate"
    for line in header_text.splitlines():
        clean = line.strip()
        # Exclude lines with email or phone or links
        if clean and not EMAIL_PATTERN.search(clean) and not PHONE_PATTERN.search(clean) and "@" not in clean and "http" not in clean:
            # Check length: names are usually 2-4 words
            words = clean.split()
            if 1 <= len(words) <= 5 and not any(w.lower() in ["curriculum", "vitae", "resume", "profile", "page"] for w in words):
                name = clean
                break

    return {
        "name": name,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
    }


def parse_experience_blocks(experience_text: str) -> List[Dict[str, Any]]:
    """Parses experience text into structured job roles."""
    blocks = []
    lines = [l.strip() for l in experience_text.splitlines() if l.strip()]
    if not lines:
        return []

    current_role: Optional[Dict[str, Any]] = None
    year_pattern = re.compile(r'\b(19\d\d|20\d\d)\b')

    for line in lines:
        # Check if line looks like a title or company header (has dates or company keywords)
        has_year = bool(year_pattern.search(line))
        is_bullet = line.startswith(('-', '•', '*', '–', '—')) or line[0].isdigit() and line[1:3] in ('. ', ') ')
        
        if (has_year or len(line) < 50) and not is_bullet and current_role is not None and current_role.get("bullets"):
            # New role entry
            blocks.append(current_role)
            current_role = {"title": line, "details": line, "bullets": []}
        elif current_role is None:
            current_role = {"title": line, "details": line, "bullets": []}
        else:
            if is_bullet:
                current_role["bullets"].append(line.lstrip('-•*–— 0123456789.)'))
            else:
                if not current_role["bullets"] and len(current_role["details"]) < 100:
                    current_role["details"] += " | " + line
                else:
                    current_role["bullets"].append(line)

    if current_role:
        blocks.append(current_role)

    return blocks


def parse_education_blocks(education_text: str) -> List[Dict[str, Any]]:
    """Parses education text into structured degree/institution blocks."""
    lines = [l.strip() for l in education_text.splitlines() if l.strip()]
    degrees = []
    for line in lines:
        degrees.append({"institution_or_degree": line})
    return degrees


def parse_resume(pdf_path_or_bytes: Any) -> Dict[str, Any]:
    """
    Complete resume parsing pipeline:
    1. Extracts raw text via PyMuPDF
    2. Segments into sections
    3. Extracts contact info
    4. Extracts and classifies skills
    5. Structures experience and education
    """
    if isinstance(pdf_path_or_bytes, bytes):
        raw_text = extract_text_from_bytes(pdf_path_or_bytes)
    elif isinstance(pdf_path_or_bytes, (str, Path)):
        raw_text = extract_text_from_pdf(str(pdf_path_or_bytes))
    else:
        raw_text = str(pdf_path_or_bytes)

    if not raw_text.strip():
        return {
            "name": "Candidate",
            "email": None,
            "phone": None,
            "summary": "",
            "skills": [],
            "categorized_skills": {},
            "skill_details": [],
            "experience": [],
            "education": [],
            "projects": "",
            "raw_text": ""
        }

    sections = segment_resume_sections(raw_text)
    contact_info = extract_contact_info(raw_text, sections.get("header", ""))
    
    # NLP Skill Extraction
    # Skills from explicit skills section + full text
    skills_data = extract_skills_from_text(raw_text)
    
    experience_blocks = parse_experience_blocks(sections.get("experience", ""))
    education_blocks = parse_education_blocks(sections.get("education", ""))

    return {
        "name": contact_info["name"],
        "email": contact_info["email"],
        "phone": contact_info["phone"],
        "linkedin": contact_info["linkedin"],
        "github": contact_info["github"],
        "summary": sections.get("summary", "") or sections.get("header", ""),
        "skills": skills_data["skills"],
        "categorized_skills": skills_data["categorized"],
        "skill_details": skills_data["skill_details"],
        "total_skills_count": skills_data["total_count"],
        "experience": experience_blocks,
        "education": education_blocks,
        "projects_text": sections.get("projects", ""),
        "raw_text": raw_text
    }
