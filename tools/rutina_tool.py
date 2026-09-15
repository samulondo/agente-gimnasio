"""Utilidades para la consulta de rutinas de entrenamiento.

Este módulo carga y filtra las rutinas almacenadas en el archivo JSON de
datos de la aplicación según el objetivo, el nivel y los días disponibles
del usuario.
"""

import json
from pathlib import Path
from typing import TypedDict


class DiaRutina(TypedDict):
    """Representa un día dentro de una rutina de entrenamiento."""

    dia: str
    enfoque: str
    ejercicios: list[dict]


class Rutina(TypedDict):
    """Representa una rutina completa de entrenamiento."""

    id: str
    nombre: str
    objetivo: str
    nivel: str
    dias_por_semana: int
    notas: str
    dias: list[DiaRutina]


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "rutinas.json"


def consultar_rutina(objetivo: str = "", nivel: str = "", dias: int = 0) -> dict:
    """Busca rutinas de entrenamiento según objetivo, nivel y días disponibles.

    La búsqueda no distingue entre mayúsculas y minúsculas. Si se indica
    ``dias``, se priorizan las rutinas cuyo número de días por semana
    coincide exactamente, y si no hay coincidencia exacta se devuelven
    las más cercanas.

    Args:
        objetivo: Objetivo de entrenamiento del usuario. Valores esperados:
            "hipertrofia", "perdida_grasa", "fuerza", "resistencia".
        nivel: Nivel de experiencia del usuario: "principiante",
            "intermedio" o "avanzado".
        dias: Número de días por semana que el usuario tiene disponibles
            para entrenar. Usa 0 para no filtrar por este criterio.

    Returns:
        Diccionario con la consulta realizada, la lista de rutinas que
        coinciden y la cantidad de resultados encontrados.
    """
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        rutinas: list[Rutina] = json.load(archivo)

    objetivo_norm = objetivo.lower().strip()
    nivel_norm = nivel.lower().strip()

    resultados = [
        rutina
        for rutina in rutinas
        if (not objetivo_norm or objetivo_norm in rutina["objetivo"].lower())
        and (not nivel_norm or nivel_norm in rutina["nivel"].lower())
    ]

    if dias:
        resultados_exactos = [r for r in resultados if r["dias_por_semana"] == dias]
        if resultados_exactos:
            resultados = resultados_exactos
        else:
            resultados = sorted(
                resultados, key=lambda r: abs(r["dias_por_semana"] - dias)
            )[:2]

    return {
        "objetivo": objetivo,
        "nivel": nivel,
        "dias": dias,
        "resultados": resultados,
        "cantidad": len(resultados),
    }
