"""Utilidades de nutrición deportiva: guías generales y cálculo de macros.

Este módulo expone dos herramientas para el agente:

- ``consultar_nutricion``: devuelve la guía nutricional general asociada
  a un objetivo (hipertrofia, pérdida de grasa, mantenimiento, fuerza o
  resistencia).
- ``calcular_macros``: estima el gasto calórico diario del usuario con la
  fórmula de Mifflin-St Jeor y distribuye las calorías en proteína, grasa
  y carbohidratos según su objetivo.

Estas herramientas ofrecen guías generales de nutrición deportiva y no
reemplazan la valoración de un nutricionista o médico, especialmente en
personas con condiciones de salud particulares.
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "nutricion.json"

# Factor de actividad física utilizado en la fórmula de Harris/Mifflin.
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


def consultar_nutricion(objetivo: str) -> dict:
    """Devuelve la guía nutricional general para un objetivo de entrenamiento.

    Args:
        objetivo: Objetivo del usuario. Valores esperados: "hipertrofia",
            "perdida_grasa", "mantenimiento", "fuerza" o "resistencia".

    Returns:
        Diccionario con la descripción, el ajuste calórico recomendado,
        las referencias de macronutrientes por kilogramo, consejos
        prácticos y alimentos recomendados. Si el objetivo no existe en
        la base de datos, incluye una lista vacía y un mensaje aclaratorio.
    """
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
    al objetivo del usuario. Finalmente distribuye las calorías resultantes
    en proteína, grasa y carbohidratos.

    Args:
        peso_kg: Peso corporal del usuario en kilogramos.
        altura_cm: Estatura del usuario en centímetros.
        edad: Edad del usuario en años.
        sexo: "hombre" o "mujer" (usado únicamente para el ajuste de la
            fórmula de Mifflin-St Jeor).
        nivel_actividad: Uno de "sedentario", "ligero", "moderado",
            "activo" o "muy_activo".
        objetivo: Objetivo del usuario, usado para aplicar el ajuste
            calórico y la referencia de proteína/grasa por kilogramo.

    Returns:
        Diccionario con la TMB, el gasto calórico total, las calorías
        objetivo y los gramos recomendados de proteína, grasa y
        carbohidratos por día.
    """
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
