# 🏋️ Agente de Gimnasio – GYM AI

Agente conversacional desarrollado con inteligencia artificial para brindar orientación sobre entrenamiento físico, rutinas de ejercicio y nutrición. El proyecto utiliza tecnologías de orquestación de agentes para procesar las consultas de los usuarios y mantener el contexto de las conversaciones.

## 🌐 Enlaces del proyecto

- **Aplicación desplegada:** https://agente-gimnasio.onrender.com
- **Repositorio GitHub:** https://github.com/samulondo/agente-gimnasio

## 👥 Integrantes

- Samuel Londoño Parra
- Karen Zúñiga Muriel

**Universidad Católica Luis Amigó**  
Ingeniería en Sistemas  
Asignatura: Sistemas Agénticos y Orquestadores de IA

## 🎯 Objetivo del proyecto

Desarrollar un agente conversacional que permita a los usuarios realizar consultas relacionadas con el entrenamiento físico, recibir recomendaciones de rutinas y obtener orientación sobre nutrición, utilizando modelos de inteligencia artificial y herramientas de recuperación de información.

## ⚙️ Tecnologías utilizadas

- **Python:** lenguaje de programación principal.
- **Streamlit:** desarrollo de la interfaz web.
- **LangChain:** integración con el modelo de inteligencia artificial.
- **LangGraph:** organización y orquestación del flujo de trabajo del agente.
- **Google Gemini:** modelo de inteligencia artificial utilizado para generar respuestas.
- **RAG (Retrieval-Augmented Generation):** recuperación de información desde una base de conocimiento.
- **Git y GitHub:** control de versiones y almacenamiento del código.
- **Render:** despliegue de la aplicación web.

## ✨ Funcionalidades

- Interacción conversacional con el agente de gimnasio.
- Generación de recomendaciones de rutinas de entrenamiento.
- Consultas relacionadas con ejercicios y nutrición.
- Conservación del contexto de la conversación mediante memoria.
- Organización del procesamiento mediante LangGraph.
- Integración de herramientas para ampliar las capacidades del agente.
- Recuperación de información mediante el enfoque RAG.
- Historial de conversación.
- Identificación de sesiones mediante Thread ID.
- Visualización del flujo de ejecución de LangGraph.
- Indicadores de procesamiento y manejo de errores.

## 📂 Estructura general del proyecto

La organización del proyecto incluye los siguientes componentes:

```text
agente-gimnasio/
│
├── app.py
├── config/
│   └── settings.py
│
├── core/
│   ├── nodes.py
│   ├── session.py
│   └── state.py
│
├── tools/
│   ├── __init__.py
│   └── rag_tool.py
│
├── tests/
│   └── test_tools.py
│
├── .streamlit/
│   └── config.toml
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 💻 Requisitos

Para ejecutar el proyecto localmente se necesita:

- Python instalado.
- Git instalado.
- Una clave API válida de Google Gemini.
- Conexión a internet para

