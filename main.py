from fastapi import FastAPI
from routers.cedula import router as cedula_router

app = FastAPI(
    title="API de Cundicents",
    description="API para gestionar la plataforma Cundicents",
    version="1.0.0"
)

app.include_router(cedula_router)
#app.include_router(cedula_router)
#app.include_router(cedula_router)
#app.include_router(cedula_router)


@app.get("/")
def inicio():
    return {"mensaje": "FastAPI Funcionando"}

