from fastapi import APIRouter, File, HTTPException, UploadFile
from schemas.cedula import CedulaResponse
from services.cedula_service import extraer_datos_cedula

router = APIRouter(prefix="/cedula", tags=["Cédula"])

TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/heic"}

@router.post("/extraer", response_model=CedulaResponse)
async def extraer_cedula(file: UploadFile = File(...)):
    if file.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de imagen no soportado: {file.content_type}. Usa JPEG, PNG, WEBP o HEIC."
        )

    imagen_bytes = await file.read()
    if not imagen_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    try:
        datos = await extraer_datos_cedula(imagen_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la imagen: {str(e)}")

    return CedulaResponse(**datos.model_dump())

