import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import and run the FastAPI app
from main import app
import uvicorn

if __name__ == "__main__":
    # Use environment variable for port, default to 8000
    port = int(os.environ.get("BOOKBOOK_PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port)
