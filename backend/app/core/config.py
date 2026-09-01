import os
from pathlib import Path

# Root project directory: career_advisor_mvp/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "sample_data"
UPLOADS_DIR = BASE_DIR / "uploads"
RESUMES_DIR = DATA_DIR / "resumes"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
RESUMES_DIR.mkdir(parents=True, exist_ok=True)

# Application Settings
APP_NAME = "CareerPulse AI"
APP_DESCRIPTION = "AI-Powered Personalized Career & Employment Advisor"
API_V1_STR = "/api"

# MongoDB connection settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "career_advisor_db")

# Design Palette Constants
THEME_COLORS = {
    "dark": "#2A2A2A",
    "background": "#F9F5ED",
    "primary": "#5E83AE",
    "primary_dark": "#4A6B8F",
    "primary_light": "#7D9EB8",
    "accent_success": "#2E7D32",
    "accent_warning": "#D97706",
    "card_bg": "#FFFFFF",
}
