# app/services/user_service.py
from database import engine
from models.auth_user import AuthUser
from schemas.user_schema import UserRegisterRequest, UserRegisterResponse, UserDetailResponse, UserUpdateDataRequest
from services.password_service import hash_password
from services.crypto_service import desencriptar_payload
from services.password_service import verify_password  

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

def verificar_usuario(payload_b64: str) -> dict:
    """
    Desencripta el payload, busca el hash en la BD usando el SP 
    y verifica la contraseña con check_password de Django.
    """
    # 1. Desencriptar
    try:
        datos = desencriptar_payload(payload_b64)
        correo = datos.get("correo")
        password_plana = datos.get("password")
    except Exception as e:
        raise ValueError(f"Payload inválido: {str(e)}")

    if not correo or not password_plana:
        raise ValueError("El payload debe contener 'correo' y 'password'.")

    # 2. Llamar al SP para obtener el hash guardado
    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()
        
        sql = "CALL verificar_Usuario(%s)"
        cursor.execute(sql, (correo,))

        # Capturar el resultado del SP
        usuario_id = None
        db_password_hash = None
        
        while True:
            if cursor.description:
                resultado = cursor.fetchone()
                if resultado:
                    usuario_id = resultado[0]
                    db_password_hash = resultado[1]
            
            if not cursor.nextset():
                break

        raw_conn.commit()

        # Si no se encontró el correo, el SP no devuelve filas
        if not db_password_hash:
            raise ValueError("Correo o contraseña incorrectos.")

        if verify_password(password_plana, db_password_hash):
            return {
                "mensaje": "Login exitoso", 
                "id_usuario": usuario_id,
                "correo": correo,                 
                "hash_password": db_password_hash 
            }
        else:
            raise ValueError("Correo o contraseña incorrectos.")

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        if isinstance(e, ValueError):
            raise e
        raise RuntimeError(f"Error al ejecutar verificar_Usuario: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()

def verificar_credenciales_sp(username: str, password: str) -> bool:
    """
    Llama al SP verificar_Usuario_Credenciales que devuelve un TINYINT en p_existe.
    """
    # NOTA: Si no quieres usar make_password, simplemente pasa 'password' directo.
    # hashed_password = hash_password(password) 
    hashed_password = password # Asumiendo que el SP espera el hash o texto plano exacto

    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()
        
        # Los 3 parámetros: p_username, p_password y el placeholder para p_existe (OUT)
        args = (username, hashed_password, 0)
        
        # Llamamos al SP
        cursor.callproc("verificar_Usuario_Credenciales", args)
        
        # Consumir result sets (PyMySQL)
        while cursor.nextset():
            pass
            
        # Recuperar el OUT (posición 2, porque es el tercer parámetro, base 0)
        cursor.execute("SELECT @_verificar_Usuario_Credenciales_2")
        resultado = cursor.fetchone()
        
        raw_conn.commit()
        
        if not resultado or resultado[0] is None:
            return False
            
        # Retorna True si p_existe es 1, False si es 0
        return bool(resultado[0])

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error al ejecutar verificar_Usuario_Credenciales: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()
