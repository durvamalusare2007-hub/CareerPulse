import requests
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

BASE_URL = "http://127.0.0.1:8000"

def generate_test_pdf_bytes():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Morgan Taylor", styles['Heading1']),
        Paragraph("morgan.taylor@example.com | (555) 987-6543", styles['Normal']),
        Spacer(1, 10),
        Paragraph("PROFESSIONAL SUMMARY", styles['Heading2']),
        Paragraph("Frontend Software Developer with experience in React, JavaScript, HTML5, CSS3, Tailwind CSS, and Git/GitHub.", styles['Normal']),
        Spacer(1, 10),
        Paragraph("TECHNICAL SKILLS", styles['Heading2']),
        Paragraph("React, JavaScript, HTML/CSS, Tailwind CSS, Git/GitHub, Redux, RESTful APIs", styles['Normal']),
        Spacer(1, 10),
        Paragraph("EXPERIENCE", styles['Heading2']),
        Paragraph("Web Developer - Modern Apps Co (2023 - Present)", styles['Heading3']),
        Paragraph("Built responsive user interfaces using React, Redux, and Tailwind CSS.", styles['Normal'])
    ]
    doc.build(story)
    return buffer.getvalue()

def test_endpoints():
    print("Testing live API endpoints with clean dynamic data...")
    
    # 1. Health
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"[PASS] Health check: {r.json()}")

    # 2. Register Job Seeker
    js_payload = {
        "name": "Morgan Taylor",
        "email": "morgan.taylor@example.com",
        "phone": "(555) 987-6543",
        "title": "Frontend Developer"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register/job-seeker", json=js_payload)
    assert r.status_code == 200, f"Job seeker registration failed: {r.text}"
    js_data = r.json()
    cand = js_data["profile"]
    cand_id = cand["id"]
    print(f"[PASS] Job Seeker Registered: {cand['name']} (ID: {cand_id})")
    assert len(cand.get("skills", [])) == 0, "New profile should have 0 skills initially"

    # 3. Test Login for Job Seeker
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "morgan.taylor@example.com", "role_type": "job_seeker"})
    assert r.status_code == 200, f"Job seeker login failed: {r.text}"
    print("[PASS] Job Seeker Login Successful")

    # 4. Upload PDF Resume and extract skills
    pdf_bytes = generate_test_pdf_bytes()
    files = {"file": ("morgan_taylor_resume.pdf", pdf_bytes, "application/pdf")}
    data = {"candidate_id": cand_id}
    r = requests.post(f"{BASE_URL}/api/resumes/upload", files=files, data=data)
    assert r.status_code == 200, f"Resume upload failed: {r.text}"
    upload_res = r.json()
    extracted_skills = upload_res["candidate"]["skills"]
    print(f"[PASS] Resume uploaded and parsed: {len(extracted_skills)} skills found: {extracted_skills}")
    assert "React" in extracted_skills
    assert "JavaScript" in extracted_skills
    assert "Tailwind CSS" in extracted_skills

    # 5. Current Role Recommendations (Strict rule: only evaluated on current skills)
    r = requests.get(f"{BASE_URL}/api/matching/current-roles/{cand_id}")
    assert r.status_code == 200, f"Current roles failed: {r.text}"
    recs = r.json()
    print(f"[PASS] Recommended Roles: {recs['qualified_roles_count']} qualified roles found")
    top_role = recs["recommendations"][0]
    print(f"       Top Role: {top_role['title']} with {top_role['match_percentage']}% match")
    assert top_role["title"] == "Frontend Developer"
    assert top_role["match_percentage"] == 100

    # 6. Skill Gap & Learning Roadmap for stretch role
    r = requests.get(f"{BASE_URL}/api/matching/skill-gap/{cand_id}/fullstack-dev")
    assert r.status_code == 200, f"Skill gap failed: {r.text}"
    gap_data = r.json()
    print(f"[PASS] Skill Gap Analysis: {gap_data['current_readiness_pct']}% readiness for Full Stack Engineer")

    r = requests.get(f"{BASE_URL}/api/matching/roadmap/{cand_id}/fullstack-dev")
    assert r.status_code == 200, f"Roadmap failed: {r.text}"
    roadmap = r.json()
    print(f"[PASS] Roadmap Generated: {len(roadmap['learning_modules'])} learning modules ({roadmap['total_estimated_weeks']} weeks)")

    # 7. Register Company
    comp_payload = {
        "name": "Nexus Cloud Innovations",
        "email": "careers@nexuscloud.example.com",
        "industry": "Cloud Software",
        "location": "San Francisco, CA",
        "description": "Building next-generation cloud infrastructure."
    }
    r = requests.post(f"{BASE_URL}/api/auth/register/company", json=comp_payload)
    assert r.status_code == 200, f"Company registration failed: {r.text}"
    comp_data = r.json()
    company = comp_data["profile"]
    comp_id = company["id"]
    print(f"[PASS] Company Registered: {company['name']} (ID: {comp_id})")

    # 8. Post Job Requisition with NLP skill auto-detection
    job_payload = {
        "company_id": comp_id,
        "title": "Frontend React Specialist",
        "description": "Seeking an engineer proficient in React, JavaScript, HTML/CSS, Tailwind CSS, and Git/GitHub.",
        "location": "Remote",
        "experience_required": "2+ years",
        "salary_range": "$95,000 - $130,000"
    }
    r = requests.post(f"{BASE_URL}/api/jobs", json=job_payload)
    assert r.status_code == 200, f"Job creation failed: {r.text}"
    job_res = r.json()
    job = job_res["job"]
    print(f"[PASS] Job Requisition Created: {job['title']} (Required Skills: {job['required_skills']})")

    # 9. Matched Candidates for Company Job
    r = requests.get(f"{BASE_URL}/api/jobs/{job['id']}/candidates")
    assert r.status_code == 200, f"Candidate matching failed: {r.text}"
    matches_data = r.json()
    matched_candidates = matches_data["matched_candidates"]
    print(f"[PASS] Matched Candidates: {len(matched_candidates)} candidates ranked")
    top_matched = matched_candidates[0]
    print(f"       Top Matched Candidate: {top_matched['name']} with {top_matched['match_score']}% fit score")
    assert top_matched["name"] == "Morgan Taylor"
    assert top_matched["match_score"] >= 80

    # 10. Frontend HTML check
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Frontend failed: {r.text}"
    assert "CareerPulse" in r.text
    print("[PASS] Web Frontend loaded successfully")

    print("\n" + "=" * 60)
    print("  ALL 10 LIVE ENDPOINT CHECKS SUCCEEDED 100%!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
