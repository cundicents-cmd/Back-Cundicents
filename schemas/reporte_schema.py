# app/schemas/reporte_schema.py
from pydantic import BaseModel, Field
from typing import Dict, Optional
from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from datetime import datetime


class Ubicacion(BaseModel):
    latitud: float = Field(..., ge=-90, le=90, description="Latitud")
    longitud: float = Field(..., ge=-180, le=180, description="Longitud")

    model_config = {
        "json_schema_extra": {
            "example": {"latitud": 4.6097, "longitud": -74.0817}
        }
    }

class ReporteCreateResponse(BaseModel):
    id_reporte: int
    p_mensaje: str
    municipio: str
    evidencias: Optional[Dict[str, str]] = None
    mensaje_evidencias: Optional[str] = None



class ReporteViewResponse(BaseModel):
    id: int
    id_usuario: int
    usuario: str
    id_incidente: int
    incidente: str
    id_municipio: int
    municipio: str
    id_sector: Optional[int] = None
    sector: Optional[str] = None
    id_prioridad: int
    tp_prioridad: str
    id_estado: int
    estado: str
    descripcion: str
    fecha_hora: datetime
    ubicacion: Optional[Dict[str, Any]] = None
    evidencias: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 2,
                "id_usuario": 1,
                "usuario": "Juan Pérez",
                "id_incidente": 3,
                "incidente": "Fuga de agua",
                "id_municipio": 5,
                "municipio": "Madrid",
                "id_sector": 2,
                "sector": "Centro",
                "id_prioridad": 1,
                "tp_prioridad": "Alta",
                "id_estado": 1,
                "estado": "Pendiente",
                "descripcion": "Fuga en la calle 10",
                "fecha_hora": "2023-10-27T14:30:00",
                "ubicacion": {"latitud": 4.6097, "longitud": -74.0817},
                "evidencias": {
                    "2_incidente_1": "https://res.cloudinary.com/.../2_incidente_1.png"
                }
            }
        }
    }
