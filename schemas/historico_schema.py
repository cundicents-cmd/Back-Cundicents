# app/schemas/historico_schema.py
from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime

class HistoricoIncidenteResponse(BaseModel):
    id: int
    cc_usuario: str
    tipo_incidente: str
    incidente: str
    municipio: str
    sector: Optional[str] = None
    prioridad: str
    estado: str
    descripcion: str
    fecha_hora: datetime
    ubicacion: Optional[Dict[str, Any]] = None
    evidencias: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True
    }