import base64
import os
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Ruta a la clave privada y contraseña de la clave (desde .env)
PEM_PATH = os.getenv("PEM_PATH", "clave_privada.pem")
PEM_PASSWORD = os.getenv("PEM_PASSWORD")

def desencriptar_payload(payload_b64: str) -> dict:
    """
    Desencripta un payload RSA en Base64 usando la clave privada PEM.
    """
    if not PEM_PASSWORD:
        raise ValueError("La variable de entorno PEM_PASSWORD no está configurada.")

    try:
        # 1. Leer el archivo de la clave privada
        with open(PEM_PATH, "rb") as f:
            pem_data = f.read()

        # 2. Cargar la clave privada usando la contraseña
        private_key = serialization.load_pem_private_key(
            pem_data,
            password=PEM_PASSWORD.encode("utf-8"),
        )

        # 3. Decodificar el texto Base64 a bytes
        encrypted_bytes = base64.b64decode(payload_b64)

        # 4. Desencriptar usando OAEP (debe coincidir con el padding que use tu frontend)
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 5. Convertir los bytes decriptados a JSON (Diccionario)
        return json.loads(decrypted_bytes.decode("utf-8"))

    except Exception as e:
        raise ValueError(f"Error al desencriptar el payload: {str(e)}")