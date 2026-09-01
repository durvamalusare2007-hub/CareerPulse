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
from app.db.seed_data import SEED_CANDIDATES, SEED_JOBS, generate_sample_pdf_resumes

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
    alex_skills = ["JavaScript", "HTML/CSS", "React", "Git/GitHub", "Tailwind CSS", "Redux"]
    recs = calculate_current_skill_role_recommendations(alex_skills)
    
    # Alex has all 4 required skills for Frontend Developer ("JavaScript", "HTML/CSS", "React", "Git/GitHub")
    top_role = recs[0]
    print(f"Top recommended role: {top_role['title']} with {top_role['match_percentage']}% match")
    assert top_role["title"] == "Frontend Developer", f"Expected Frontend Developer, got {top_role['title']}"
    assert top_role["match_percentage"] == 100, f"Expected 100% match, got {top_role['match_percentage']}%"
    assert top_role["is_qualified"] is True
    print("[PASS] Current-skill recommendations test passed!")

def test_skill_gap_and_roadmap():
    print("\nTesting Skill Gap Analysis & Personalized Roadmap...")
    alex_skills = ["JavaScript", "HTML/CSS", "React", "Git/GitHub", "Tailwind CSS"]
    # Stretch role: Full Stack Engineer (requires Python, Node.js, PostgreSQL, RESTful APIs)
    gap = analyze_skill_gap_for_role("fullstack-dev", alex_skills)
    print(f"Readiness for Full Stack: {gap['current_readiness_pct']}%")
    print(f"Missing skills count: {gap['missing_skills_count']}")
    assert gap["missing_skills_count"] > 0
    
    roadmap = generate_personalized_roadmap("fullstack-dev", alex_skills)
    print(f"Generated Roadmap: {roadmap['target_role_title']} with {len(roadmap['learning_modules'])} modules ({roadmap['total_estimated_weeks']} weeks)")
    assert len(roadmap["learning_modules"]) > 0
    print("[PASS] Skill gap and roadmap test passed!")

def test_candidate_ranking():
    print("\nTesting Candidate Ranking for Company Jobs...")
    job = {
        "id": "test-job-react",
        "title": "Frontend React Specialist",
        "required_skills": ["React", "JavaScript", "HTML/CSS", "Git/GitHub"],
        "preferred_skills": ["Tailwind CSS", "Redux", "TypeScript"]
    }
    ranked = rank_candidates_for_job(job, SEED_CANDIDATES)
    top_cand = ranked[0]
    print(f"Top candidate ranked for job: {top_cand['name']} with score {top_cand['match_score']}%")
    assert top_cand["name"] == "Alex Rivera", f"Expected Alex Rivera, got {top_cand['name']}"
    assert top_cand["match_score"] >= 80
    print("[PASS] Candidate ranking test passed!")

def test_pdf_generation_and_parsing():
    print("\nTesting PDF Generation and PyMuPDF Extraction...")
    generate_sample_pdf_resumes()
    pdf_path = Path(__file__).resolve().parent.parent / "sample_data" / "resumes" / "alex_rivera_resume.pdf"
    assert pdf_path.exists(), f"PDF should exist at {pdf_path}"
    
    parsed = parse_resume(pdf_path)
    print(f"Parsed candidate: {parsed['name']}, Email: {parsed['email']}")
    print(f"Parsed skills count from PDF: {len(parsed['skills'])}")
    assert len(parsed["skills"]) > 0, "Should extract skills from generated PDF"
    print("[PASS] PDF generation and parsing test passed!")

if __name__ == "__main__":
    print("=" * 60)
    print("  RUNNING ALL CAREERPULSE AI UNIT & INTEGRATION TESTS")
    print("=" * 60)
    test_nlp_extraction()
    test_current_skill_recommendations()
    test_skill_gap_and_roadmap()
    test_candidate_ranking()
    test_pdf_generation_and_parsing()
    print("\n" + "=" * 60)
    print("  ALL 5 TEST SUITES PASSED PERFECTLY!")
    print("=" * 60)
