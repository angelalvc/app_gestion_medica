from firebase_admin import credentials, firestore
import firebase_admin
import os

# Configura la ruta absoluta al archivo de credenciales
CREDENTIALS_PATH =  "./clave_privada.json"

# Inicializar Firebase solo una vez
cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from services.services import verify_user
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, patients, appointments
from models.models import Cita, Paciente
from dotenv import load_dotenv

# Crear aplicación FastAPI
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "./clave_privada.json")

# Configurar Jinja2 para plantillas HTML
templates = Jinja2Templates(directory="./templates")

# Inicializar Firestore
db = firestore.client()

# Middleware simple de autenticación
def is_authenticated(request: Request):
    return request.session.get("user") is not None

# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(patients.router, prefix="/api/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])

# Configurar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Ruta para el formulario de inicio de sesión
@app.post("/", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if verify_user(username, password):
        request.session["user"] = username  # Guardar el usuario en la sesión
        return RedirectResponse("/dashboard", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales incorrectas."})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/")
    
    # Obtener usuario (ajusta según tu sistema de sesiones)
    usuario = {"nombre": request.session.get("usuario", "Doctor")}

    # Fechas para filtrar
    hoy = datetime.now().date().isoformat()
    manana = (datetime.now() + timedelta(days=1)).date().isoformat()

    # Citas para hoy
    citas_hoy_docs = db.collection('citas').where('fecha', '==', hoy).stream()
    citas_hoy = [doc.to_dict() for doc in citas_hoy_docs]

    # Citas para mañana
    citas_manana_docs = db.collection('citas').where('fecha', '==', manana).stream()
    citas_manana = [doc.to_dict() for doc in citas_manana_docs]
    
    # Próxima cita (la más cercana a partir de ahora)
    todas_citas_docs = db.collection('citas').stream()
    todas_citas = [doc.to_dict() for doc in todas_citas_docs]
    ahora = datetime.now().strftime("%H:%M")
    proxima_cita = None
    # Filtra por fecha >= hoy y hora >= ahora
    futuras = [c for c in todas_citas if c['fecha'] >= hoy and c['hora'] >= ahora]
    if futuras:
        proxima_cita = sorted(futuras, key=lambda c: (c['fecha'], c['hora']))[0]
    elif citas_hoy:
        proxima_cita = sorted(citas_hoy, key=lambda c: c['hora'])[0]
    else:
        proxima_cita = {"fecha": "", "hora": "", "paciente_nombre": "Sin próximas citas"}

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "usuario": usuario,
        "proxima_cita": proxima_cita,
        "citas_hoy": citas_hoy,
        "citas_manana": citas_manana
    })

@app.get("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

@app.get("/patients/register", response_class=HTMLResponse)
async def register_patient_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/")
    return templates.TemplateResponse("register_patient.html", {"request": request})

@app.post("/patients/register", response_class=HTMLResponse)
async def register_patient(
    request: Request,
    nombre: str = Form(...),
    edad: int = Form(...),
    sexo: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...)
):
    if not is_authenticated(request):
        return RedirectResponse("/")
    paciente = Paciente(nombre=nombre, edad=edad, sexo=sexo, email=email, telefono=telefono)
    doc_ref = db.collection('pacientes').document()  # genera un ID único
    paciente.id = doc_ref.id
    doc_ref.set(paciente.dict(exclude_unset=True))
    return templates.TemplateResponse("register_patient.html", {"request": request, "message": "Paciente registrado correctamente"})

@app.get("/appointments/register", response_class=HTMLResponse)
async def register_appointment_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/")
    return templates.TemplateResponse("register_appointment.html", {"request": request})

@app.post("/appointments/register", response_class=HTMLResponse)
async def register_appointment(
    request: Request,
    paciente_nombre: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    motivo: str = Form(...),
    tipo: str = Form(...),
    diagnostico: str = Form(...),
    procedimiento: str = Form(...)
):
    if not is_authenticated(request):
        return RedirectResponse("/")
    # Buscar paciente por nombre
    pacientes = db.collection('pacientes').where('nombre', '==', paciente_nombre).stream()
    pacientes_list = [p for p in pacientes]
    if not pacientes_list:
        return templates.TemplateResponse("register_appointment.html", {"request": request, "error": "Paciente no encontrado"})
    paciente_id = pacientes_list[0].id
    cita = Cita(
        paciente_id=paciente_id,
        paciente_nombre=paciente_nombre,
        fecha=fecha,
        hora=hora,
        motivo=motivo,
        tipo=tipo,
        diagnostico=diagnostico,
        procedimiento=procedimiento
    )
    doc_ref = db.collection('citas').document()
    cita.id = doc_ref.id
    doc_ref.set(cita.dict(exclude_unset=True))
    return templates.TemplateResponse("register_appointment.html", {"request": request, "message": "Cita registrada correctamente"})

# Mostrar formulario de búsqueda de pacientes
@app.get("/patients/list", response_class=HTMLResponse)
async def search_patient_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/")
    return RedirectResponse("/patients/search")

# Procesar búsqueda de pacientes
@app.get("/patients/search", response_class=HTMLResponse)
async def search_patient(request: Request, nombre: str = ""):
    if not is_authenticated(request):
        return RedirectResponse("/")
    pacientes_list = []
    if nombre:
        docs = db.collection('pacientes').where('nombre', '==', nombre).stream()
    else:
        docs = db.collection('pacientes').stream()
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id  # Agrega el ID del documento Firestore
        pacientes_list.append(Paciente(**data))
    if not pacientes_list:
        return templates.TemplateResponse("search_patient.html", {"request": request, "error": "Paciente no encontrado"})
    return templates.TemplateResponse("search_patient.html", {"request": request, "pacientes": pacientes_list})

# Mostrar formulario de búsqueda de citas
@app.get("/appointments/search", response_class=HTMLResponse)
async def search_appointment_form(
    request: Request, 
    paciente_id: str = None,
    paciente_nombre: str = None,
    fecha: str = None
):
    if not is_authenticated(request):
        return RedirectResponse("/")
    citas_list = []
    error = None
    
    # Búsqueda por ID del paciente
    if not paciente_id and not paciente_nombre and not fecha:
        docs = db.collection('citas') \
                 .order_by("fecha") \
                 .order_by("hora") \
                 .stream()
        citas_list = [Cita(**doc.to_dict()) for doc in docs]

    # Búsqueda por ID específico
    elif paciente_id:
        docs = db.collection('citas') \
                 .where('paciente_id', '==', paciente_id) \
                 .stream()
        citas_list = [Cita(**doc.to_dict()) for doc in docs]

    # Búsqueda por nombre de paciente
    elif paciente_nombre:
        pacientes = db.collection('pacientes') \
                      .where('nombre', '==', paciente_nombre) \
                      .stream()
        pacientes_list = [p for p in pacientes]
        if pacientes_list:
            paciente_id = pacientes_list[0].id
            docs = db.collection('citas') \
                     .where('paciente_id', '==', paciente_id) \
                     .stream()
            citas_list = [Cita(**doc.to_dict()) for doc in docs]

    # Búsqueda por fecha
    elif fecha:
        docs = db.collection('citas') \
                 .where('fecha', '==', fecha) \
                 .stream()
        citas_list = [Cita(**doc.to_dict()) for doc in docs]

    # Si no se encontraron citas
    if not citas_list:
        error = "No se encontraron citas para ese paciente."

    pacientes_docs = db.collection('pacientes').stream()
    pacientes_list = [Paciente(**{**doc.to_dict(), "id": doc.id}) for doc in pacientes_docs]

    return templates.TemplateResponse(
        "search_appointment.html",
        {
            "request": request,
            "citas": citas_list,
            "pacientes_list": pacientes_list,
            "error": error
        }
    )

@app.get("/records/{paciente_id}", response_class=HTMLResponse)
async def expediente_paciente(request: Request, paciente_id: str):
    if not is_authenticated(request):
        return RedirectResponse("/")
    # Obtener datos del paciente
    doc = db.collection('pacientes').document(paciente_id).get()
    if not doc.exists:
        return templates.TemplateResponse(
            "records.html",
            {"request": request,"paciente": None,"citas": [] ,"error": "Paciente no encontrado"})
    paciente = doc.to_dict()
    # Obtener citas del pacientes
    citas_docs = db.collection('citas').where('paciente_id', '==', paciente_id).stream()
    citas = [cita.to_dict() for cita in citas_docs]
    return templates.TemplateResponse(
        "records.html",
        {"request": request, "paciente": paciente, "citas": citas})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
                
              
