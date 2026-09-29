"""Tool con Chain anidada: genera una recomendación priorizada.

Este es el patrón avanzado de la guía: la Tool consulta primero datos
estructurados (la rutina más adecuada, vía `tools.rutina_tool`) y luego
invoca una Chain de LangChain (`chains.recomendacion_chain`) para
convertir esos datos, junto con el contexto del usuario (objetivo,
molestias, restricciones), en una recomendación priorizada y
personalizada en lenguaje natural.
"""

from langchain.tools import tool

from chains.recomendacion_chain import crear_recomendacion_chain, serializar_rutina
from tools.rutina_tool import _buscar_rutinas


@tool
def generar_recomendacion_priorizada(
    objetivo: str = "",
    nivel: str = "",
    dias: int = 0,
    contexto: str = "",
) -> str:
    """Genera una recomendación de entrenamiento priorizada y personalizada.

    Busca primero la rutina más adecuada según objetivo, nivel y días
    disponibles, y luego usa una Chain de LangChain para priorizar y
    adaptar esa rutina considerando el contexto adicional del usuario
    (por ejemplo, una molestia, una lesión o una preferencia particular).

    Args:
        objetivo: Objetivo de entrenamiento del usuario.
        nivel: Nivel de experiencia del usuario.
        dias: Días por semana disponibles para entrenar.
        contexto: Información adicional a considerar, como molestias,
            restricciones o preferencias mencionadas por el usuario.

    Returns:
        Texto breve con la recomendación priorizada, en un máximo de 5
        puntos, generado a partir de la rutina encontrada.
    """
    resultado_rutina = _buscar_rutinas(objetivo, nivel, dias)

    chain = crear_recomendacion_chain()

    return chain.invoke(
        {
            "rutina": serializar_rutina(resultado_rutina.get("resultados", [])),
            "contexto": contexto or "Sin restricciones adicionales.",
        }
    )
