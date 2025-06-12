from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="interfaces/api/templates")

USERNAME = "admin"
PASSWORD = "password"

@router.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        request.session["logged_in"] = True
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
