import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    print("Testing live API endpoints...")
    
    # 1. Health
    r = requests.get(f"{BASE_URL}/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"[PASS] Health check: {r.json()}")

    # 2. Personas
    r = requests.get(f"{BASE_URL}/api/auth/personas")
    assert r.status_code == 200, f"Personas failed: {r.text}"
    personas = r.json()
    job_seekers = personas.get("job_seekers", [])
    companies = personas.get("companies", [])
    print(f"[PASS] Personas: {len(job_seekers)} Job Seekers, {len(companies)} Companies")
    assert len(job_seekers) >= 4, "Expected at least 4 job seekers"
    assert len(companies) >= 3, "Expected at least 3 companies"

    # 3. Current Role Recommendations for Alex Rivera
    alex_id = job_seekers[0]["id"]
    r = requests.get(f"{BASE_URL}/api/matching/current-roles/{alex_id}")
    assert r.status_code == 200, f"Current roles failed: {r.text}"
    rec_data = r.json()
    print(f"[PASS] Current Roles for {rec_data['candidate_name']}: {rec_data['qualified_roles_count']} qualified roles")
    assert rec_data["qualified_roles_count"] > 0
    top_role = rec_data["recommendations"][0]
    print(f"       Top Role: {top_role['title']} ({top_role['match_percentage']}%)")

    # 4. Skill Gap for Full Stack Dev
    r = requests.get(f"{BASE_URL}/api/matching/skill-gap/{alex_id}/fullstack-dev")
    assert r.status_code == 200, f"Skill gap failed: {r.text}"
    gap_data = r.json()
    print(f"[PASS] Skill Gap for Full Stack Engineer: {gap_data['current_readiness_pct']}% readiness, {gap_data['missing_skills_count']} gaps")

    # 5. Personalized Learning Roadmap
    r = requests.get(f"{BASE_URL}/api/matching/roadmap/{alex_id}/fullstack-dev")
    assert r.status_code == 200, f"Roadmap failed: {r.text}"
    roadmap_data = r.json()
    print(f"[PASS] Roadmap: {len(roadmap_data['learning_modules'])} modules, {roadmap_data['total_estimated_weeks']} weeks")

    # 6. Company Jobs & Candidate Ranking
    r = requests.get(f"{BASE_URL}/api/jobs")
    assert r.status_code == 200, f"Jobs list failed: {r.text}"
    jobs = r.json()
    print(f"[PASS] Listed {len(jobs)} active company jobs")
    
    first_job_id = jobs[0]["id"]
    r = requests.get(f"{BASE_URL}/api/jobs/{first_job_id}/candidates")
    assert r.status_code == 200, f"Candidate matches failed: {r.text}"
    matches_data = r.json()
    print(f"[PASS] Candidates ranked for '{matches_data['job']['title']}': {len(matches_data['matched_candidates'])} candidates evaluated")
    top_match = matches_data["matched_candidates"][0]
    print(f"       Top Match: {top_match['name']} ({top_match['match_score']}%)")

    # 7. Real-Time NLP Skill Extraction from Job Description Text
    test_jd = "Looking for a DevOps specialist proficient in Kubernetes, Terraform, Prometheus, and AWS cloud architectures."
    r = requests.post(f"{BASE_URL}/api/jobs/extract-skills", json={"text": test_jd})
    assert r.status_code == 200, f"Skill extract failed: {r.text}"
    extracted = r.json()
    print(f"[PASS] NLP extracted skills from text: {extracted['skills']}")
    assert "Kubernetes" in extracted["skills"]
    assert "AWS" in extracted["skills"]

    # 8. Web frontend index.html served
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Frontend failed: {r.text}"
    assert "CareerPulse AI" in r.text
    print("[PASS] Web Frontend loaded successfully at http://127.0.0.1:8000")

    print("\n" + "=" * 60)
    print("  ALL 8 LIVE ENDPOINT CHECKS SUCCEEDED 100%!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()
