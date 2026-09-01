import re
from typing import Any, Dict, List, Set, Tuple

# Comprehensive taxonomy of skills categorized into 8 domains
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": {
        "Python": ["python", "python3", "py", "cpython"],
        "JavaScript": ["javascript", "js", "ecmascript", "es6", "es2020"],
        "TypeScript": ["typescript", "ts"],
        "Java": ["java", "j2ee", "core java", "java 8", "java 11", "java 17"],
        "C++": ["c++", "cpp", "c/c++"],
        "C#": ["c#", "csharp", ".net c#"],
        "Go": ["go", "golang"],
        "Rust": ["rust", "rustlang"],
        "Ruby": ["ruby", "ruby on rails", "ror"],
        "PHP": ["php", "php7", "php8"],
        "SQL": ["sql", "t-sql", "pl/sql", "ansi sql"],
        "HTML/CSS": ["html", "html5", "css", "css3", "sass", "scss", "less"],
        "Bash/Shell": ["bash", "shell", "powershell", "zsh", "sh", "shell scripting"],
        "Kotlin": ["kotlin"],
        "Swift": ["swift", "swiftui"],
        "R": ["r", "r-lang", "r programming"],
        "Scala": ["scala"],
    },
    "Frameworks & Libraries": {
        "React": ["react", "react.js", "reactjs", "react-dom", "react native"],
        "Node.js": ["node.js", "nodejs", "node", "express", "express.js", "nest.js", "nestjs"],
        "Vue.js": ["vue", "vue.js", "vuejs", "vue3", "nuxt", "nuxtjs"],
        "Angular": ["angular", "angular.js", "angularjs", "angular 2+"],
        "Django": ["django", "django rest framework", "drf"],
        "FastAPI": ["fastapi", "fast api"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "spring framework", "spring", "spring mvc"],
        "Next.js": ["next.js", "nextjs", "next"],
        "Tailwind CSS": ["tailwind", "tailwind css", "tailwindcss"],
        "Bootstrap": ["bootstrap", "bootstrap 5"],
        "ASP.NET": ["asp.net", "asp.net core", ".net core", "dotnet core"],
        "GraphQL": ["graphql", "apollo", "relay"],
        "Redux": ["redux", "redux toolkit", "rtk"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "TensorFlow": ["tensorflow", "tf"],
        "PyTorch": ["pytorch", "torch"],
        "Keras": ["keras"],
        "OpenCV": ["opencv", "cv2"],
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "ecs", "eks", "rds", "cloudformation", "iam"],
        "Azure": ["azure", "microsoft azure", "azure devops", "azure functions", "blob storage", "aks"],
        "Google Cloud (GCP)": ["gcp", "google cloud", "google cloud platform", "bigquery", "gcs", "gke", "cloud run"],
        "Docker": ["docker", "dockerfile", "docker-compose", "containerization", "containers"],
        "Kubernetes": ["kubernetes", "k8s", "helm", "kubectl"],
        "CI/CD": ["ci/cd", "continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins", "circleci", "travis ci", "argo cd"],
        "Terraform": ["terraform", "iac", "infrastructure as code"],
        "Linux": ["linux", "ubuntu", "debian", "centos", "redhat", "unix", "posix"],
        "Nginx": ["nginx"],
        "Ansible": ["ansible"],
        "Prometheus": ["prometheus", "grafana", "monitoring", "observability", "datadog", "elk stack", "splunk"],
    },
    "Databases & Storage": {
        "PostgreSQL": ["postgresql", "postgres", "psql"],
        "MySQL": ["mysql", "mariadb"],
        "MongoDB": ["mongodb", "mongo", "nosql", "documentdb"],
        "Redis": ["redis", "in-memory cache", "caching"],
        "Elasticsearch": ["elasticsearch", "elastic search", "opensearch"],
        "SQLite": ["sqlite", "sqlite3"],
        "Oracle DB": ["oracle", "oracle database"],
        "DynamoDB": ["dynamodb", "amazon dynamodb"],
        "Firebase": ["firebase", "firestore", "realtime database"],
        "Snowflake": ["snowflake"],
        "Kafka": ["kafka", "apache kafka", "event streaming", "message broker", "rabbitmq"],
    },
    "AI, ML & Data Science": {
        "Machine Learning": ["machine learning", "ml", "supervised learning", "unsupervised learning", "model training", "predictive modeling"],
        "Deep Learning": ["deep learning", "neural networks", "cnn", "rnn", "transformers", "lstm"],
        "Natural Language Processing (NLP)": ["nlp", "natural language processing", "spacy", "nltk", "hugging face", "llm", "large language models", "bert", "gpt", "rag", "embeddings", "langchain"],
        "Computer Vision": ["computer vision", "image processing", "object detection", "yolo", "segmentation"],
        "Data Analysis": ["data analysis", "data analytics", "exploratory data analysis", "eda", "statistical analysis", "statistics"],
        "Data Engineering": ["data engineering", "etl", "elt", "data pipeline", "airflow", "spark", "apache spark", "dbt"],
        "Data Visualization": ["data visualization", "tableau", "power bi", "matplotlib", "seaborn", "plotly", "looker"],
        "Generative AI": ["generative ai", "genai", "prompt engineering", "openai api", "fine-tuning", "diffusion models"],
    },
    "Design & Product Tools": {
        "Figma": ["figma"],
        "UI/UX Design": ["ui/ux", "ui design", "ux design", "user experience", "wireframing", "prototyping", "user research"],
        "Git/GitHub": ["git", "github", "gitlab", "bitbucket", "version control"],
        "Jira": ["jira", "confluence", "trello", "asana"],
        "Postman": ["postman", "swagger", "api testing", "openapi"],
    },
    "Methodologies & Practices": {
        "Agile/Scrum": ["agile", "scrum", "kanban", "sprint planning", "retrospectives"],
        "RESTful APIs": ["rest", "restful", "rest api", "restful api", "api design", "web services"],
        "Microservices": ["microservices", "microservice architecture", "distributed systems"],
        "Test-Driven Development (TDD)": ["tdd", "test driven development", "unit testing", "jest", "pytest", "cypress", "selenium", "integration testing"],
        "Clean Architecture": ["clean code", "clean architecture", "solid principles", "design patterns", "oop", "object oriented programming"],
        "System Design": ["system design", "scalability", "high availability", "load balancing", "fault tolerance"],
    },
    "Soft Skills": {
        "Communication": ["communication", "technical communication", "presentation skills", "verbal communication", "written communication"],
        "Leadership": ["leadership", "team leadership", "mentorship", "leading teams", "tech lead", "project management"],
        "Problem Solving": ["problem solving", "analytical thinking", "critical thinking", "troubleshooting", "debugging"],
        "Collaboration": ["collaboration", "cross-functional", "team player", "teamwork", "stakeholder management"],
        "Time Management": ["time management", "prioritization", "multitasking", "delivery"],
        "Adaptability": ["adaptability", "quick learner", "fast learner", "growth mindset"],
    }
}

# Build flat lookup map of aliases to canonical skill names and categories
CANONICAL_LOOKUP: Dict[str, Tuple[str, str]] = {}
for category, skills in SKILL_TAXONOMY.items():
    for canonical_name, aliases in skills.items():
        # Canonical name itself
        CANONICAL_LOOKUP[canonical_name.lower()] = (canonical_name, category)
        for alias in aliases:
            CANONICAL_LOOKUP[alias.lower()] = (canonical_name, category)


def normalize_text(text: str) -> str:
    """Clean and normalize text for robust token/phrase matching."""
    text = text.lower()
    # Normalize slashes and dots in known tech terms
    text = re.sub(r'[^\w\s\+\#\.\/\-]', ' ', text)
    return text


def extract_skills_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts all standardized skills present in a text string.
    Returns:
      - skills: list of unique canonical skill names
      - categorized: dict of category -> list of canonical skill names
      - skill_details: list of dicts with name, category, frequency, and matched aliases
    """
    if not text:
        return {"skills": [], "categorized": {}, "skill_details": []}

    cleaned_text = normalize_text(text)
    # Token set and bigram/trigram phrases for matching
    words = cleaned_text.split()
    
    found_canonical: Dict[str, Dict[str, Any]] = {}

    # Sort lookup aliases by length descending so longer phrases match first (e.g. "amazon web services" before "web")
    sorted_aliases = sorted(CANONICAL_LOOKUP.keys(), key=lambda x: len(x), reverse=True)

    for alias in sorted_aliases:
        canonical_name, category = CANONICAL_LOOKUP[alias]
        
        # Regex boundary match to avoid partial substrings (e.g. "go" in "good")
        # Handle special characters in regex
        escaped_alias = re.escape(alias)
        # If alias starts/ends with word char, use \b boundary
        prefix = r'(?:\b|^)' if alias[0].isalnum() else ''
        suffix = r'(?:\b|$)' if alias[-1].isalnum() else ''
        pattern = f"{prefix}{escaped_alias}{suffix}"

        matches = list(re.finditer(pattern, cleaned_text))
        if matches:
            count = len(matches)
            if canonical_name not in found_canonical:
                found_canonical[canonical_name] = {
                    "name": canonical_name,
                    "category": category,
                    "count": count,
                    "matched_terms": [alias]
                }
            else:
                found_canonical[canonical_name]["count"] += count
                if alias not in found_canonical[canonical_name]["matched_terms"]:
                    found_canonical[canonical_name]["matched_terms"].append(alias)

    categorized: Dict[str, List[str]] = {}
    for skill_name, info in found_canonical.items():
        cat = info["category"]
        if cat not in categorized:
            categorized[cat] = []
        categorized[cat].append(skill_name)

    # Sort by frequency and name
    skills_list = sorted(list(found_canonical.keys()), key=lambda x: (-found_canonical[x]["count"], x))
    skill_details = [found_canonical[s] for s in skills_list]

    return {
        "skills": skills_list,
        "categorized": categorized,
        "skill_details": skill_details,
        "total_count": len(skills_list)
    }


def get_all_taxonomy_skills() -> Dict[str, List[str]]:
    """Returns all available skills organized by category."""
    return {cat: list(skills.keys()) for cat, skills in SKILL_TAXONOMY.items()}
