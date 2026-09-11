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

def test_full_application_flow():
    print("============================================================")
    print("  TESTING ALL NEW & EXISTING FEATURES (E2E API VERIFICATION)")
    print("============================================================")
    
    # 1. Health check
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200
    print(f"[PASS] Health check: {r.json()}")

    # 2. Register Job Seeker
    js_payload = {
        "name": "Morgan Taylor",
        "email": "morgan.taylor.test@example.com",
        "phone": "(555) 987-6543",
        "title": "Frontend Developer"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register/job-seeker", json=js_payload)
    assert r.status_code == 200
    cand = r.json()["profile"]
    cand_id = cand["id"]
    print(f"[PASS] Job Seeker Registered: {cand['name']} (ID: {cand_id})")

    # 3. Upload Resume
    pdf_bytes = generate_test_pdf_bytes()
    files = {"file": ("morgan_taylor_resume.pdf", pdf_bytes, "application/pdf")}
    data = {"candidate_id": cand_id}
    r = requests.post(f"{BASE_URL}/api/resumes/upload", files=files, data=data)
    assert r.status_code == 200
    extracted_skills = r.json()["candidate"]["skills"]
    print(f"[PASS] Resume Uploaded & Skills Extracted: {extracted_skills}")
    assert "React" in extracted_skills

    # 4. Test Resume Deletion
    r = requests.delete(f"{BASE_URL}/api/resumes/{cand_id}")
    assert r.status_code == 200
    updated_cand = r.json()["candidate"]
    print(f"[PASS] Resume Deleted: resume_filename is {updated_cand['resume_filename']}, skills count is {len(updated_cand['skills'])}")
    assert updated_cand["resume_filename"] is None
    assert len(updated_cand["skills"]) == 0

    # 5. Re-upload Resume for subsequent tests
    r = requests.post(f"{BASE_URL}/api/resumes/upload", files={"file": ("morgan_taylor_resume.pdf", pdf_bytes, "application/pdf")}, data={"candidate_id": cand_id})
    assert r.status_code == 200
    print("[PASS] Resume Re-uploaded successfully")

    # 6. Register Company
    comp_payload = {
        "name": "Nexus Cloud Innovations",
        "email": "careers.test@nexuscloud.example.com",
        "industry": "Cloud Software",
        "location": "San Francisco, CA",
        "description": "Building next-generation cloud infrastructure."
    }
    r = requests.post(f"{BASE_URL}/api/auth/register/company", json=comp_payload)
    assert r.status_code == 200
    comp = r.json()["profile"]
    comp_id = comp["id"]
    print(f"[PASS] Company Registered: {comp['name']} (ID: {comp_id})")

    # 7. Post Job Requisition
    job_payload = {
        "company_id": comp_id,
        "title": "Frontend React Specialist",
        "description": "Seeking an engineer proficient in React, JavaScript, HTML/CSS, Tailwind CSS, and Git/GitHub.",
        "location": "Remote",
        "experience_required": "2+ years",
        "salary_range": "$95,000 - $130,000",
        "required_skills": ["React", "JavaScript", "HTML/CSS", "Git/GitHub"],
        "preferred_skills": ["Tailwind CSS", "Redux"]
    }
    r = requests.post(f"{BASE_URL}/api/jobs", json=job_payload)
    assert r.status_code == 200
    job = r.json()["job"]
    job_id = job["id"]
    print(f"[PASS] Job Requisition Created: '{job['title']}' (ID: {job_id})")

    # 8. Edit Job Requisition
    edit_payload = {
        "title": "Senior Frontend React Engineer",
        "salary_range": "$110,000 - $145,000"
    }
    r = requests.put(f"{BASE_URL}/api/jobs/{job_id}", json=edit_payload)
    assert r.status_code == 200
    updated_job = r.json()["job"]
    print(f"[PASS] Job Requisition Edited: Title updated to '{updated_job['title']}', Salary: {updated_job['salary_range']}")
    assert updated_job["title"] == "Senior Frontend React Engineer"

    # 9. Job Seeker Applies to Job
    r = requests.post(f"{BASE_URL}/api/jobs/{job_id}/apply", json={"candidate_id": cand_id, "candidate_name": "Morgan Taylor"})
    assert r.status_code == 200
    print(f"[PASS] Job Application Submitted: {r.json()['message']}")

    # 10. Check Candidate Applications
    r = requests.get(f"{BASE_URL}/api/jobs/applications/candidate/{cand_id}")
    assert r.status_code == 200
    apps = r.json()
    assert len(apps) >= 1
    print(f"[PASS] Candidate Applications: {len(apps)} active application(s)")

    # 11. Company Selects Candidate for Interview
    interview_payload = {
        "status": "interview",
        "location": "Google Meet Video Call",
        "date": "2026-09-22",
        "time": "11:00 AM EST",
        "required_documents": "Resume, Portfolio samples, Government ID"
    }
    r = requests.post(f"{BASE_URL}/api/jobs/{job_id}/candidates/{cand_id}/status", json=interview_payload)
    assert r.status_code == 200
    print(f"[PASS] Candidate Selected for Interview: {r.json()['message']}")

    # 12. Candidate Receives Structured Interview Notification
    r = requests.get(f"{BASE_URL}/api/notifications/{cand_id}")
    assert r.status_code == 200
    notifs = r.json()
    assert len(notifs) >= 1
    interview_notif = notifs[0]
    print(f"[PASS] Candidate Notification Received: '{interview_notif['title']}' on {interview_notif['date']} at {interview_notif['time']}")
    assert interview_notif["type"] == "interview_invitation"
    assert interview_notif["location"] == "Google Meet Video Call"

    # 13. Create a second job and test Candidate Rejection
    job_2 = requests.post(f"{BASE_URL}/api/jobs", json={
        "company_id": comp_id,
        "title": "Data Analyst Requisition",
        "description": "SQL and Python",
        "required_skills": ["SQL", "Pandas"]
    }).json()["job"]
    
    r = requests.post(f"{BASE_URL}/api/jobs/{job_2['id']}/candidates/{cand_id}/status", json={
        "status": "rejected",
        "reason": "Does not meet the mandatory SQL / Pandas requirements for this specific role."
    })
    assert r.status_code == 200
    print("[PASS] Candidate Rejection Notification Sent")

    # 14. Delete Job Requisition
    r = requests.delete(f"{BASE_URL}/api/jobs/{job_2['id']}")
    assert r.status_code == 200
    print(f"[PASS] Job Requisition Deleted: {r.json()['message']}")

    # 15. News Endpoint
    r = requests.get(f"{BASE_URL}/api/news")
    assert r.status_code == 200
    news_items = r.json()
    assert len(news_items) > 0
    print(f"[PASS] News Feed: {len(news_items)} compact headline items retrieved")
    print(f"       Sample: '{news_items[0]['headline']}' ({news_items[0]['date_time']})")

    print("\n" + "=" * 60)
    print("  ALL 15 E2E LIVE TEST CHECKS SUCCEEDED WITH 100% PASS!")
    print("=" * 60)

if __name__ == "__main__":
    test_full_application_flow()
