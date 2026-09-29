"""Tool para obtener la fecha y el día actual."""

from datetime import datetime

from langchain.tools import tool

DIAS = {
    0: "lunes",
    1: "martes",
    2: "miércoles",
    3: "jueves",
    4: "viernes",
    5: "sábado",
    6: "domingo",
}


@tool
def obtener_fecha() -> dict:
    """Obtiene la fecha actual, el día de la semana y la hora.

    Útil para saber qué día de entrenamiento le corresponde al usuario
    según su rutina, o para calcular cuántos días faltan para un evento.

    Returns:
        Diccionario con la fecha (AAAA-MM-DD), el día de la semana en
        español y la hora actual (HH:MM).
    """
    ahora = datetime.now()

    return {
        "fecha": ahora.strftime("%Y-%m-%d"),
        "dia": DIAS[ahora.weekday()],
        "hora": ahora.strftime("%H:%M"),
    }
