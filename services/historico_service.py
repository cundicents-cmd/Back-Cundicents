# app/services/historico_service.py
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from models.auth_user import AuthUser
from models.historico_view import VerHistoricoIncidente
from schemas.historico_schema import HistoricoIncidenteResponse

def obtener_historico_por_usuario(db: Session, user_id: int) -> List[HistoricoIncidenteResponse]:
    """
    Obtiene la cédula del usuario y retorna su historial de incidentes.
    """
    # 1. Buscar el usuario para obtener la cédula
    usuario = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    
    if not usuario:
        raise ValueError(f"Usuario con id {user_id} no encontrado.")
    
    if not usuario.cedula:
        raise ValueError(f"El usuario con id {user_id} no tiene una cédula registrada.")

    # 2. Consultar la vista filtrando por la cédula (cc_usuario)
    # Convertimos a string por si la columna en la vista es VARCHAR
    stmt = (
        select(VerHistoricoIncidente)
        .where(VerHistoricoIncidente.cc_usuario == str(usuario.cedula))
        .order_by(VerHistoricoIncidente.fecha_hora.desc())
    )
    
    resultados = db.execute(stmt).scalars().all()
    
    return [HistoricoIncidenteResponse.model_validate(r) for r in resultados]