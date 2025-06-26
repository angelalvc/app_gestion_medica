from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from services.services import verify_user
from fastapi.templating import Jinja2Templates


router = APIRouter()


templates = Jinja2Templates(directory="./templates")

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_user(username, password):
        request.session["user"] = username  # Guardar usuario en la sesión
        return RedirectResponse("/dashboard", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})
    
    