from tools.ejercicio_tool import consultar_ejercicio
from tools.fecha_tool import obtener_fecha
from tools.nutricion_tool import calcular_macros, consultar_nutricion
from tools.recomendacion_tool import generar_recomendacion_priorizada
from tools.rutina_tool import consultar_rutina
from tools.rag_tool import buscar_conocimiento_gimnasio

TOOLS_GIMNASIO = [
    obtener_fecha,
    consultar_ejercicio,
    consultar_nutricion,
    calcular_macros,
    consultar_rutina,
    generar_recomendacion_priorizada,
    buscar_conocimiento_gimnasio,
]