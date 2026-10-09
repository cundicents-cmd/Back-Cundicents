from google.genai import types
from core.gemini import client
from core.config import settings
from models.cedula import DatosCedula

PROMPT = """
Analiza la imagen adjunta. Es una cédula de ciudadanía colombiana.
Extrae EXACTAMENTE los siguientes datos:
- nombres: los nombres de la persona (sin apellidos).
- apellidos: los apellidos de la persona (sin nombres).
- numero_documento: el número de documento, sin puntos ni espacios.

Si la imagen no corresponde a una cédula o no puedes leer los datos,
devuelve cadenas vacías en los campos que no puedas identificar.
Devuelve la información en formato JSON siguiendo el esquema proporcionado.
"""

async def extraer_datos_cedula(imagen_bytes: bytes, mime_type: str) -> DatosCedula:
    """
    Envía la imagen de la cédula a Gemini y devuelve los datos estructurados.
    """
    imagen_part = types.Part.from_bytes(data=imagen_bytes, mime_type=mime_type)

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=DatosCedula,   # Gemini devolverá exactamente este formato
        temperature=0.0                # Sin creatividad, solo extracción
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[PROMPT, imagen_part],
        config=config
    )

    return DatosCedula.model_validate_json(response.text)