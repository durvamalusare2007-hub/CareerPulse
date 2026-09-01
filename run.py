import sys
from pathlib import Path
import uvicorn

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("=" * 60)
    print("  [STARTING] CareerPulse AI Career & Employment Advisor")
    print("  [WEB URL]  http://127.0.0.1:8000")
    print("  [DOCS]     http://127.0.0.1:8000/docs")
    print("=" * 60)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
