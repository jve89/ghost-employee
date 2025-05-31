from fastapi import FastAPI
from interfaces.api.routes.jobs import router as jobs_router

app = FastAPI()

app.include_router(jobs_router, prefix="/jobs")
