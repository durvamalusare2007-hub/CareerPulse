import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.nlp.skill_extractor import extract_skills_from_text, normalize_text
from app.nlp.parser import parse_resume
from app.ml.matcher import (
    calculate_current_skill_role_recommendations,
    analyze_skill_gap_for_role,
    generate_personalized_roadmap,
    rank_candidates_for_job,
    STANDARDIZED_ROLES
)

def test_nlp_extraction():
    print("Testing NLP Skill Extraction...")
    sample_text = """
    Experienced Software Engineer skilled in React, JavaScript, HTML5, CSS3, Tailwind CSS, and Python.
    Worked with FastAPI, Docker, and PostgreSQL on AWS cloud infrastructure.
    Strong problem solving, leadership, and communication abilities.
    """
    extracted = extract_skills_from_text(sample_text)
    skills = extracted["skills"]
    print(f"Extracted {len(skills)} skills: {skills}")
    
    assert "React" in skills, "React should be extracted"
    assert "Python" in skills, "Python should be extracted"
    assert "FastAPI" in skills, "FastAPI should be extracted"
    assert "Docker" in skills, "Docker should be extracted"
    assert "AWS" in skills, "AWS should be extracted"
    assert "PostgreSQL" in skills, "PostgreSQL should be extracted"
    print("[PASS] NLP extraction test passed!")

def test_current_skill_recommendations():
    print("\nTesting Strict Current-Skill Recommendations...")
    candidate_skills = ["JavaScript", "HTML/CSS", "React", "Git/GitHub", "Tailwind CSS", "Redux"]
    recs = calculate_current_skill_role_recommendations(candidate_skills)
    
    top_role = recs[0]
    print(f"Top recommended role: {top_role['title']} with {top_role['match_percentage']}% match")
    assert top_role["title"] == "Frontend Developer", f"Expected Frontend Developer, got {top_role['title']}"
    assert top_role["match_percentage"] == 100, f"Expected 100% match, got {top_role['match_percentage']}%"
    assert top_role["is_qualified"] is True
    print("[PASS] Current-skill recommendations test passed!")

def test_skill_gap_and_roadmap():
    print("\nTesting Skill Gap Analysis & Personalized Roadmap...")
    candidate_skills = ["JavaScript", "HTML/CSS", "React", "Git/GitHub", "Tailwind CSS"]
    gap = analyze_skill_gap_for_role("fullstack-dev", candidate_skills)
    print(f"Readiness for Full Stack: {gap['current_readiness_pct']}%")
    print(f"Missing skills count: {gap['missing_skills_count']}")
    assert gap["missing_skills_count"] > 0
    
    roadmap = generate_personalized_roadmap("fullstack-dev", candidate_skills)
    print(f"Generated Roadmap: {roadmap['target_role_title']} with {len(roadmap['learning_modules'])} modules ({roadmap['total_estimated_weeks']} weeks)")
    assert len(roadmap["learning_modules"]) > 0
    print("[PASS] Skill gap and roadmap test passed!")

def test_candidate_ranking():
    print("\nTesting Candidate Ranking for Company Jobs...")
    test_candidates = [
        {
            "id": "cand-test-1",
            "name": "Jane Developer",
            "title": "Frontend Engineer",
            "email": "jane@example.com",
            "skills": ["React", "JavaScript", "HTML/CSS", "Git/GitHub", "Tailwind CSS"]
        },
        {
            "id": "cand-test-2",
            "name": "John Analyst",
            "title": "Data Analyst",
            "email": "john@example.com",
            "skills": ["Python", "SQL", "Pandas", "Data Analysis"]
        }
    ]
    job = {
        "id": "test-job-react",
        "title": "Frontend React Specialist",
        "required_skills": ["React", "JavaScript", "HTML/CSS", "Git/GitHub"],
        "preferred_skills": ["Tailwind CSS", "TypeScript"]
    }
    ranked = rank_candidates_for_job(job, test_candidates)
    top_cand = ranked[0]
    print(f"Top candidate ranked for job: {top_cand['name']} with score {top_cand['match_score']}%")
    assert top_cand["name"] == "Jane Developer"
    assert top_cand["match_score"] >= 80
    print("[PASS] Candidate ranking test passed!")

def test_pdf_parsing():
    print("\nTesting PDF Parsing with PyMuPDF...")
    # Generate a lightweight test PDF in memory / temp
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Jane Candidate", styles['Heading1']),
        Paragraph("jane@example.com | (555) 123-4567", styles['Normal']),
        Spacer(1, 10),
        Paragraph("PROFESSIONAL SUMMARY", styles['Heading2']),
        Paragraph("Experienced engineer proficient in Python, FastAPI, Docker, and PostgreSQL.", styles['Normal']),
        Spacer(1, 10),
        Paragraph("TECHNICAL SKILLS", styles['Heading2']),
        Paragraph("Python, FastAPI, Docker, PostgreSQL, AWS, Git/GitHub, Linux", styles['Normal'])
    ]
    doc.build(story)
    pdf_bytes = buffer.getvalue()

    parsed = parse_resume(pdf_bytes)
    print(f"Parsed candidate: {parsed['name']}, Email: {parsed['email']}")
    print(f"Parsed skills count from PDF: {len(parsed['skills'])} -> {parsed['skills']}")
    assert "Python" in parsed["skills"]
    assert "FastAPI" in parsed["skills"]
    assert "Docker" in parsed["skills"]
    assert "PostgreSQL" in parsed["skills"]
    print("[PASS] PDF parsing test passed!")

if __name__ == "__main__":
    print("=" * 60)
    print("  RUNNING ALL CAREERPULSE ADVISOR UNIT & INTEGRATION TESTS")
    print("=" * 60)
    test_nlp_extraction()
    test_current_skill_recommendations()
    test_skill_gap_and_roadmap()
    test_candidate_ranking()
    test_pdf_parsing()
    print("\n" + "=" * 60)
    print("  ALL 5 TEST SUITES PASSED PERFECTLY!")
    print("=" * 60)
