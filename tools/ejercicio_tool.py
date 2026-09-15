"""Utilidades para la consulta de ejercicios específicos.

Este módulo permite buscar ejercicios por nombre, grupo muscular o equipo
disponible dentro de la base de datos de ejercicios de la aplicación.
"""

import json
from pathlib import Path
from typing import TypedDict


class Ejercicio(TypedDict):
    """Representa un ejercicio de la base de datos."""

    nombre: str
    grupo_muscular: str
    equipo: str
    nivel: str
    series_repeticiones: str
    tecnica: str
    alternativas: list[str]


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "ejercicios.json"


def consultar_ejercicio(consulta: str) -> dict:
    """Busca ejercicios según nombre, grupo muscular o equipo.

    La búsqueda no distingue entre mayúsculas y minúsculas y permite
    coincidencias parciales, por lo que también sirve para listar todos
    los ejercicios de un grupo muscular (por ejemplo, "pierna" o "core").

    Args:
        consulta: Nombre del ejercicio, grupo muscular o equipo utilizado
            como criterio de búsqueda.

    Returns:
        Diccionario con la consulta realizada, la lista de ejercicios que
        coinciden y la cantidad de resultados encontrados.
    """
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        ejercicios: list[Ejercicio] = json.load(archivo)

    criterio = consulta.lower().strip()

    resultados = [
        ejercicio
        for ejercicio in ejercicios
        if criterio in ejercicio["nombre"].lower()
        or criterio in ejercicio["grupo_muscular"].lower()
        or criterio in ejercicio["equipo"].lower()
    ]

    return {
        "consulta": consulta,
        "resultados": resultados,
        "cantidad": len(resultados),
    }
