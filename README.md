# 📊 Agente de análisis de ventas con Agentic AI

Aplicación web desarrollada con **Streamlit** que permite consultar datos de ventas en **lenguaje natural**, traducir esas solicitudes a **SQL**, ejecutar las consultas sobre **PostgreSQL** mediante **MCP (Model Context Protocol)** y devolver resultados en **tabla, gráfico, texto o archivo descargable**.

El proyecto implementa un flujo tipo agente con **Amazon Bedrock** para interpretar la intención del usuario, **LangGraph** para modelar el flujo del agente y **MCP PostgreSQL** como conector para consultar la base de datos.

---

## 🚀 Funcionalidades principales

- Interpretación de consultas en lenguaje natural sobre ventas
- Detección semántica de intención con **Amazon Bedrock**
- Generación automática de consultas **SQL**
- Ejecución de consultas en **PostgreSQL** a través de **MCP**
- Respuesta dinámica en:
  - tabla
  - gráfico
  - texto
  - archivo CSV / Excel
- Seguimiento conversacional:
  - reutiliza la intención previa
  - permite refinar consultas
  - permite cambiar solo la presentación
- Gráficos automáticos con **Plotly**
- Exportación de resultados a **CSV** y **Excel**

---

## 🧱 Tecnologías utilizadas

- **Python**
- **Streamlit**
- **Amazon Bedrock**
- **PostgreSQL**
- **MCP PostgreSQL Server**
- **LangGraph**
- **LangChain**
- **Plotly**
- **pandas**
- **python-dotenv**

---

## 🧠 Arquitectura general

El flujo principal del agente es:

1. El usuario escribe una consulta en lenguaje natural
2. Bedrock interpreta la intención semántica
3. El sistema genera una consulta SQL segura
4. La consulta se ejecuta en PostgreSQL mediante MCP
5. El sistema decide cómo presentar el resultado
6. Streamlit muestra la salida como tabla, gráfico, texto o archivo

---

## 📁 Estructura del proyecto

```text
agenticai-ventas/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── agent/
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   ├── orchestrator.py
│   └── sql_generator.py
├── prompts/
│   └── sales_prompt.py
├── services/
    ├── bedrock_service.py
    ├── mcp_service.py
    ├── chart_service.py
    ├── export_service.py
    └── response_service.py
