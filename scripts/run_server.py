# scripts/run_server.py

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from interfaces.api.routes import dashboard, email_input, mailgun_inbound

app = FastAPI(title="Ghost Employee v3", version="0.1.0")

# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="interfaces/api/static"), name="static")

# Routes
app.include_router(dashboard.router)
app.include_router(email_input.router)
app.include_router(mailgun_inbound.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("scripts.run_server:app", host="0.0.0.0", port=8000, reload=True)
