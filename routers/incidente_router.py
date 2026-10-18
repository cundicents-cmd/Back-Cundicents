# app/routers/incidente_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.incidente_schema import IncidenteResponse
from services.incidente_service import obtener_todos_los_incidentes

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])


@router.get(
    "/",
    response_model=List[IncidenteResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los incidentes",
    description="Devuelve todos los incidentes registrados en la tabla 'incidentes'."
)
def listar_incidentes(db: Session = Depends(get_db)):
    """Obtiene la lista completa de incidentes."""
    try:
        return obtener_todos_los_incidentes(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener incidentes: {str(e)}"
        )