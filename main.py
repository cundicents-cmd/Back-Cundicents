from fastapi import FastAPI
from core.config import settings
from fastapi.openapi.utils import get_openapi
from core.config_django import setup_django 
from routers.cedula import router as cedula_router
from routers.incidente_router import router as incidente_router
from routers.reporte_router import router as reporte_router
from routers.user_router import router as user_router
from routers.historico_router import router as historico_router

setup_django()


app = FastAPI( 
    title="API de Cundicents",
    description="API para gestionar la plataforma Cundicents",
    version="1.0.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
    openapi_url="/openapi.json" if settings.app_env != "production" else None,
)

# app.add_middleware(
#     allowed_hosts=["*"],
# )

app.include_router(cedula_router)
app.include_router(user_router)
app.include_router(incidente_router)
app.include_router(reporte_router)
app.include_router(historico_router)


@app.get("/")
def inicio():
    return {"mensaje": "FastAPI Funcionando"}

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "La API está funcionando correctamente"
    }

@app.get("/v1/models")
def listar_modelos():
    return {
        "object": "list",
        "data": [
            {
                "id": "cundicents",
                "object": "model",
                "created": 0,
                "owned_by": "cundicents"
            }
        ]
    }

def custom_openapi():
    # Si el esquema ya fue generado, lo devolvemos de la caché
    if app.openapi_schema:
        return app.openapi_schema
    
    # Generamos el esquema base
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Función auxiliar recursiva para buscar y corregir los tipos de archivo
    def fix_upload_files(schema_part):
        if isinstance(schema_part, dict):
            # Si el diccionario representa un archivo (octet-stream)
            if schema_part.get("contentMediaType") == "application/octet-stream":
                del schema_part["contentMediaType"]
                schema_part["format"] = "binary"
            
            # Recorremos todas las claves para buscar anidamientos (arrays, objetos, etc.)
            for key, value in schema_part.items():
                fix_upload_files(value)
        elif isinstance(schema_part, list):
            for item in schema_part:
                fix_upload_files(item)

    # Aplicamos la corrección a todo el esquema
    fix_upload_files(openapi_schema)
    
    # Guardamos en caché para no recalcular en cada petición
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi