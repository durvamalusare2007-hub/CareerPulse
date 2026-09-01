from typing import Any, Dict, List, Optional, Set
import math

# Standardized Career Role Taxonomy
STANDARDIZED_ROLES: List[Dict[str, Any]] = [
    {
        "id": "frontend-dev",
        "title": "Frontend Developer",
        "category": "Software Engineering",
        "level": "Mid-Level",
        "salary_range": "$85,000 - $120,000",
        "required_skills": ["JavaScript", "HTML/CSS", "React", "Git/GitHub"],
        "preferred_skills": ["TypeScript", "Tailwind CSS", "Redux", "RESTful APIs", "UI/UX Design"],
        "description": "Build responsive, high-performance web user interfaces, collaborate with product designers, and integrate backend REST/GraphQL APIs.",
        "future_role_paths": ["fullstack-dev", "frontend-lead", "ui-ux-engineer"]
    },
    {
        "id": "backend-dev-python",
        "title": "Python Backend Developer",
        "category": "Software Engineering",
        "level": "Mid-Level",
        "salary_range": "$95,000 - $130,000",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "RESTful APIs", "Git/GitHub"],
        "preferred_skills": ["Docker", "Redis", "CI/CD", "Linux", "Microservices"],
        "description": "Design and build scalable server-side applications, database schemas, RESTful APIs, and asynchronous microservices.",
        "future_role_paths": ["fullstack-dev", "cloud-devops-engineer", "data-engineer", "ml-engineer"]
    },
    {
        "id": "fullstack-dev",
        "title": "Full Stack Engineer",
        "category": "Software Engineering",
        "level": "Senior",
        "salary_range": "$115,000 - $155,000",
        "required_skills": ["JavaScript", "Python", "React", "Node.js", "PostgreSQL", "RESTful APIs", "Git/GitHub"],
        "preferred_skills": ["TypeScript", "Docker", "AWS", "Redis", "CI/CD", "Tailwind CSS"],
        "description": "Architect and implement end-to-end full stack web platforms, from reactive frontends to robust distributed backend APIs and databases.",
        "future_role_paths": ["engineering-lead", "solutions-architect", "cloud-devops-engineer"]
    },
    {
        "id": "data-analyst",
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "level": "Mid-Level",
        "salary_range": "$80,000 - $110,000",
        "required_skills": ["SQL", "Python", "Data Analysis", "Data Visualization", "Pandas"],
        "preferred_skills": ["NumPy", "Git/GitHub", "Communication", "Problem Solving"],
        "description": "Transform complex datasets into actionable business intelligence, build interactive dashboards, and perform exploratory statistical analysis.",
        "future_role_paths": ["data-scientist", "data-engineer", "bi-lead"]
    },
    {
        "id": "data-scientist",
        "title": "Data Scientist",
        "category": "Data & Analytics",
        "level": "Senior",
        "salary_range": "$120,000 - $160,000",
        "required_skills": ["Python", "SQL", "Machine Learning", "Data Analysis", "Pandas", "Scikit-Learn"],
        "preferred_skills": ["Deep Learning", "TensorFlow", "PyTorch", "Data Visualization", "Statistics"],
        "description": "Develop predictive machine learning models, statistical experiments, and algorithmic solutions to drive key product and business outcomes.",
        "future_role_paths": ["ml-engineer", "ai-researcher", "data-science-lead"]
    },
    {
        "id": "ml-engineer",
        "title": "Machine Learning Engineer",
        "category": "AI & Machine Learning",
        "level": "Senior",
        "salary_range": "$135,000 - $185,000",
        "required_skills": ["Python", "Machine Learning", "PyTorch", "Docker", "RESTful APIs", "Git/GitHub"],
        "preferred_skills": ["Natural Language Processing (NLP)", "Deep Learning", "FastAPI", "Kubernetes", "AWS", "Generative AI"],
        "description": "Train, evaluate, optimize, and deploy production machine learning and deep learning pipelines and real-time inference APIs.",
        "future_role_paths": ["ai-architect", "engineering-lead"]
    },
    {
        "id": "cloud-devops-engineer",
        "title": "Cloud & DevOps Engineer",
        "category": "Infrastructure & Cloud",
        "level": "Mid-Senior",
        "salary_range": "$110,000 - $150,000",
        "required_skills": ["Linux", "Docker", "AWS", "CI/CD", "Bash/Shell", "Git/GitHub"],
        "preferred_skills": ["Kubernetes", "Terraform", "PostgreSQL", "Prometheus", "Python"],
        "description": "Automate cloud infrastructure provisioning, CI/CD pipelines, container orchestration, monitoring, and high-availability deployments.",
        "future_role_paths": ["solutions-architect", "site-reliability-lead", "devops-architect"]
    },
    {
        "id": "solutions-architect",
        "title": "Cloud Solutions Architect",
        "category": "Architecture & Strategy",
        "level": "Staff / Lead",
        "salary_range": "$160,000 - $215,000",
        "required_skills": ["AWS", "System Design", "Microservices", "Docker", "Kubernetes", "PostgreSQL", "CI/CD"],
        "preferred_skills": ["Terraform", "Kafka", "Security", "Leadership", "Communication"],
        "description": "Design resilient, scalable, enterprise-grade cloud architectures, evaluate technical trade-offs, and guide engineering teams.",
        "future_role_paths": ["principal-architect", "cto"]
    },
    {
        "id": "engineering-lead",
        "title": "Engineering Team Lead",
        "category": "Engineering Management",
        "level": "Lead",
        "salary_range": "$150,000 - $195,000",
        "required_skills": ["Leadership", "Agile/Scrum", "Git/GitHub", "System Design", "Communication", "Problem Solving"],
        "preferred_skills": ["Microservices", "CI/CD", "Full Stack Experience", "Time Management"],
        "description": "Lead high-performing agile engineering squads, mentor engineers, manage technical delivery, and align product roadmaps.",
        "future_role_paths": ["engineering-director", "vp-engineering"]
    },
    {
        "id": "qa-automation-engineer",
        "title": "QA Automation Engineer",
        "category": "Quality Engineering",
        "level": "Mid-Level",
        "salary_range": "$80,000 - $115,000",
        "required_skills": ["Python", "Test-Driven Development (TDD)", "Git/GitHub", "RESTful APIs", "Bash/Shell"],
        "preferred_skills": ["Docker", "CI/CD", "Postman", "JavaScript", "Linux"],
        "description": "Design, implement, and maintain automated test suites, end-to-end regression frameworks, and continuous quality pipelines.",
        "future_role_paths": ["backend-dev-python", "cloud-devops-engineer", "qa-lead"]
    }
]


# Skill Learning Resource & Project Catalog
SKILL_LEARNING_DATA: Dict[str, Dict[str, Any]] = {
    "Docker": {
        "difficulty": "Moderate",
        "est_weeks": 2,
        "summary": "Containerize applications for consistent local development and cloud production deployment.",
        "resources": [
            {"title": "Docker Official Getting Started Guide", "url": "https://docs.docker.com/get-started/", "type": "Documentation"},
            {"title": "Docker for Beginners (FreeCodeCamp)", "url": "https://www.freecodecamp.org/news/what-is-docker-used-for-a-docker-container-tutorial-for-beginners/", "type": "Tutorial"},
            {"title": "Docker Compose Multi-Container Guide", "url": "https://docs.docker.com/compose/", "type": "Guide"}
        ],
        "project_idea": "Multi-container application packaging a React frontend, FastAPI backend, and PostgreSQL database with Docker Compose.",
        "milestones": [
            "Write your first Dockerfile and build an image.",
            "Run containers and bind host ports/volumes.",
            "Orchestrate a 3-tier app using Docker Compose."
        ]
    },
    "Kubernetes": {
        "difficulty": "Advanced",
        "est_weeks": 3,
        "summary": "Automate container deployment, scaling, load balancing, and fault tolerance in clustered environments.",
        "resources": [
            {"title": "Kubernetes Official Basics Tutorial", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "type": "Official Tutorial"},
            {"title": "Minikube Local Cluster Setup", "url": "https://minikube.sigs.k8s.io/docs/start/", "type": "Hands-on Lab"}
        ],
        "project_idea": "Deploy a high-availability microservice with Deployments, Services, ConfigMaps, Ingress, and auto-scaling rules.",
        "milestones": [
            "Set up Minikube or Kind cluster locally.",
            "Write manifests for Deployments, Pods, and Services.",
            "Implement rolling updates and zero-downtime rollbacks."
        ]
    },
    "AWS": {
        "difficulty": "Moderate-Advanced",
        "est_weeks": 3,
        "summary": "Master core cloud infrastructure services including compute (EC2/Lambda), storage (S3), databases (RDS), and IAM security.",
        "resources": [
            {"title": "AWS Free Tier & Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "type": "Course"},
            {"title": "Serverless APIs with AWS Lambda & API Gateway", "url": "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html", "type": "Documentation"}
        ],
        "project_idea": "Build a serverless image processing pipeline using S3 event triggers, AWS Lambda, and DynamoDB.",
        "milestones": [
            "Configure IAM roles, policies, and least-privilege security.",
            "Host static assets in S3 with CloudFront CDN.",
            "Deploy a containerized API to AWS ECS or App Runner."
        ]
    },
    "TypeScript": {
        "difficulty": "Moderate",
        "est_weeks": 2,
        "summary": "Add compile-time type safety, interfaces, generics, and strict tooling to JavaScript codebases.",
        "resources": [
            {"title": "TypeScript for JavaScript Programmers Handbook", "url": "https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html", "type": "Documentation"},
            {"title": "Total TypeScript Interactive Cheatsheet", "url": "https://www.totaltypescript.com/tutorials", "type": "Interactive Guide"}
        ],
        "project_idea": "Refactor an existing React + Node.js application into strict TypeScript with shared data models.",
        "milestones": [
            "Understand primitive types, unions, and interfaces.",
            "Master Generics and Utility Types (Partial, Omit, Record).",
            "Integrate TypeScript with React components and API client."
        ]
    },
    "Machine Learning": {
        "difficulty": "Advanced",
        "est_weeks": 4,
        "summary": "Understand feature engineering, classification, regression, cross-validation, and model evaluation metrics.",
        "resources": [
            {"title": "Scikit-Learn Official User Guide", "url": "https://scikit-learn.org/stable/user_guide.html", "type": "Documentation"},
            {"title": "Kaggle Machine Learning Micro-Courses", "url": "https://www.kaggle.com/learn", "type": "Interactive Course"}
        ],
        "project_idea": "Build an end-to-end customer churn prediction pipeline with hyperparameter tuning and model explainability (SHAP).",
        "milestones": [
            "Clean and preprocess tabular data with Pandas & Scikit-learn.",
            "Train and benchmark Random Forest, XGBoost, and Logistic Regression.",
            "Evaluate precision, recall, ROC-AUC and prevent data leakage."
        ]
    },
    "PyTorch": {
        "difficulty": "Advanced",
        "est_weeks": 3,
        "summary": "Build and train neural networks, custom loss functions, and transfer learning models using PyTorch tensors and autograd.",
        "resources": [
            {"title": "Deep Learning with PyTorch: A 60 Minute Blitz", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html", "type": "Tutorial"},
            {"title": "Hugging Face Course on Transformers", "url": "https://huggingface.co/course/chapter1/1", "type": "Course"}
        ],
        "project_idea": "Fine-tune a pre-trained Transformer model for sentiment classification or text embeddings.",
        "milestones": [
            "Understand Tensors, Autograd, and Module architectures.",
            "Write standard training and validation loops with optimizers.",
            "Save, load, and run inference on GPU/CPU."
        ]
    },
    "Microservices": {
        "difficulty": "Advanced",
        "est_weeks": 3,
        "summary": "Design decoupled, independently deployable services communicating over REST, gRPC, and asynchronous message brokers.",
        "resources": [
            {"title": "Microservices Patterns by Chris Richardson", "url": "https://microservices.io/patterns/microservices.html", "type": "Architecture Guide"},
            {"title": "Designing Distributed Systems (Martin Fowler)", "url": "https://martinfowler.com/articles/microservices.html", "type": "Article"}
        ],
        "project_idea": "Build an E-Commerce Order & Inventory system with asynchronous event publishing via Kafka or Redis.",
        "milestones": [
            "Decompose a monolithic domain into service boundaries.",
            "Implement asynchronous event publishing with transactional outbox.",
            "Handle distributed tracing and circuit breaker patterns."
        ]
    },
    "CI/CD": {
        "difficulty": "Moderate",
        "est_weeks": 2,
        "summary": "Automate continuous testing, linting, security audits, and deployment pipelines using GitHub Actions or GitLab CI.",
        "resources": [
            {"title": "GitHub Actions Official Quickstart", "url": "https://docs.github.com/en/actions/quickstart", "type": "Documentation"},
            {"title": "CI/CD Pipeline Best Practices Guide", "url": "https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment", "type": "Guide"}
        ],
        "project_idea": "Create a GitHub Actions workflow that runs automated unit tests, builds a Docker image, and deploys to a staging server.",
        "milestones": [
            "Write workflow YAML triggers on pull requests and pushes.",
            "Set up secret management and caching for dependencies.",
            "Implement multi-stage matrix testing and deployment gates."
        ]
    }
}


def calculate_current_skill_role_recommendations(
    user_skills: List[str],
    company_jobs: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    STRICT CURRENT-SKILL MATCHING:
    Evaluates standardized roles and active company jobs ONLY against the skills the user already possesses.
    A user is NEVER told to learn new skills before being shown roles they already qualify for.
    """
    user_skill_set = {s.lower() for s in user_skills}
    recommendations = []

    for role in STANDARDIZED_ROLES:
        req_skills = role["required_skills"]
        pref_skills = role.get("preferred_skills", [])

        matched_req = [s for s in req_skills if s.lower() in user_skill_set]
        missing_req = [s for s in req_skills if s.lower() not in user_skill_set]
        matched_pref = [s for s in pref_skills if s.lower() in user_skill_set]
        missing_pref = [s for s in pref_skills if s.lower() not in user_skill_set]

        # Calculate percentage based strictly on required skills
        req_match_pct = round((len(matched_req) / len(req_skills)) * 100) if req_skills else 100
        
        # Overall qualification metric
        is_qualified = req_match_pct >= 50 or (len(matched_req) >= 2 and len(matched_req) >= len(req_skills) - 1)
        
        # Determine match tier
        if req_match_pct >= 85:
            match_tier = "Excellent Match"
            tier_badge = "success"
        elif req_match_pct >= 65:
            match_tier = "Strong Match"
            tier_badge = "primary"
        elif req_match_pct >= 45:
            match_tier = "Potential Match"
            tier_badge = "warning"
        else:
            match_tier = "Stretch Match"
            tier_badge = "neutral"

        # Find matching company open positions if provided
        open_jobs_count = 0
        matching_company_postings = []
        if company_jobs:
            for job in company_jobs:
                job_title = job.get("title", "").lower()
                role_title = role["title"].lower()
                if job_title in role_title or role_title in job_title or any(w in job_title for w in role_title.split()):
                    open_jobs_count += 1
                    matching_company_postings.append({
                        "job_id": job.get("id"),
                        "company_name": job.get("company_name", "Partner Company"),
                        "title": job.get("title"),
                        "location": job.get("location"),
                        "experience_required": job.get("experience_required"),
                        "salary_range": job.get("salary_range")
                    })

        rec = {
            "role_id": role["id"],
            "title": role["title"],
            "category": role["category"],
            "level": role["level"],
            "salary_range": role["salary_range"],
            "description": role["description"],
            "match_percentage": req_match_pct,
            "match_tier": match_tier,
            "tier_badge": tier_badge,
            "is_qualified": is_qualified,
            "matched_required_skills": matched_req,
            "missing_required_skills": missing_req,
            "matched_preferred_skills": matched_pref,
            "missing_preferred_skills": missing_pref,
            "total_user_skills_used": len(matched_req) + len(matched_pref),
            "future_role_paths": role.get("future_role_paths", []),
            "open_jobs_count": open_jobs_count,
            "company_postings": matching_company_postings[:3]
        }
        recommendations.append(rec)

    # Sort descending by match percentage, putting roles the user qualifies for at the top!
    recommendations.sort(key=lambda x: (-x["match_percentage"], -x["total_user_skills_used"]))
    return recommendations


def analyze_skill_gap_for_role(
    target_role_id: str,
    user_skills: List[str]
) -> Dict[str, Any]:
    """
    Computes detailed skill gap analysis between the user's current skills and a target/stretch future role.
    """
    user_skill_set = {s.lower() for s in user_skills}
    target_role = next((r for r in STANDARDIZED_ROLES if r["id"] == target_role_id), None)
    if not target_role:
        return {"error": f"Role '{target_role_id}' not found."}

    req_skills = target_role["required_skills"]
    pref_skills = target_role.get("preferred_skills", [])

    matched_req = [s for s in req_skills if s.lower() in user_skill_set]
    missing_req = [s for s in req_skills if s.lower() not in user_skill_set]
    matched_pref = [s for s in pref_skills if s.lower() in user_skill_set]
    missing_pref = [s for s in pref_skills if s.lower() not in user_skill_set]

    all_target_skills = req_skills + pref_skills
    all_matched = matched_req + matched_pref
    current_readiness = round((len(all_matched) / len(all_target_skills)) * 100) if all_target_skills else 100

    # Detail each missing skill
    gap_breakdown = []
    total_est_weeks = 0

    all_missing = missing_req + missing_pref
    for skill in all_missing:
        is_core = skill in missing_req
        learn_info = SKILL_LEARNING_DATA.get(skill, {
            "difficulty": "Moderate",
            "est_weeks": 2,
            "summary": f"Core competency in {skill} to unlock advanced capabilities.",
            "resources": [
                {"title": f"Learn {skill} - Official Documentation", "url": f"https://www.google.com/search?q={skill}+official+documentation", "type": "Documentation"},
                {"title": f"{skill} Practical Hands-on Tutorial", "url": f"https://www.google.com/search?q={skill}+hands+on+tutorial", "type": "Tutorial"}
            ],
            "project_idea": f"Implement a standalone project incorporating {skill} within your current stack.",
            "milestones": [
                f"Master core syntax and setup for {skill}.",
                f"Build a feature using {skill}.",
                f"Integrate {skill} with your current portfolio."
            ]
        })
        
        weeks = learn_info.get("est_weeks", 2)
        total_est_weeks += weeks

        gap_breakdown.append({
            "skill": skill,
            "importance": "Mandatory Requirement" if is_core else "High-Value Advantage",
            "is_core": is_core,
            "difficulty": learn_info.get("difficulty", "Moderate"),
            "est_weeks": weeks,
            "summary": learn_info.get("summary"),
            "resources": learn_info.get("resources", []),
            "project_idea": learn_info.get("project_idea"),
            "milestones": learn_info.get("milestones", [])
        })

    # Sort gaps so mandatory core requirements come first
    gap_breakdown.sort(key=lambda x: (not x["is_core"], x["skill"]))

    return {
        "target_role": target_role,
        "current_readiness_pct": current_readiness,
        "matched_skills": all_matched,
        "missing_skills_count": len(all_missing),
        "gap_breakdown": gap_breakdown,
        "estimated_total_learning_weeks": max(2, math.ceil(total_est_weeks * 0.75)), # parallel learning adjustment
        "career_impact": {
            "salary_potential": target_role["salary_range"],
            "seniority_level": target_role["level"],
            "market_demand": "High Demand across 2026 Tech Hiring"
        }
    }


def generate_personalized_roadmap(
    target_role_id: str,
    user_skills: List[str]
) -> Dict[str, Any]:
    """
    Generates a structured, week-by-week personalized learning roadmap to transition from current skills to target role.
    """
    gap_analysis = analyze_skill_gap_for_role(target_role_id, user_skills)
    if "error" in gap_analysis:
        return gap_analysis

    target_role = gap_analysis["target_role"]
    gaps = gap_analysis["gap_breakdown"]

    modules = []
    current_week = 1

    if not gaps:
        # User already possesses all skills for this role!
        modules.append({
            "phase": "Phase 1: Portfolio & Interview Readiness",
            "weeks": "Week 1 - 2",
            "focus_skills": gap_analysis["matched_skills"][:4],
            "title": "Showcase Mastery & System Design",
            "description": "You already possess the core skills for this role! Focus on system design, performance optimization, and interviewing.",
            "tasks": [
                "Polish your GitHub portfolio with complete READMEs and live demos.",
                "Review system design trade-offs and architectural patterns.",
                "Prepare for technical interviews with behavioral and scenario questions."
            ],
            "project": "End-to-End Production Capstone showcasing existing skills.",
            "resources": [
                {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "type": "Repository"},
                {"title": "Tech Interview Handbook", "url": "https://www.techinterviewhandbook.org/", "type": "Guide"}
            ]
        })
    else:
        # Group gaps into progressive phases
        for idx, gap in enumerate(gaps[:4]):  # Top priority 3-4 skills
            duration = gap.get("est_weeks", 2)
            end_week = current_week + duration - 1
            week_str = f"Week {current_week}" if current_week == end_week else f"Weeks {current_week} - {end_week}"
            
            phase_num = idx + 1
            modules.append({
                "phase": f"Phase {phase_num}: Master {gap['skill']}",
                "weeks": week_str,
                "focus_skills": [gap["skill"]],
                "importance": gap["importance"],
                "difficulty": gap["difficulty"],
                "title": f"Foundations to Real-World {gap['skill']}",
                "description": gap["summary"],
                "tasks": gap.get("milestones", []),
                "project": gap.get("project_idea"),
                "resources": gap.get("resources", [])
            })
            current_week = end_week + 1

        # Capstone Integration Phase
        modules.append({
            "phase": f"Phase {len(modules) + 1}: Final Capstone & Role Portfolio",
            "weeks": f"Weeks {current_week} - {current_week + 1}",
            "focus_skills": [g["skill"] for g in gaps[:3]] + gap_analysis["matched_skills"][:2],
            "importance": "Career Milestone",
            "difficulty": "Comprehensive",
            "title": f"{target_role['title']} Full-Stack Integration Capstone",
            "description": f"Combine your newly acquired skills with your existing foundation to build a production-grade application tailored for {target_role['title']} hiring managers.",
            "tasks": [
                "Architect a multi-component application solving a real business problem.",
                "Implement CI/CD automated deployment with monitoring.",
                "Write comprehensive test coverage and technical documentation."
            ],
            "project": f"Production-grade {target_role['title']} Capstone Repository with live demo.",
            "resources": [
                {"title": "Awesome Production Best Practices", "url": "https://github.com/", "type": "Guide"}
            ]
        })

    return {
        "target_role_id": target_role["id"],
        "target_role_title": target_role["title"],
        "target_role_level": target_role["level"],
        "target_role_salary": target_role["salary_range"],
        "current_readiness_pct": gap_analysis["current_readiness_pct"],
        "existing_foundation_skills": gap_analysis["matched_skills"],
        "skills_to_acquire": [g["skill"] for g in gaps],
        "total_estimated_weeks": current_week + 1 if gaps else 2,
        "learning_modules": modules
    }


def rank_candidates_for_job(
    job: Dict[str, Any],
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Ranks registered job seekers against a company's job requirements.
    Matches required and preferred skills with weighted hybrid scoring.
    """
    req_skills = job.get("required_skills", [])
    pref_skills = job.get("preferred_skills", [])
    req_skill_set = {s.lower() for s in req_skills}
    pref_skill_set = {s.lower() for s in pref_skills}

    ranked = []
    for cand in candidates:
        cand_skills = cand.get("skills", [])
        cand_skill_set = {s.lower() for s in cand_skills}

        matched_req = [s for s in req_skills if s.lower() in cand_skill_set]
        missing_req = [s for s in req_skills if s.lower() not in cand_skill_set]
        
        matched_pref = [s for s in pref_skills if s.lower() in cand_skill_set]
        missing_pref = [s for s in pref_skills if s.lower() not in cand_skill_set]

        req_score = (len(matched_req) / len(req_skills)) * 100 if req_skills else 100
        pref_score = (len(matched_pref) / len(pref_skills)) * 100 if pref_skills else 50

        # Overall composite match score (70% required, 30% preferred)
        overall_score = round(req_score * 0.75 + pref_score * 0.25)
        
        # Fit tier badge
        if overall_score >= 80:
            tier = "Top Fit"
            tier_color = "emerald"
        elif overall_score >= 60:
            tier = "Strong Candidate"
            tier_color = "blue"
        elif overall_score >= 40:
            tier = "Partial Fit"
            tier_color = "amber"
        else:
            tier = "Low Match"
            tier_color = "slate"

        ranked.append({
            "candidate_id": cand.get("id"),
            "name": cand.get("name", "Candidate"),
            "title": cand.get("title") or (cand.get("experience", [{}])[0].get("title") if cand.get("experience") else "Software Professional"),
            "email": cand.get("email"),
            "phone": cand.get("phone"),
            "summary": cand.get("summary"),
            "match_score": overall_score,
            "req_match_percentage": round(req_score),
            "pref_match_percentage": round(pref_score),
            "tier": tier,
            "tier_color": tier_color,
            "matched_required_skills": matched_req,
            "missing_required_skills": missing_req,
            "matched_preferred_skills": matched_pref,
            "total_candidate_skills": len(cand_skills),
            "skills": cand_skills,
            "experience": cand.get("experience", []),
            "education": cand.get("education", []),
            "resume_filename": cand.get("resume_filename")
        })

    # Sort descending by match score
    ranked.sort(key=lambda x: (-x["match_score"], -len(x["matched_required_skills"])))
    return ranked
