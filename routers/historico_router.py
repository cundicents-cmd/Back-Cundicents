# app/routers/historico_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.historico_schema import HistoricoIncidenteResponse
from services.historico_service import obtener_historico_por_usuario

router = APIRouter(prefix="/historico", tags=["Histórico"])

@router.get(
    "/usuario/{user_id}",
    response_model=List[HistoricoIncidenteResponse],
    status_code=status.HTTP_200_OK,
    summary="Obtener histórico de incidentes por ID de usuario",
    description="Busca la cédula del usuario en auth_user y devuelve todos sus incidentes desde la vista ver_Historico_Incidentes."
)
def listar_historico(user_id: int, db: Session = Depends(get_db)):
    try:
        return obtener_historico_por_usuario(db, user_id)
    except ValueError as e:
        # Errores controlados: usuario no existe o no tiene cédula
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        # Errores inesperados
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar histórico: {str(e)}"
        )