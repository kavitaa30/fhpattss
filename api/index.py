"""Vercel entry point: exposes the FastAPI app from backend/ as a serverless function."""
import sys
from pathlib import Path

# Make `import app...` work (the backend package lives in <repo>/backend).
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app  # noqa: E402,F401  (Vercel looks for a variable named `app`)