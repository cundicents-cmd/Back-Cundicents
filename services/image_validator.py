from fastapi import UploadFile

# Magic bytes (firmas binarias) de los formatos de imagen soportados
MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png":  [b"\x89PNG\r\n\x1a\n"],
    "image/gif":  [b"GIF87a", b"GIF89a"],
    "image/webp": [b"RIFF"],  # luego validamos 'WEBP' en el offset 8
}

TIPOS_MIME_PERMITIDOS = set(MAGIC_SIGNATURES.keys())
MAX_TAMANO_BYTES = 5 * 1024 * 1024  # 5 MB por imagen


def _detectar_tipo_por_firma(contenido: bytes) -> str | None:
    """Devuelve el MIME real detectado por magic bytes, o None si no es imagen."""
    for mime, firmas in MAGIC_SIGNATURES.items():
        for firma in firmas:
            if contenido.startswith(firma):
                # WebP requiere chequeo adicional en offset 8
                if mime == "image/webp" and contenido[8:12] != b"WEBP":
                    continue
                return mime
    return None


async def validar_imagenes(evidencias: list[UploadFile]) -> list[UploadFile]:
    """
    Valida que cada archivo sea realmente una imagen.
    - content_type declarado debe estar entre los permitidos
    - magic bytes deben coincidir con el tipo declarado
    - tamaño máximo 5 MB
    Devuelve la lista si todo es válido; lanza ValueError en caso contrario.
    """
    if len(evidencias) > 4:
        raise ValueError("Máximo se permiten 4 imágenes en 'evidencias'.")

    for i, archivo in enumerate(evidencias, start=1):
        # 1) Validar content_type declarado
        if archivo.content_type not in TIPOS_MIME_PERMITIDOS:
            raise ValueError(
                f"Evidencia #{i}: tipo '{archivo.content_type}' no permitido. "
                f"Permitidos: {', '.join(sorted(TIPOS_MIME_PERMITIDOS))}."
            )

        # 2) Leer bytes para validar firma y tamaño
        contenido = await archivo.read()
        await archivo.seek(0)  # rebobinar para que Cloudinary lo pueda leer después

        if not contenido:
            raise ValueError(f"Evidencia #{i}: el archivo está vacío.")

        if len(contenido) > MAX_TAMANO_BYTES:
            raise ValueError(
                f"Evidencia #{i}: excede el tamaño máximo de 5 MB."
            )

        # 3) Validar magic bytes (firma real del archivo)
        mime_real = _detectar_tipo_por_firma(contenido)
        if mime_real is None:
            raise ValueError(
                f"Evidencia #{i}: el archivo no es una imagen válida "
                f"(no coincide con ninguna firma JPEG/PNG/GIF/WebP)."
            )

        if mime_real != archivo.content_type:
            raise ValueError(
                f"Evidencia #{i}: el tipo declarado ({archivo.content_type}) "
                f"no coincide con el contenido real ({mime_real})."
            )

    return evidencias