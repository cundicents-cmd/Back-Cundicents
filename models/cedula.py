from pydantic import BaseModel, Field

class DatosCedula(BaseModel):
    nombres: str = Field(..., description="Nombres de la persona según la cédula.")
    apellidos: str = Field(..., description="Apellidos de la persona según la cédula.")
    numero_documento: str = Field(..., description="Número de documento de la cédula.")