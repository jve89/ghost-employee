# infrastructure/auth/decorators.py

from functools import wraps
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED

def require_login_json(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request: Request = kwargs.get("request") or args[0]
        session = request.session
        if not session.get("logged_in"):
            accept = request.headers.get("accept", "")
            if "text/html" in accept:
                return RedirectResponse(url="/login", status_code=303)
            else:
                return JSONResponse({"error": "Unauthorized"}, status_code=HTTP_401_UNAUTHORIZED)
        return await func(*args, **kwargs)
    return wrapper
