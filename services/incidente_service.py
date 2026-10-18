
# app/services/incidente_service.py
from typing import List
from sqlalchemy.orm import Session
from models.incidente import Incidente
from schemas.incidente_schema import IncidenteResponse


def obtener_todos_los_incidentes(db: Session) -> List[IncidenteResponse]:
    incidentes = db.query(Incidente).order_by(Incidente.id.asc()).all()

    return [IncidenteResponse.model_validate(i) for i in incidentes]