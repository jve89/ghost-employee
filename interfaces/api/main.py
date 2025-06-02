from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from interfaces.api.routes.jobs import router as jobs_router
from interfaces.api.routes.dashboard import router as dashboard_router
from interfaces.api.routes import dashboard
from config.config_loader import load_job_configs
from fastapi.responses import RedirectResponse

app = FastAPI()
app.include_router(jobs_router, prefix="/jobs")
app.include_router(dashboard_router)

templates = Jinja2Templates(directory="interfaces/api/templates")

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    job_configs = load_job_configs()
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": job_configs})
