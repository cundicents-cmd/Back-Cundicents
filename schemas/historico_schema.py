# app/schemas/historico_schema.py
from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
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

    @field_validator("cc_usuario", mode="before")
    @classmethod
    def convertir_cc_usuario_a_string(cls, valor):
        if valor is None:
            return None
        return str(valor)

    model_config = {
        "from_attributes": True
    }