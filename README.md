# Proyecto de Gestión Médica

Gestión Médica es una aplicación web desarrollada en Python con FastAPI y Firebase, diseñada para la administración eficiente de pacientes, citas y registros médicos en clínicas o consultorios pequeños.

---

## 🚀 Características principales

- Registro y autenticación de usuarios.
- Administración de pacientes y sus datos personales.
- Registro y gestión de citas médicas.
- Búsqueda de pacientes y citas.
- Visualización de historial médico.
- Interfaz web simple y responsiva (HTML, CSS, Jinja2).
- Integración con Firebase para almacenamiento seguro.
- Modularidad y estructura limpia para fácil mantenimiento y expansión.

---

## 📦 Estructura del proyecto

```
gestion-medica-app/
├── app/
│   ├── main.py
│   ├── routers/
│   ├── models/
│   ├── services/
│   ├── templates/
│   └── static/
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Requisitos previos

- Python 3.8 o superior
- Cuenta y proyecto en Firebase (para credenciales)
- Archivo de credenciales de Firebase (clave_privada.json)

---

## 🛠️ Instalación y configuración

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/angelalvc/app_gestion_medica.git
   cd app_gestion_medica
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r app/requirements.txt
   ```

3. **Prepara las variables de entorno**
   - Copia `.env.example` a `.env` y completa los valores necesarios.
   - Asegúrate de tener tu archivo `clave_privada.json` en la ruta especificada.

4. **Inicia la aplicación**
   ```bash
   uvicorn app.main:app --reload
   ```
   Accede a [http://127.0.0.1:8000](http://127.0.0.1:8000) en tu navegador.

---

## 📑 Uso de la API

- La documentación interactiva de la API está disponible en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- Principales endpoints:
    - `/auth/login` y `/auth/logout`
    - `/api/patients`
    - `/api/appointments`
    - `/dashboard`
    - `/patients/register`, `/appointments/register`

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Para colaborar:

1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commits descriptivos.
4. Abre un Pull Request.

Lee el archivo `CONTRIBUTING.md` para más detalles.

---

## ❓ Preguntas frecuentes

- **¿Puedo ejecutar la app en cualquier sistema operativo?**  
  Sí, mientras tengas Python 3.8+ y las dependencias instaladas.
- **¿Se pueden usar otras bases de datos?**  
  Actualmente está integrado con Firebase, pero puedes adaptar la capa de servicios.
- **¿Cómo proteger las credenciales?**  
  Nunca subas `clave_privada.json` ni `.env` con datos reales al repositorio público.

---

## 📬 Contacto

Para dudas, sugerencias o soporte, abre un issue o contacta a [angelalvc](alvaradoac1918@gmail.com).

---

```

Accede a la aplicación en tu navegador en `http://127.0.0.1:8000`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.
