
"""Configuración central del Agente de Gimnasio."""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GEMINI_MODEL = (
    os.getenv("GEMINI_MODEL") or "gemini-3.8-flash"
).strip()


def validar_configuracion() -> None:
    """Verifica que exista una clave de API de Gemini."""
    if not GEMINI_API_KEY:
        raise ValueError(
            "Falta GEMINI_API_KEY. Configura una clave válida "
            "en el archivo .env."
        )
