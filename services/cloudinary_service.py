# app/services/cloudinary_service.py
import os
import cloudinary
import cloudinary.uploader
from typing import List, Dict
from fastapi import UploadFile

# Configuración (idealmente desde variables de entorno)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

async def subir_evidencias(
    evidencias: List[UploadFile],
    municipio: str,
    id_insercion: int,
) -> Dict[str, str]:
    """
    Sube hasta 4 imágenes a Cloudinary en la carpeta del municipio.
    Los nombres serán {id_insercion}_incidente_1, {id_insercion}_incidente_2, etc.
    """
    if len(evidencias) > 4:
        raise ValueError("Máximo 4 imágenes permitidas en 'evidencias'.")

    carpeta = f"incidentes/{municipio.replace(' ', '_').lower()}"
    urls: Dict[str, str] = {}

    for idx, archivo in enumerate(evidencias, start=1):
        # 👇 AQUÍ ESTÁ EL CAMBIO: Usamos el id_insercion en el nombre
        public_id = f"{id_insercion}_incidente_{idx}"

        resultado = cloudinary.uploader.upload(
            archivo.file,
            folder=carpeta,
            public_id=public_id,
            overwrite=True,
            resource_type="image",
        )
        
        # Guardamos en el JSON con el nombre real generado
        urls[public_id] = resultado["secure_url"]

    return urls