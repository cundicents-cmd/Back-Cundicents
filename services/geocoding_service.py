import httpx
from typing import Optional

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
# Nominatim EXIGE un User-Agent identificable [citation:3]
USER_AGENT = "ReporteIncidentesApp/1.0 (contacto@tudominio.com)"


async def obtener_municipio(latitud: float, longitud: float) -> str:
    """
    Geocodificación inversa: obtiene el municipio/ciudad desde lat/lon.
    Lanza excepción si no se puede determinar.
    """
    params = {
        "lat": latitud,
        "lon": longitud,
        "format": "jsonv2",
        "addressdetails": 1,
        "accept-language": "es",
    }
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

    address = data.get("address", {})

    # Nominatim puede devolver el municipio bajo distintas claves según la zona
    municipio = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("village")
        or address.get("county")
    )

    if not municipio:
        raise ValueError(
            f"No se pudo determinar el municipio para ({latitud}, {longitud}). "
            f"Respuesta: {data.get('display_name', 'sin dirección')}"
        )

    return municipio