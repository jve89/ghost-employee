import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import uvicorn
from interfaces.api import main

# If you have watcher or environment init, keep them here
# from app import startup
# startup.start_watchers()

if __name__ == "__main__":
    uvicorn.run(
        "interfaces.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )