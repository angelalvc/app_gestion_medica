from fastapi import APIRouter, HTTPException, Body
from models.models import Cita
from firebase_admin import firestore
from typing import List

router = APIRouter()
db = firestore.client()

# Crear cita
@router.post("/", response_model=Cita)
async def create_cita(
    cita: Cita,
    paciente_email: str = Body(None),
    paciente_nombre: str = Body(None)
):
    # Buscar paciente por email o nombre
    paciente_id = None
    if paciente_email:
        docs = db.collection('pacientes').where('email', '==', paciente_email).stream()
        pacientes = [doc for doc in docs]
        if pacientes:
            paciente_id = pacientes[0].id
    elif paciente_nombre:
        docs = db.collection('pacientes').where('nombre', '==', paciente_nombre).stream()
        pacientes = [doc for doc in docs]
        if pacientes:
            paciente_id = pacientes[0].id
    if not paciente_id:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    cita.paciente_id = paciente_id
    doc_ref = db.collection('citas').document()
    cita.id = doc_ref.id
    doc_ref.set(cita.dict(exclude_unset=True))
    return cita

# Listar todas las citas
@router.get("/", response_model=List[Cita])
async def list_citas():
    docs = db.collection('citas').stream()
    citas = [Cita(**doc.to_dict()) for doc in docs]
    return citas

# Actualizar cita
@router.put("/{cita_id}", response_model=Cita)
async def update_cita(cita_id: str, cita: Cita):
    doc_ref = db.collection('citas').document(cita_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    doc_ref.update(cita.dict(exclude_unset=True))
    data = doc_ref.get().to_dict()
    return Cita(**data)

# Eliminar cita
@router.delete("/{cita_id}")
async def delete_cita(cita_id: str):
    doc_ref = db.collection('citas').document(cita_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    doc_ref.delete()
    return {"message": "Cita eliminada"}

# Obtener cita por paciente ID
@router.get("/by_paciente/{paciente_id}", response_model=List[Cita])
async def get_citas_by_paciente(paciente_id: str):
    docs = db.collection('citas').where('paciente_id', '==', paciente_id).stream()
    citas = [Cita(**doc.to_dict()) for doc in docs]
    return citas

# Obtener cita por ID
@router.get("/{cita_id}", response_model=Cita)
async def get_cita(cita_id: str):
    doc_ref = db.collection('citas').document(cita_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Cita no encontrada")
    return Cita(**doc.to_dict())

# Obtener cita por fecha
@router.get("/by_fecha/{fecha}", response_model=List[Cita])
async def get_citas_by_fecha(fecha: str):
    docs = db.collection('citas').where('fecha', '==', fecha).stream()
    citas = [Cita(**doc.to_dict()) for doc in docs]
    return citas