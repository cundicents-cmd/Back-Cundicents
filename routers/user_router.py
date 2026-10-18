from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status
from database import get_db                                     

from schemas.user_schema import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserDetailResponse, 
    UserUpdatePasswordRequest,
    UserRegisterResponse,
    UserUpdateDataRequest                                            
)
from services.user_service import (
    registrar_ciudadano,
    obtener_usuario_por_id, 
    actualizar_password_usuario,
    actualizar_datos_usuario                                       
)

router = APIRouter(prefix="/users", tags=["Usuarios"])

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo ciudadano",
    description="Llama al SP registrar_Ciudadano para insertar un usuario en auth_user."
)
def register_user(data: UserRegisterRequest):
    """
    Registra un ciudadano usando el procedimiento almacenado.

    - **nombre**: Nombre del ciudadano
    - **apellido**: Apellido del ciudadano
    - **contrasena**: Contraseña (mínimo 6 caracteres)
    - **correo**: Correo electrónico válido
    - **cedula**: Número de cédula
    """
    try:
        resultado = registrar_ciudadano(data)
        return resultado
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al registrar ciudadano: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario por ID",
    description="Devuelve first_name, last_name, email y cedula de auth_user según su id."
)
def obtener_usuario(
    user_id: int = Path(..., gt=0, description="ID del usuario a consultar"),
    db: Session = Depends(get_db),
):
    """Consulta un usuario por su ID."""
    try:
        usuario = obtener_usuario_por_id(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al consultar usuario: {str(e)}"
        )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {user_id} no encontrado"
        )

    return usuario

@router.post(
    "/{user_id}/password",
    response_model=UserRegisterResponse,  # Reutilizamos el schema que tiene "p_mensaje"
    status_code=status.HTTP_200_OK,
    summary="Actualizar contraseña de usuario",
    description="Busca el correo del usuario por su ID, hashea la nueva clave con Django y actualiza la BD mediante el SP."
)
def actualizar_password(
    user_id: int = Path(..., gt=0, description="ID del usuario a actualizar"),
    data: UserUpdatePasswordRequest = ...,
    db: Session = Depends(get_db)
):
    try:
        mensaje = actualizar_password_usuario(db, user_id, data.new_password)
        return UserRegisterResponse(p_mensaje=mensaje)
    except ValueError as e:
        # Errores de negocio (usuario no existe, sin correo)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        # Errores de base de datos o SP
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/{user_id}/actualizar",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos personales del usuario",
    description="Obtiene la cédula del usuario en la BD y llama al SP actualizar_Usuario enviando contraseña vacía."
)
def actualizar_datos(
    user_id: int = Path(..., gt=0, description="ID del usuario a actualizar"),
    data: UserUpdateDataRequest = ...,
    db: Session = Depends(get_db)
):
    try:
        mensaje = actualizar_datos_usuario(db, user_id, data)
        return UserRegisterResponse(p_mensaje=mensaje)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )