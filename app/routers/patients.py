from fastapi import APIRouter, HTTPException
from models.models import Paciente
from firebase_admin import firestore
from typing import List

router = APIRouter()
db = firestore.client()

# Crear paciente
@router.post("/", response_model=Paciente)
async def create_paciente(paciente: Paciente):
    doc_ref = db.collection('pacientes').document()  # genera un ID único
    paciente.id = doc_ref.id
    doc_ref.set(paciente.dict(exclude_unset=True))
    return paciente

# Obtener todos los pacientes
@router.get("/", response_model=List[Paciente])
async def list_pacientes():
    docs = db.collection('pacientes').stream()
    pacientes = [Paciente(**doc.to_dict()) for doc in docs]
    return pacientes

# Actualizar un paciente
@router.put("/{paciente_id}", response_model=Paciente)
async def update_paciente(paciente_id: str, paciente: Paciente):
    doc_ref = db.collection('pacientes').document(paciente_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    doc_ref.update(paciente.dict(exclude_unset=True))
    data = doc_ref.get().to_dict()
    return Paciente(**data)

# Eliminar un paciente
@router.delete("/{paciente_id}")
async def delete_paciente(paciente_id: str):
    doc_ref = db.collection('pacientes').document(paciente_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    doc_ref.delete()
    return {"message": "Paciente eliminado"}

# Obtener paciente por ID
@router.get("/{paciente_id}", response_model=Paciente)
async def get_paciente(paciente_id: str):
    doc_ref = db.collection('pacientes').document(paciente_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return Paciente(**doc.to_dict())