from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password: str

class Medico(BaseModel):
    id: str
    name: str
    age: int
    email: str
    phone: str
    
class Paciente(BaseModel):
    id: Optional[str] = None
    nombre: str
    edad: int
    sexo: str
    email: str
    telefono: str
    
class Cita(BaseModel):
    id: Optional[str] = None
    paciente_id: Optional[str] = None
    fecha: str #formato YYYY-MM-DD
    hora: str #formato HH:MM
    motivo: str
    diagnostico: str
    procedimiento: str        