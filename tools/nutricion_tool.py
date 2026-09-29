"""Utilidades de nutrición deportiva: guías generales y cálculo de macros."""

import json
from pathlib import Path

from langchain.tools import tool

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "nutricion.json"

FACTORES_ACTIVIDAD = {
    "sedentario": 1.2,
    "ligero": 1.375,
    "moderado": 1.55,
    "activo": 1.725,
    "muy_activo": 1.9,
}


def _cargar_nutricion() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def _buscar_guia_nutricional(objetivo: str) -> dict:
    guias = _cargar_nutricion()
    objetivo_norm = objetivo.lower().strip().replace(" ", "_")

    if objetivo_norm not in guias:
        return {
            "objetivo": objetivo,
            "encontrado": False,
            "mensaje": "No se encontró una guía para ese objetivo. "
            "Usa uno de: hipertrofia, perdida_grasa, mantenimiento, fuerza, resistencia.",
        }

    return {"objetivo": objetivo_norm, "encontrado": True, **guias[objetivo_norm]}


def _calcular_macros(
    peso_kg: float,
    altura_cm: float,
    edad: int,
    sexo: str,
    nivel_actividad: str,
    objetivo: str,
) -> dict:
    guias = _cargar_nutricion()
    objetivo_norm = objetivo.lower().strip().replace(" ", "_")
    guia = guias.get(objetivo_norm, guias["mantenimiento"])

    sexo_norm = sexo.lower().strip()
    if sexo_norm in ("hombre", "masculino", "m"):
        tmb = 10 * peso_kg + 6.25 * altura_cm - 5 * edad + 5
    else:
        tmb = 10 * peso_kg + 6.25 * altura_cm - 5 * edad - 161

    factor = FACTORES_ACTIVIDAD.get(nivel_actividad.lower().strip(), 1.375)
    tdee = tmb * factor

    calorias_objetivo = tdee * (1 + guia["ajuste_calorico_pct"] / 100)

    proteina_g = guia["proteina_g_por_kg"] * peso_kg
    grasa_g = guia["grasa_g_por_kg"] * peso_kg
    calorias_restantes = calorias_objetivo - (proteina_g * 4) - (grasa_g * 9)
    carbohidratos_g = max(calorias_restantes / 4, 0)

    return {
        "tmb_kcal": round(tmb),
        "gasto_calorico_total_kcal": round(tdee),
        "calorias_objetivo_kcal": round(calorias_objetivo),
        "objetivo": objetivo_norm,
        "macros_diarios": {
            "proteina_g": round(proteina_g),
            "grasa_g": round(grasa_g),
            "carbohidratos_g": round(carbohidratos_g),
        },
    }


@tool
def consultar_nutricion(objetivo: str) -> dict:
    """Devuelve la guía nutricional general para un objetivo de entrenamiento.

    Args:
        objetivo: Objetivo del usuario. Valores esperados: "hipertrofia",
            "perdida_grasa", "mantenimiento", "fuerza" o "resistencia".

    Returns:
        Diccionario con la descripción, el ajuste calórico recomendado,
        las referencias de macronutrientes por kilogramo, consejos
        prácticos y alimentos recomendados.
    """
    return _buscar_guia_nutricional(objetivo)


@tool
def calcular_macros(
    peso_kg: float,
    altura_cm: float,
    edad: int,
    sexo: str,
    nivel_actividad: str,
    objetivo: str,
) -> dict:
    """Calcula el gasto calórico diario y la distribución de macronutrientes.

    Usa la ecuación de Mifflin-St Jeor para estimar la tasa metabólica
    basal (TMB), la multiplica por un factor de actividad para obtener el
    gasto calórico total (TDEE) y aplica el ajuste calórico correspondiente
    al objetivo del usuario.

    Args:
        peso_kg: Peso corporal del usuario en kilogramos.
        altura_cm: Estatura del usuario en centímetros.
        edad: Edad del usuario en años.
        sexo: "hombre" o "mujer".
        nivel_actividad: Uno de "sedentario", "ligero", "moderado",
            "activo" o "muy_activo".
        objetivo: Objetivo del usuario, usado para el ajuste calórico y
            la referencia de proteína/grasa por kilogramo.

    Returns:
        Diccionario con la TMB, el gasto calórico total, las calorías
        objetivo y los gramos recomendados de proteína, grasa y
        carbohidratos por día.
    """
    return _calcular_macros(peso_kg, altura_cm, edad, sexo, nivel_actividad, objetivo)
