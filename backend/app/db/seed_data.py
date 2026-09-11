import logging
from pathlib import Path
from app.core.config import RESUMES_DIR, UPLOADS_DIR
from app.db.database import get_db

logger = logging.getLogger("career_advisor.seed")

async def initialize_seed_data():
    """Initializes database collections and storage directories with zero mock user data."""
    RESUMES_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Database storage initialized with clean state.")
