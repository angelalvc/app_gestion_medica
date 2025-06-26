from firebase_admin import firestore, credentials
from models.models import User
from typing import Optional

db = firestore.client()

def get_user_by_username(username: str) -> Optional[dict]:
    """Obtiene un usuario por su nombre de usuario desde Firestore."""
    try:
        doc = db.collection('users').document(username).get()
        if doc.exists:
            user_data = doc.to_dict()
            user_data['doc_id'] = doc.id  # Agrega el ID del documento
            return user_data
        else:
            print(f"Usuario {username} no encontrado.")
    except Exception as e:
        print(f"Error al obtener usuario {username}: {e}")
    return None

def verify_user(username: str, password: str) -> bool:
    """
    Verifica si un usuario y contraseña son válidos.
    Busca el usuario en la colección 'users' y compara la contraseña.
    """
    user = get_user_by_username(username)
    if user is None:
        return False
    # Asegúrate de que el campo 'password' exista en el usuario
    if 'password' in user and user['password'] == password:
        return True
    return False