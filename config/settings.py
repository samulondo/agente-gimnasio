"""Configuración central del Agente de Gimnasio v2 con LangChain.

Carga las variables definidas en el archivo `.env` y proporciona la
configuración necesaria para interactuar con la API de Gemini a través
de LangChain.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# .strip() evita fallos si la variable de entorno quedó con un salto de
# línea o espacios invisibles al pegarla en el proveedor de despliegue.
GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or "").strip()
GEMINI_MODEL = (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash").strip()


def validar_configuracion() -> None:
    """Valida que la configuración necesaria para Gemini sea correcta.

    Raises:
        ValueError: Si `GEMINI_API_KEY` no está definida o conserva el valor
            de ejemplo.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "tu_api_key_aqui":
        raise ValueError(
            "Configura una API Key válida en el archivo .env "
            "usando GEMINI_API_KEY."
        )
