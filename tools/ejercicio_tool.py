"""Utilidades para la consulta de ejercicios específicos.

Este módulo permite buscar ejercicios por nombre, grupo muscular o equipo
disponible dentro de la base de datos de ejercicios de la aplicación.
Cada resultado incluye un enlace de video de apoyo (búsqueda en YouTube
generada a partir del nombre del ejercicio) para que el usuario pueda ver
la técnica en video.
"""

import json
from pathlib import Path
from typing import TypedDict
from urllib.parse import quote

from langchain.tools import tool


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


def _url_video(nombre_ejercicio: str) -> str:
    """Genera un enlace de búsqueda en YouTube para un ejercicio.

    Se usa una búsqueda en lugar de un enlace fijo para evitar videos
    rotos o eliminados con el tiempo: el enlace siempre lleva a
    resultados vigentes sobre la técnica de ese ejercicio.

    Args:
        nombre_ejercicio: Nombre del ejercicio.

    Returns:
        URL de búsqueda de YouTube para la técnica del ejercicio.
    """
    consulta = quote(f"{nombre_ejercicio} técnica ejercicio tutorial")
    return f"https://www.youtube.com/results?search_query={consulta}"


def _buscar_ejercicios(consulta: str) -> dict:
    """Busca ejercicios según nombre, grupo muscular o equipo."""
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        ejercicios: list[Ejercicio] = json.load(archivo)

    criterio = consulta.lower().strip()

    resultados = [
        {**ejercicio, "video": _url_video(ejercicio["nombre"])}
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


@tool
def consultar_ejercicio(consulta: str) -> dict:
    """Busca ejercicios según nombre, grupo muscular o equipo.

    La búsqueda permite coincidencias parciales, por lo que también sirve
    para listar todos los ejercicios de un grupo muscular (por ejemplo,
    "pierna" o "core"). Cada resultado incluye un campo "video" con un
    enlace de apoyo para ver la técnica en video.

    Args:
        consulta: Nombre del ejercicio, grupo muscular o equipo utilizado
            como criterio de búsqueda.

    Returns:
        Diccionario con la consulta realizada, la lista de ejercicios que
        coinciden (cada uno con su enlace de video) y la cantidad de
        resultados encontrados.
    """
    return _buscar_ejercicios(consulta)