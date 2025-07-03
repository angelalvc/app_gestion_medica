from firebase_admin import credentials, firestore
import firebase_admin

# Configura la ruta absoluta al archivo de credenciales
CREDENTIALS_PATH =  "./clave_privada.json"

# Inicializar Firebase solo una vez
cred = credentials.Certificate(CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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
    return templates.TemplateResponse("dashboard.html", {"request": request})

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
        fecha=fecha,
        hora=hora,
        motivo=motivo,
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
    return templates.TemplateResponse("search_patient.html", {"request": request})

# Procesar búsqueda de pacientes
@app.get("/patients/search", response_class=HTMLResponse)
async def search_patient(request: Request, nombre: str = ""):
    if not is_authenticated(request):
        return RedirectResponse("/")
    docs = db.collection('pacientes').where('nombre', '==', nombre).stream()
    pacientes_list = []
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
    
    #Búsqueda por ID del paciente
    if paciente_id:
        docs = db.collection('citas').where('paciente_id', '==', paciente_id).stream()
        citas_list = [Cita(**doc.to_dict()) for doc in docs]
    #Búsqueda por nombre del paciente
    elif paciente_nombre:
        pacientes = db.collection('pacientes').where('nombre', '==', paciente_nombre).stream()
        pacientes_list = [p for p in pacientes]
        if pacientes_list:
            paciente_id = pacientes_list[0].id
            docs = db.collection('citas').where('paciente_id', '==', paciente_id).stream()
            citas_list = [Cita(**doc.to_dict()) for doc in docs]
    #Búsqueda por fecha        
    elif fecha:
        docs = db.collection('citas').where('fecha', '==', fecha).stream()
        citas_list = [Cita(**doc.to_dict()) for doc in docs]        
    if not citas_list:    
        error = "No se encontraron citas para ese paciente."
    return templates.TemplateResponse("search_appointment.html", {"request": request, "citas": citas_list, "error": error})

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
                
              
