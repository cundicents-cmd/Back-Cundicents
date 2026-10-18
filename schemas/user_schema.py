# app/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, description="Nombre del ciudadano")
    apellido: str = Field(..., min_length=1, max_length=150, description="Apellido del ciudadano")
    contrasena: str = Field(..., min_length=6, max_length=128, description="Contraseña (mín. 6 caracteres)")
    correo: EmailStr = Field(..., description="Correo electrónico válido")
    cedula: Optional[int] = Field(None, description="Número de cédula")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "contrasena": "MiClave123",
                "correo": "juan@example.com",
                "cedula": "1234567890"
            }
        }
    }

class UserRegisterResponse(BaseModel):
    p_mensaje: str = Field(..., description="Mensaje de resultado del procedimiento almacenado")

class UserDetailResponse(BaseModel):
    """Datos públicos de un usuario consultado por ID."""
    first_name: str = Field(..., description="Nombre del usuario")
    last_name: str = Field(..., description="Apellido del usuario")
    email: EmailStr = Field(..., description="Correo electrónico")
    cedula: Optional[int] = Field(None, description="Número de cédula")
        
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "email": "juan@example.com",
                "cedula": "1234567890"
            }
        }
    }

class UserUpdatePasswordRequest(BaseModel):
    new_password: str = Field(
        ..., 
        min_length=6, 
        max_length=128, 
        description="Nueva contraseña (mínimo 6 caracteres)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {"new_password": "NuevaClaveSegura123"}
        }
    }

class UserUpdateDataRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    apellido: str = Field(..., min_length=1, max_length=150)
    correo: EmailStr = Field(...)

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Juan Carlos",
                "apellido": "Pérez Gómez",
                "correo": "juancarlos@example.com"
            }
        }
    }