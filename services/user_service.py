# app/services/user_service.py
from database import engine
from models.auth_user import AuthUser
from schemas.user_schema import UserRegisterRequest, UserRegisterResponse, UserDetailResponse, UserUpdateDataRequest
from services.password_service import hash_password
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

def registrar_ciudadano(data: UserRegisterRequest) -> UserRegisterResponse:
    hashed_password = hash_password(data.contrasena)

    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()

        args = (
            data.nombre,
            data.apellido,
            hashed_password,
            data.correo,
            data.cedula,
            0,  # Placeholder para p_mensaje (OUT)
        )

        # Ejecutar el SP
        cursor.callproc("registrar_Ciudadano", args)

        # ⚠️ PyMySQL: consumir TODOS los result sets con nextset()
        # Cada llamada a nextset() avanza al siguiente result set.
        # Debemos hacerlo hasta que devuelva None.
        while cursor.nextset():
            pass

        # Recuperar el parámetro OUT desde la variable de sesión.
        # La posición 5 corresponde a p_mensaje (0-based).
        cursor.execute("SELECT @_registrar_Ciudadano_5")
        result = cursor.fetchone()

        raw_conn.commit()

        p_mensaje = result[0] if result and result[0] is not None else "Registro procesado sin mensaje"

        return UserRegisterResponse(p_mensaje=p_mensaje)

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error al ejecutar registrar_Ciudadano: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()

def obtener_usuario_por_id(db: Session, user_id: int) -> Optional[UserDetailResponse]:
    """
    Consulta auth_user por id y devuelve first_name, last_name, email y cedula.
    Retorna None si el usuario no existe.
    """
    stmt = select(AuthUser).where(AuthUser.id == user_id)
    usuario = db.execute(stmt).scalar_one_or_none()

    if usuario is None:
        return None

    return UserDetailResponse.model_validate(usuario)

def actualizar_password_usuario(db: Session, user_id: int, new_password: str) -> str:
    """
    Busca el correo del usuario, hashea la contraseña con Django 
    y llama al SP sp_actualizar_password.
    """
    # 1. Obtener el usuario para sacar el correo
    usuario = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    
    if not usuario:
        raise ValueError(f"Usuario con id {user_id} no encontrado.")
        
    if not usuario.email:
        raise ValueError(f"El usuario con id {user_id} no tiene un correo registrado.")

    correo = usuario.email

    # 2. Hashear la nueva contraseña con make_password (Django)
    hashed_password = hash_password(new_password)

    # 3. Llamar al Procedimiento Almacenado
    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()
        
        # Ejecutamos el SP enviando correo y password (asumiendo que no tiene OUT param)
        sql = "CALL sp_actualizar_password(%s, %s)"
        cursor.execute(sql, (correo, hashed_password))

        # Consumir los result sets generados por el SP para evitar errores de conexión
        while cursor.nextset():
            pass

        raw_conn.commit()
        return "Contraseña actualizada correctamente."

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error al ejecutar sp_actualizar_password: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()

def actualizar_datos_usuario(db: Session, user_id: int, data: UserUpdateDataRequest) -> str:
    """
    Obtiene la cédula del usuario y llama al SP actualizar_Usuario 
    enviando la contraseña vacía.
    """
    # 1. Obtener el usuario para extraer su cédula actual
    usuario = db.query(AuthUser).filter(AuthUser.id == user_id).first()
    
    if not usuario:
        raise ValueError(f"Usuario con id {user_id} no encontrado.")
        
    # Si la cédula es nula en la BD, la enviamos como string vacío o None
    cedula_actual = usuario.cedula if usuario.cedula else ""

    # 2. Llamar al Procedimiento Almacenado
    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()
        
        # SP recibe: id, nombre, apellido, cedula, correo, contraseña
        # Enviamos "" en la contraseña para no afectarla
        sql = "CALL actualizar_Usuario(%s, %s, %s, %s, %s, %s)"
        parametros = (
            user_id, 
            data.nombre, 
            data.apellido, 
            cedula_actual, 
            data.correo, 
            None  
        )
        
        cursor.execute(sql, parametros)

        # Consumir los result sets generados
        while cursor.nextset():
            pass

        raw_conn.commit()
        return "Datos del usuario actualizados correctamente."

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error al ejecutar actualizar_Usuario: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()