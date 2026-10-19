from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from database import get_db

# Schemas
from schemas.user_schema import (
    UserRegisterRequest,
    UserRegisterResponse,
    UserDetailResponse, 
    UserUpdatePasswordRequest,
    UserUpdateDataRequest                                            
)

# Servicios
from services.user_service import (
    registrar_ciudadano,
    obtener_usuario_por_id, 
    actualizar_password_usuario,
    actualizar_datos_usuario,
    verificar_usuario,
    verificar_credenciales_sp
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
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Verificar credenciales de usuario (Login)",
    description="Recibe un payload RSA en Base64, lo desencripta y verifica las credenciales."
)
def login(payload: str = Query(..., description="String Base64 encriptado con RSA")):
    try:
        resultado = verificar_usuario(payload)
        return {
            "p_mensaje": resultado["mensaje"],
            "id_usuario": resultado["id_usuario"],
            "correo": resultado["correo"],                # 👈 Se agrega a la respuesta
            "hash_password": resultado["hash_password"]   # 👈 Se agrega a la respuesta
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/verificar-credenciales",
    status_code=status.HTTP_200_OK,
    summary="Verificar credenciales con SP",
    description="Usa el SP verificar_Usuario_Credenciales para validar usuario y contraseña."
)
def verificar_credenciales(
    username: str = Query(..., description="Nombre de usuario o cédula"),
    password: str = Query(..., description="Contraseña del usuario")
):
    try:
        existe = verificar_credenciales_sp(username, password)
        
        if existe:
            return {"p_existe": 1, "mensaje": "Credenciales válidas"}
        else:
            # Es buena práctica devolver 401 si no existe
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
            
    except HTTPException:
        raise # Re-lanzamos el 401
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
    response_model=UserRegisterResponse,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/{user_id}/actualizar",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar datos personales del usuario",
    description="Obtiene la cédula del usuario en la BD y llama al SP actualizar_Usuario enviando NULL en la contraseña."
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

    