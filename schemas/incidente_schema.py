from pydantic import BaseModel, Field

class IncidenteResponse(BaseModel):
    id: int = Field(..., description="ID del incidente")
    incidente: str = Field(..., description="Descripción del incidente")
    id_tp_incidente: int = Field(..., description="ID del tipo de incidente")
    id_prioridad: int = Field(..., description="ID de la prioridad default")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "incidente": "Fuga de agua en la calle 10",
                "id_tp_incidente": 3,
                "id_prioridad": 3
            }
        }
    }