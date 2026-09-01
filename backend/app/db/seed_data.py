import asyncio
from pathlib import Path
from typing import Any, Dict, List
import uuid

from app.core.config import RESUMES_DIR
from app.db.database import get_db

SEED_CANDIDATES = [
    {
        "id": "cand-alex-rivera",
        "name": "Alex Rivera",
        "email": "alex.rivera@example.com",
        "phone": "(555) 234-5678",
        "linkedin": "https://linkedin.com/in/alexrivera-dev",
        "github": "https://github.com/alexrivera",
        "title": "Frontend Engineer",
        "summary": "Creative and detail-oriented Frontend Developer with 3+ years building performant responsive web apps with React, JavaScript (ES6+), HTML5/CSS3, and modern component systems.",
        "skills": ["JavaScript", "HTML/CSS", "React", "Git/GitHub", "Tailwind CSS", "Redux", "RESTful APIs", "UI/UX Design", "Communication", "Problem Solving"],
        "experience": [
            {
                "title": "Frontend Developer - PixelCraft Studios",
                "details": "PixelCraft Studios | 2023 - Present",
                "bullets": [
                    "Engineered customer dashboard in React and Tailwind CSS, increasing user engagement by 35%.",
                    "Integrated RESTful API endpoints and managed global state using Redux Toolkit.",
                    "Collaborated closely with UI/UX designers in Figma to translate wireframes into pixel-perfect components."
                ]
            },
            {
                "title": "Junior Web Developer - Digital Wave Labs",
                "details": "Digital Wave Labs | 2021 - 2023",
                "bullets": [
                    "Maintained client web interfaces with vanilla JavaScript, HTML5, CSS3, and Git version control.",
                    "Reduced page load time by 28% through asset optimization and responsive refactoring."
                ]
            }
        ],
        "education": [
            {"institution_or_degree": "B.S. in Computer Science - State University (2017 - 2021)"}
        ],
        "resume_filename": "alex_rivera_resume.pdf"
    },
    {
        "id": "cand-priya-sharma",
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "phone": "(555) 345-6789",
        "linkedin": "https://linkedin.com/in/priyasharma-data",
        "github": "https://github.com/priyasharma-data",
        "title": "Data Analyst",
        "summary": "Analytical Data Analyst with 3 years of experience extracting insights from massive datasets using SQL, Python, Pandas, and interactive dashboards.",
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Data Analysis", "Data Visualization", "Git/GitHub", "Problem Solving", "Communication", "Agile/Scrum"],
        "experience": [
            {
                "title": "Data Analyst - Insight Analytics Corp",
                "details": "Insight Analytics Corp | 2023 - Present",
                "bullets": [
                    "Constructed SQL queries and automated Python data pipelines processing 2M+ daily transactions.",
                    "Built 12+ executive dashboards visualizing churn metrics and cohort retention.",
                    "Conducted exploratory data analysis (EDA) using Pandas and Matplotlib."
                ]
            }
        ],
        "education": [
            {"institution_or_degree": "B.S. in Statistics & Data Science - Tech Institute (2019 - 2023)"}
        ],
        "resume_filename": "priya_sharma_resume.pdf"
    },
    {
        "id": "cand-marcus-chen",
        "name": "Marcus Chen",
        "email": "marcus.chen@example.com",
        "phone": "(555) 456-7890",
        "linkedin": "https://linkedin.com/in/marcuschen-devops",
        "github": "https://github.com/marcuschen",
        "title": "Cloud & DevOps Engineer",
        "summary": "Results-driven Cloud & DevOps Engineer specializing in AWS infrastructure automation, container orchestration with Docker and Kubernetes, and zero-downtime CI/CD pipelines.",
        "skills": ["Linux", "Docker", "AWS", "CI/CD", "Bash/Shell", "Git/GitHub", "Kubernetes", "PostgreSQL", "Prometheus", "Python", "Problem Solving"],
        "experience": [
            {
                "title": "DevOps Engineer - Apex Cloud Systems",
                "details": "Apex Cloud Systems | 2022 - Present",
                "bullets": [
                    "Architected automated CI/CD pipelines via GitHub Actions, decreasing release cycle from weekly to daily.",
                    "Managed AWS multi-region infrastructure (EC2, S3, RDS, ECS) with Docker containerization.",
                    "Set up centralized monitoring and alerting with Prometheus and Grafana."
                ]
            }
        ],
        "education": [
            {"institution_or_degree": "B.S. in Information Systems - Metro University (2018 - 2022)"}
        ],
        "resume_filename": "marcus_chen_resume.pdf"
    },
    {
        "id": "cand-devon-brooks",
        "name": "Devon Brooks",
        "email": "devon.brooks@example.com",
        "phone": "(555) 567-8901",
        "linkedin": "https://linkedin.com/in/devonbrooks-dev",
        "github": "https://github.com/devonbrooks",
        "title": "Python Backend Developer",
        "summary": "Backend software engineer focused on high-throughput microservices, FastAPI/Django, relational databases, and clean modular architecture.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "RESTful APIs", "Git/GitHub", "Docker", "Redis", "Linux", "Microservices", "TDD"],
        "experience": [
            {
                "title": "Backend Software Engineer - Nexus Grid Tech",
                "details": "Nexus Grid Tech | 2022 - Present",
                "bullets": [
                    "Designed high-performance RESTful APIs handling 15,000 requests/sec with FastAPI and PostgreSQL.",
                    "Implemented Redis caching layer cutting database query latency by 60%.",
                    "Wrote comprehensive unit tests and automated regression suites."
                ]
            }
        ],
        "education": [
            {"institution_or_degree": "B.S. in Software Engineering - Valley State (2018 - 2022)"}
        ],
        "resume_filename": "devon_brooks_resume.pdf"
    }
]

SEED_COMPANIES = [
    {
        "id": "comp-acme-cloud",
        "name": "Acme CloudTech",
        "industry": "Cloud Computing & SaaS",
        "location": "San Francisco, CA (Hybrid / Remote)",
        "website": "https://acmecloudtech.example.com",
        "description": "Acme CloudTech builds enterprise-grade cloud native acceleration platforms trusted by Fortune 500 engineering teams worldwide.",
        "logo_text": "AC"
    },
    {
        "id": "comp-fintech-pulse",
        "name": "FinTech Pulse",
        "industry": "Financial Technology & Trading",
        "location": "New York, NY (Hybrid)",
        "website": "https://fintechpulse.example.com",
        "description": "FinTech Pulse is revolutionizing automated quantitative algorithmic trading and real-time payment reconciliation systems.",
        "logo_text": "FP"
    },
    {
        "id": "comp-healthdata-ai",
        "name": "HealthData AI",
        "industry": "Healthcare AI & Analytics",
        "location": "Boston, MA (Remote)",
        "website": "https://healthdata-ai.example.com",
        "description": "HealthData AI develops predictive clinical diagnostics and real-time biometric analysis software for hospitals and researchers.",
        "logo_text": "HA"
    }
]

SEED_JOBS = [
    {
        "id": "job-frontend-acme",
        "company_id": "comp-acme-cloud",
        "company_name": "Acme CloudTech",
        "title": "Frontend React Engineer",
        "location": "Remote / San Francisco",
        "salary_range": "$95,000 - $125,000",
        "experience_required": "2+ years",
        "description": "We are seeking a talented Frontend Engineer to build intuitive, lightning-fast dashboard experiences for our cloud management console. You will work with React, JavaScript, HTML5/CSS3, Tailwind CSS, and RESTful APIs.",
        "required_skills": ["React", "JavaScript", "HTML/CSS", "Git/GitHub"],
        "preferred_skills": ["Tailwind CSS", "TypeScript", "Redux", "RESTful APIs", "UI/UX Design"],
        "created_at": "2026-08-25"
    },
    {
        "id": "job-backend-acme",
        "company_id": "comp-acme-cloud",
        "company_name": "Acme CloudTech",
        "title": "Python Backend & API Engineer",
        "location": "Remote",
        "salary_range": "$105,000 - $135,000",
        "experience_required": "3+ years",
        "description": "Join our Core Backend squad building scalable microservices with Python, FastAPI, and PostgreSQL. You will design resilient REST APIs, integrate Redis caching, and maintain containerized workloads.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "RESTful APIs", "Git/GitHub"],
        "preferred_skills": ["Docker", "Redis", "Linux", "Microservices", "CI/CD"],
        "created_at": "2026-08-26"
    },
    {
        "id": "job-devops-fintech",
        "company_id": "comp-fintech-pulse",
        "company_name": "FinTech Pulse",
        "title": "Cloud Infrastructure & DevOps Engineer",
        "location": "New York, NY (Hybrid)",
        "salary_range": "$115,000 - $150,000",
        "experience_required": "3+ years",
        "description": "We are looking for an experienced Cloud & DevOps Engineer to lead our AWS cloud infrastructure, Kubernetes container clusters, CI/CD automation, and Linux observability.",
        "required_skills": ["AWS", "Docker", "Linux", "CI/CD", "Bash/Shell", "Git/GitHub"],
        "preferred_skills": ["Kubernetes", "PostgreSQL", "Prometheus", "Terraform", "Python"],
        "created_at": "2026-08-27"
    },
    {
        "id": "job-data-analyst-health",
        "company_id": "comp-healthdata-ai",
        "company_name": "HealthData AI",
        "title": "Healthcare Data Analyst",
        "location": "Remote",
        "salary_range": "$85,000 - $110,000",
        "experience_required": "2+ years",
        "description": "Analyze clinical trials and patient biometric data streams using SQL, Python, Pandas, and data visualization tools. Work alongside clinicians and data scientists.",
        "required_skills": ["SQL", "Python", "Data Analysis", "Data Visualization", "Pandas"],
        "preferred_skills": ["NumPy", "Git/GitHub", "Communication", "Problem Solving"],
        "created_at": "2026-08-28"
    },
    {
        "id": "job-fullstack-fintech",
        "company_id": "comp-fintech-pulse",
        "company_name": "FinTech Pulse",
        "title": "Senior Full Stack Engineer",
        "location": "New York, NY / Remote",
        "salary_range": "$125,000 - $160,000",
        "experience_required": "4+ years",
        "description": "Lead the development of our next-generation trader workstation. Requires strong proficiency across React, Node.js or Python, PostgreSQL, and scalable REST/WebSocket APIs.",
        "required_skills": ["JavaScript", "React", "Python", "PostgreSQL", "RESTful APIs", "Git/GitHub"],
        "preferred_skills": ["Docker", "AWS", "TypeScript", "Redis", "Tailwind CSS"],
        "created_at": "2026-08-29"
    },
    {
        "id": "job-ml-health",
        "company_id": "comp-healthdata-ai",
        "company_name": "HealthData AI",
        "title": "Machine Learning Engineer (Health AI)",
        "location": "Boston, MA / Remote",
        "salary_range": "$135,000 - $180,000",
        "experience_required": "3+ years",
        "description": "Design, train, and deploy deep learning and NLP models for biomedical literature extraction and diagnosis prediction pipelines.",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "RESTful APIs", "Docker", "Git/GitHub"],
        "preferred_skills": ["Natural Language Processing (NLP)", "FastAPI", "Deep Learning", "AWS", "Kubernetes"],
        "created_at": "2026-08-30"
    }
]


def generate_sample_pdf_resumes():
    """Generates authentic PDF resume files in sample_data/resumes/ using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        RESUMES_DIR.mkdir(parents=True, exist_ok=True)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'CandTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#2A2A2A"),
            alignment=TA_CENTER
        )
        subtitle_style = ParagraphStyle(
            'CandSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#5E83AE"),
            alignment=TA_CENTER
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#2A2A2A"),
            spaceBefore=10,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#333333")
        )
        bold_body = ParagraphStyle(
            'BoldBody',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#2A2A2A")
        )

        for cand in SEED_CANDIDATES:
            pdf_path = RESUMES_DIR / cand["resume_filename"]
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )
            story = []

            # Header
            story.append(Paragraph(cand["name"], title_style))
            contact_str = f"{cand['title']} | {cand['email']} | {cand['phone']} | {cand['github']}"
            story.append(Paragraph(contact_str, subtitle_style))
            story.append(Spacer(1, 8))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#5E83AE"), spaceAfter=10))

            # Summary
            story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
            story.append(Paragraph(cand["summary"], body_style))
            story.append(Spacer(1, 6))

            # Skills
            story.append(Paragraph("TECHNICAL SKILLS", section_heading))
            skills_str = " • ".join(cand["skills"])
            story.append(Paragraph(skills_str, body_style))
            story.append(Spacer(1, 6))

            # Experience
            story.append(Paragraph("WORK EXPERIENCE", section_heading))
            for exp in cand["experience"]:
                story.append(Paragraph(exp["title"], bold_body))
                story.append(Paragraph(exp["details"], subtitle_style))
                for bullet in exp["bullets"]:
                    story.append(Paragraph(f"• {bullet}", body_style))
                story.append(Spacer(1, 4))

            # Education
            story.append(Paragraph("EDUCATION", section_heading))
            for edu in cand["education"]:
                story.append(Paragraph(edu["institution_or_degree"], body_style))

            doc.build(story)
            print(f"Generated sample PDF resume: {pdf_path}")
    except Exception as e:
        print(f"Notice: Could not build PDF with reportlab ({e}). Continuing with text seed data.")


async def initialize_seed_data():
    """Seeds the database with candidate profiles, companies, and jobs if empty."""
    db = get_db()

    # Generate sample PDFs
    generate_sample_pdf_resumes()

    # Candidates
    cand_col = db.get_collection("candidates")
    count = await cand_col.count_documents()
    if count == 0:
        for cand in SEED_CANDIDATES:
            await cand_col.insert_one(cand)
        print(f"Seeded {len(SEED_CANDIDATES)} candidates.")

    # Companies
    comp_col = db.get_collection("companies")
    comp_count = await comp_col.count_documents()
    if comp_count == 0:
        for comp in SEED_COMPANIES:
            await comp_col.insert_one(comp)
        print(f"Seeded {len(SEED_COMPANIES)} companies.")

    # Jobs
    job_col = db.get_collection("jobs")
    job_count = await job_col.count_documents()
    if job_count == 0:
        for job in SEED_JOBS:
            await job_col.insert_one(job)
        print(f"Seeded {len(SEED_JOBS)} jobs.")
