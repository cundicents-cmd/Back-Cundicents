# app/routers/reporte_router.py
import json
from typing import List
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError
from schemas.reporte_schema import ReporteCreateResponse, Ubicacion
from services.reporte_service import registrar_reporte_completo
from services.image_validator import validar_imagenes
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.reporte_schema import ReporteCreateResponse, ReporteViewResponse
from services.reporte_service import registrar_reporte_completo, obtener_reportes_por_usuario



router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.post(
    "/",
    response_model=ReporteCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un reporte de incidente",
)
async def crear_reporte(
    id_usuario: int = Form(..., gt=0),
    id_incidente: int = Form(..., gt=0),
    descripcion: str = Form(..., min_length=1, max_length=2000),
    ubicacion: str = Form(
        ..., 
        description="JSON en texto con latitud y longitud. Ej: {\"latitud\": 4.6097, \"longitud\": -74.0817}"
    ),
    evidencias: List[UploadFile] = File(default=[], description="Hasta 4 imágenes"),
):
    # 1. Parsear y validar el JSON de ubicación
    try:
        ubicacion_dict = json.loads(ubicacion)
        ubicacion_valida = Ubicacion(**ubicacion_dict)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El campo 'ubicacion' debe ser un JSON válido."
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error en las coordenadas: {e.errors()}"
        )

    # 2. Validar imágenes
    try:
        await validar_imagenes(evidencias)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    # 3. Ejecutar el flujo principal
    try:
        resultado = await registrar_reporte_completo(
            id_usuario=id_usuario,
            id_incidente=id_incidente,
            latitud=ubicacion_valida.latitud,     # 👈 Extraídas del JSON
            longitud=ubicacion_valida.longitud,   # 👈 Extraídas del JSON
            descripcion=descripcion,
            evidencias=evidencias,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if "error" in resultado:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"])

    return ReporteCreateResponse(
        id_reporte=resultado["id_reporte"],
        p_mensaje=f"Reporte registrado con ID {resultado['id_reporte']}",
        municipio=resultado["municipio"],
        evidencias=resultado.get("evidencias"),
        mensaje_evidencias=resultado.get("mensaje_evidencias"),
    )


@router.get(
    "/usuario/{id_usuario}",
    response_model=List[ReporteViewResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener reportes por ID de usuario",
    description="Consulta la vista ver_Reportes y devuelve todos los incidentes reportados por un usuario."
)
def listar_reportes_por_usuario(
    id_usuario: int, 
    db: Session = Depends(get_db)
):
    try:
        reportes = obtener_reportes_por_usuario(db, id_usuario)
        return reportes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar los reportes: {str(e)}"
        )