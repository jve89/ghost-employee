from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import pathlib

from interfaces.api.routes import dashboard, mailgun_inbound

app = FastAPI(
    title="Ghost Employee API",
    description="Backend API for Ghost Employee system",
    version="0.1.0",
)

# Mount static files
static_dir = pathlib.Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include your routers
app.include_router(dashboard.router)
app.include_router(mailgun_inbound.router)
