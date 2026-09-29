"""Chain para generar una recomendación de entrenamiento priorizada.

Esta Chain se invoca desde dentro de una Tool
(`tools/recomendacion_tool.py`), tomando como entrada una rutina ya
filtrada por objetivo/nivel/días y el contexto adicional del usuario
(por ejemplo, una molestia o restricción), para producir una
recomendación breve y priorizada en lenguaje natural.
"""

import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import GEMINI_API_KEY, GEMINI_MODEL

RECOMENDACION_SYSTEM_PROMPT = """
Prioriza y adapta la rutina de entrenamiento usando exclusivamente los
datos proporcionados. Considera el objetivo, el nivel, y cualquier
molestia o restricción mencionada en el contexto adicional. No inventes
ejercicios que no estén en la rutina. Si el contexto menciona dolor o
una lesión en una zona, indica qué ejercicio de la rutina debería
evitarse o sustituirse por una alternativa más segura, y aclara que se
debe consultar a un profesional de la salud antes de continuar con esa
parte del entrenamiento. Devuelve una recomendación breve, en un máximo
de 5 puntos, ordenada por prioridad.
""".strip()


def crear_recomendacion_chain():
    """Crea una Chain fija: datos -> prompt -> modelo -> salida."""
    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=0.1,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RECOMENDACION_SYSTEM_PROMPT),
            (
                "human",
                "Rutina disponible:\n{rutina}\n\n"
                "Contexto adicional (objetivo, molestias o restricciones): {contexto}",
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def serializar_rutina(rutina) -> str:
    """Convierte el resultado de la búsqueda de rutinas a JSON legible."""
    return json.dumps(rutina, ensure_ascii=False, indent=2)
