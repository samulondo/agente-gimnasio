"""Integración del agente de gimnasio con la API de Gemini.

Este módulo configura el cliente de Gemini y proporciona las funciones
necesarias para construir el contexto del agente y generar respuestas a
partir de los mensajes del usuario.

El agente utiliza la información conocida del usuario, la memoria
reciente de la conversación y un conjunto de herramientas (rutinas,
ejercicios y nutrición) para responder consultas sobre entrenamiento y
alimentación.
"""

from typing import TypedDict

from google import genai
from google.genai import types

from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from tools.ejercicio_tool import consultar_ejercicio
from tools.nutricion_tool import calcular_macros, consultar_nutricion
from tools.rutina_tool import consultar_rutina


class Usuario(TypedDict):
    """Representa la información de entrenamiento conocida del usuario."""

    nombre: str
    objetivo: str
    nivel: str
    dias_disponibles: str
    peso_kg: str
    altura_cm: str
    edad: str
    sexo: str
    restricciones: list[str]


# Cliente utilizado para realizar solicitudes a la API de Gemini.
client = genai.Client(api_key=GEMINI_API_KEY)


def construir_contexto(usuario: Usuario, memoria: str) -> str:
    """Construye las instrucciones de contexto para el agente de gimnasio.

    Combina la información actual del usuario con la memoria reciente de
    la conversación y las instrucciones que determinan el comportamiento
    del modelo, incluyendo cuándo debe usar cada herramienta disponible y
    las restricciones de seguridad que debe respetar.

    Args:
        usuario: Información de entrenamiento actual del usuario.
        memoria: Representación textual de los mensajes recientes de la
            conversación.

    Returns:
        Instrucción de sistema que se enviará al modelo Gemini como
        contexto.
    """
    restricciones = (
        "; ".join(usuario["restricciones"]) if usuario["restricciones"] else "Ninguna registrada"
    )

    return f"""
Eres un agente de gimnasio: ayudas con rutinas de entrenamiento, técnica de
ejercicios y alimentación deportiva.

ESTADO ACTUAL DEL USUARIO:
Nombre: {usuario["nombre"]}
Objetivo: {usuario["objetivo"]}
Nivel: {usuario["nivel"]}
Días disponibles por semana: {usuario["dias_disponibles"]}
Peso (kg): {usuario["peso_kg"]}
Altura (cm): {usuario["altura_cm"]}
Edad: {usuario["edad"]}
Sexo: {usuario["sexo"]}
Molestias o restricciones mencionadas: {restricciones}

MEMORIA RECIENTE:
{memoria}

Dispones de estas herramientas:
- consultar_rutina: para recomendar una rutina según objetivo, nivel y días disponibles.
- consultar_ejercicio: para explicar la técnica, el grupo muscular o alternativas de un ejercicio.
- consultar_nutricion: para dar una guía general de alimentación según el objetivo.
- calcular_macros: para estimar calorías y macronutrientes diarios cuando el
  usuario ha dado peso, altura, edad, sexo y nivel de actividad.

Usa la herramienta correspondiente en vez de inventar datos de rutinas,
ejercicios o cálculos nutricionales.

Restricciones importantes de seguridad:
- No diagnostiques lesiones ni reemplaces a un médico, fisioterapeuta o
  nutricionista: si el usuario menciona dolor o una lesión, recomienda
  pausar el ejercicio implicado y consultar a un profesional antes de
  continuar con esa parte de la rutina.
- No recomiendes suplementación farmacológica ni dietas extremas.
- No aumentes drásticamente cargas, volumen o restricción calórica sin que
  el usuario lo confirme explícitamente.
- Si el objetivo o los datos del usuario parecen poco realistas o riesgosos,
  sugiere una alternativa más segura en lugar de seguir la petición al pie
  de la letra.

Si puedes responder usando el estado o la memoria, responde directamente.
Sé breve, claro y motivador.
""".strip()


def responder(
    mensaje_usuario: str,
    usuario: Usuario,
    memoria: str,
) -> str:
    """Genera una respuesta del agente de gimnasio mediante Gemini.

    Construye el contexto de la conversación y envía el mensaje del
    usuario al modelo configurado de Gemini. El modelo puede utilizar las
    herramientas de rutinas, ejercicios y nutrición cuando la consulta lo
    requiera.

    Args:
        mensaje_usuario: Mensaje enviado por el usuario.
        usuario: Información de entrenamiento actual del usuario.
        memoria: Representación textual de los mensajes recientes de la
            conversación.

    Returns:
        Respuesta textual generada por Gemini. Si el modelo no devuelve
        contenido textual, se retorna un mensaje predeterminado.
    """
    contexto = construir_contexto(usuario, memoria)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=mensaje_usuario,
        config=types.GenerateContentConfig(
            system_instruction=contexto,
            tools=[consultar_rutina, consultar_ejercicio, consultar_nutricion, calcular_macros],
        ),
    )

    return response.text or "No fue posible generar una respuesta."
