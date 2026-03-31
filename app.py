import pandas as pd
import streamlit as st
from agent.orchestrator import run_orchestrator
from services.chart_service import build_chart
from services.export_service import dataframe_to_csv_bytes, dataframe_to_excel_bytes

st.set_page_config(page_title="Agente de Ventas", page_icon="📊", layout="centered")

st.title("📊 Agente de análisis de ventas")
st.write("Consulta ventas de loterías en lenguaje natural.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hola. Soy tu agente de análisis de ventas. Pregúntame por ventas, rankings, gráficos o archivos."
        }
    ]

if "last_intent" not in st.session_state:
    st.session_state.last_intent = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input("Escribe tu consulta...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                result = run_orchestrator(
                    user_prompt=user_prompt,
                    previous_intent=st.session_state.last_intent
                )

                if not result["ok"]:
                    st.error(result["error"])
                    assistant_content = result["error"]
                else:
                    intent = result["intent"]
                    sql = result["sql"]
                    df = result["data"]
                    assistant_content = result["message"]

                    # guardar intención válida para follow-up
                    st.session_state.last_intent = intent

                    st.markdown(assistant_content)

                    df_display = df.copy()

                    if "total_ventas" in df_display.columns:
                        df_display["total_ventas"] = df_display["total_ventas"].apply(
                            lambda x: f"COP {x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
                        )
                    elif "ventas" in df_display.columns:
                        df_display["ventas"] = df_display["ventas"].apply(
                            lambda x: f"COP {x:,.0f}".replace(",", ".") if pd.notnull(x) else ""
                        )

                    presentation = intent.get("presentation", "table")

                    if presentation == "table":
                        st.dataframe(df_display, use_container_width=True)

                    elif presentation == "chart":
                        chart = build_chart(df, intent)
                        if chart:
                            st.plotly_chart(chart, use_container_width=True)
                        else:
                            st.info("No encontré suficientes datos para graficar, así que te muestro la tabla.")
                            st.dataframe(df_display, use_container_width=True)

                    elif presentation == "file":
                        st.dataframe(df_display, use_container_width=True)

                        if not df.empty:
                            csv_bytes = dataframe_to_csv_bytes(df)
                            excel_bytes = dataframe_to_excel_bytes(df)

                            col1, col2 = st.columns(2)

                            with col1:
                                st.download_button(
                                    label="Descargar CSV",
                                    data=csv_bytes,
                                    file_name="resultado_ventas.csv",
                                    mime="text/csv",
                                )

                            with col2:
                                st.download_button(
                                    label="Descargar Excel",
                                    data=excel_bytes,
                                    file_name="resultado_ventas.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                )

            except Exception as e:
                st.error(f"Error al procesar la consulta: {str(e)}")
                assistant_content = "No pude procesar tu consulta en este momento."

    st.session_state.messages.append({"role": "assistant", "content": assistant_content})