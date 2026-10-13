from tools.ejercicio_tool import consultar_ejercicio
from tools.fecha_tool import obtener_fecha
from tools.nutricion_tool import consultar_nutricion
from tools.recomendacion_tool import obtener_recomendaciones
from tools.rutina_tool import consultar_rutina

TOOLS_GIMNASIO = [
    obtener_fecha,
    consultar_ejercicio,
    consultar_nutricion,
    consultar_rutina,
    obtener_recomendaciones,
]