# Proyecto de Gestión Médica

Este proyecto es una aplicación web para la gestión de consultas y procedimientos médicos, desarrollada utilizando Python, FastAPI y Firebase.

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de archivos:

```
gestion-medica-app
├── app
│   ├── main.py                # Punto de entrada de la aplicación
│   ├── routers
│   │   └── __init__.py        # Rutas de la aplicación
│   ├── models
│   │   └── __init__.py        # Modelos de datos
│   ├── services
│   │   └── __init__.py        # Lógica de negocio
│   └── utils
│       └── __init__.py        # Funciones utilitarias
├── requirements.txt            # Dependencias del proyecto
├── .env                        # Variables de entorno
└── README.md                   # Documentación del proyecto
```

## Requisitos

Asegúrate de tener instaladas las siguientes dependencias:

- FastAPI
- firebase-admin

Puedes instalar las dependencias ejecutando:

```
pip install -r requirements.txt
```

## Configuración

1. Clona este repositorio en tu máquina local.
2. Crea un archivo `.env` en la raíz del proyecto y agrega tus credenciales de Firebase y otras configuraciones necesarias.
3. Asegúrate de tener el archivo `clave_privada.json` en la raíz del proyecto o en la ubicación especificada en `main.py`.

## Ejecución

Para iniciar la aplicación, ejecuta el siguiente comando:

```
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Accede a la aplicación en tu navegador en `http://127.0.0.1:8000`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.
