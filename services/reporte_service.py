# app/services/reporte_service.py
import json
from typing import List
from fastapi import UploadFile
from database import engine
from services.geocoding_service import obtener_municipio
from services.cloudinary_service import subir_evidencias
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.reporte_view import VerReporte
from schemas.reporte_schema import ReporteViewResponse



def _es_numero(valor: str) -> bool:
    """Determina si el mensaje del SP es un ID numérico."""
    try:
        int(valor)
        return True
    except (ValueError, TypeError):
        return False


def _llamar_sp_registrar(
    id_usuario: int,
    id_incidente: int,
    municipio: str,
    descripcion: str,
    latitud: float,
    longitud: float,
) -> str:
    """
    Llama al SP registrar_Reporte_Incidente.
    Como el SP espera solo 5 parámetros, usamos un CALL directo y leemos el resultado.
    """
    ubicacion_json = json.dumps({"latitud": latitud, "longitud": longitud})

    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()
        
        # Ejecutamos el SP directamente enviando solo los 5 parámetros
        sql = "CALL registrar_Reporte_Incidente(%s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_usuario, id_incidente, municipio, descripcion, ubicacion_json))

        # Consumir todos los result sets que devuelva el SP
        mensaje_sp = None
        while True:
            if cursor.description:
                # Si el SP hace un SELECT, lo capturamos aquí
                resultado = cursor.fetchone()
                if resultado and resultado[0] is not None:
                    mensaje_sp = str(resultado[0])
            
            # Avanzar al siguiente result set o salir del bucle
            if not cursor.nextset():
                break

        raw_conn.commit()

        if mensaje_sp is None:
            raise RuntimeError("El SP registrar_Reporte_Incidente no devolvió ningún resultado (mensaje o ID).")

        return mensaje_sp

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error en registrar_Reporte_Incidente: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()

def _llamar_sp_adjuntar(id_reporte: int, evidencias_json: str) -> str:
    """
    Llama al SP adjuntar_Evidencias(id, json) que solo hace UPDATE.
    No tiene parámetro OUT, así que validamos con rowcount.
    Devuelve un mensaje informativo.
    """
    raw_conn = engine.raw_connection()
    cursor = None
    try:
        cursor = raw_conn.cursor()

        args = (id_reporte, evidencias_json)
        cursor.callproc("adjuntar_Evidencias", args)

        # PyMySQL: consumir result sets con nextset()
        while cursor.nextset():
            pass

        # rowcount refleja las filas afectadas por el UPDATE dentro del SP
        filas_afectadas = cursor.rowcount

        raw_conn.commit()

        if filas_afectadas == 0:
            raise RuntimeError(
                f"adjuntar_Evidencias no actualizó ninguna fila para id={id_reporte}. "
                f"Verifica que el reporte exista."
            )

        return f"Evidencias adjuntadas correctamente ({filas_afectadas} fila(s) actualizada(s))."

    except Exception as e:
        if raw_conn:
            raw_conn.rollback()
        raise RuntimeError(f"Error en adjuntar_Evidencias: {e}")

    finally:
        if cursor:
            cursor.close()
        if raw_conn:
            raw_conn.close()
            

async def registrar_reporte_completo(
    id_usuario: int,
    id_incidente: int,
    latitud: float,
    longitud: float,
    descripcion: str,
    evidencias: List[UploadFile],
) -> dict:
    """
    Orquesta el flujo completo:
    1. Geocodificación inversa → municipio
    2. SP registrar_Reporte_Incidente → id o error
    3. Cloudinary → URLs de evidencias
    4. SP adjuntar_Evidencias → mensaje final
    """
    # 1️⃣ Obtener municipio
    municipio = await obtener_municipio(latitud, longitud)

    # 2️⃣ Registrar reporte
    resultado_sp = _llamar_sp_registrar(
        id_usuario, id_incidente, municipio, descripcion, latitud, longitud
    )

    # 3️⃣ Verificar si es ID (éxito) o texto (error)
    if not _es_numero(resultado_sp):
        # El SP devolvió texto → es un error de negocio
        return {"error": resultado_sp}

    id_reporte = int(resultado_sp)

    # 4️⃣ Subir evidencias si las hay
    urls_evidencias = {}
    mensaje_evidencias = None

    if evidencias:
        urls_evidencias = await subir_evidencias(evidencias, municipio, id_reporte)
        evidencias_json = json.dumps(urls_evidencias, ensure_ascii=False)
        mensaje_evidencias = _llamar_sp_adjuntar(id_reporte, evidencias_json)

    return {
        "id_reporte": id_reporte,
        "municipio": municipio,
        "evidencias": urls_evidencias or None,
        "mensaje_evidencias": mensaje_evidencias,
    }


def obtener_reportes_por_usuario(db: Session, id_usuario: int) -> List[ReporteViewResponse]:
    """
    Consulta la vista ver_Reportes y devuelve los reportes del usuario indicado.
    """
    # Seleccionamos de la vista filtrando por el id_usuario y ordenamos por fecha descendente
    stmt = (
        select(VerReporte)
        .where(VerReporte.id_usuario == id_usuario)
        .order_by(VerReporte.fecha_hora.desc())
    )
    
    resultados = db.execute(stmt).scalars().all()
    
    return [ReporteViewResponse.model_validate(r) for r in resultados]