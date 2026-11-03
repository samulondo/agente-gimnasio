"""Pruebas unitarias básicas de las funciones de consulta del agente."""
from tools.rutina_tool import _buscar_rutinas
from tools.ejercicio_tool import _buscar_ejercicios
from tools.nutricion_tool import _buscar_guia_nutricional


def test_busqueda_rutinas_devuelve_estructura():
    resultado = _buscar_rutinas("hipertrofia", "principiante", 4)
    assert "resultados" in resultado
    assert isinstance(resultado["resultados"], list)
    assert resultado["cantidad"] == len(resultado["resultados"])


def test_busqueda_ejercicio_devuelve_estructura():
    resultado = _buscar_ejercicios("sentadilla")
    assert "resultados" in resultado
    assert isinstance(resultado["resultados"], list)


def test_guia_nutricional_hipertrofia():
    resultado = _buscar_guia_nutricional("hipertrofia")
    assert resultado["encontrado"] is True
