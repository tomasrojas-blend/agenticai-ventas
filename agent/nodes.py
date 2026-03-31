from agent.sql_generator import generate_sql
from services.bedrock_service import parse_intent_with_bedrock
from services.mcp_service import run_query_mcp
from services.response_service import build_natural_response


def normalize_presentation(intent: dict, user_prompt: str) -> dict:
    prompt = user_prompt.lower()

    chart_words = ["grafica", "gráfica", "grafico", "gráfico", "visualiza", "visualización"]
    file_words = ["excel", "csv", "archivo", "descarga", "descárgalo", "exporta", "guarda"]
    table_words = ["tabla", "tabular"]

    asked_chart = any(word in prompt for word in chart_words)
    asked_file = any(word in prompt for word in file_words)
    asked_table = any(word in prompt for word in table_words)

    normalized = intent.copy()

    if asked_chart:
        normalized["presentation"] = "chart"
        return normalized

    if asked_file:
        normalized["presentation"] = "file"
        return normalized

    if asked_table:
        normalized["presentation"] = "table"
        return normalized

    normalized["presentation"] = "table"
    return normalized


def refine_intent_for_chart(intent: dict, df):
    if intent.get("presentation") != "chart":
        return intent

    if df is not None and len(df) >= 2:
        return intent

    filters = intent.get("filters", {})
    loterias = filters.get("loterias", [])
    anio = filters.get("anio")

    if anio is not None and len(loterias) >= 1:
        refined = intent.copy()
        refined["dimensions"] = ["anio", "mes", "loteria"]
        refined["sort"] = [
            {"field": "anio", "direction": "asc"},
            {"field": "mes", "direction": "asc"},
        ]
        return refined

    return intent


def parse_intent_node(state):
    intent = parse_intent_with_bedrock(
        user_prompt=state["user_prompt"],
        previous_intent=state.get("previous_intent"),
    )

    if "error" in intent:
        return {"error": intent["error"]}

    intent = normalize_presentation(intent, state["user_prompt"])
    return {"intent": intent}


def generate_sql_node(state):
    sql = generate_sql(state["intent"])
    return {"sql": sql}


def run_query_node(state):
    df = run_query_mcp(state["sql"])
    return {"data": df}


def refine_chart_node(state):
    intent = state["intent"]
    df = state["data"]

    refined_intent = refine_intent_for_chart(intent, df)

    if refined_intent != intent:
        sql = generate_sql(refined_intent)
        df = run_query_mcp(sql)
        return {
            "intent": refined_intent,
            "sql": sql,
            "data": df,
        }

    return {}


def build_response_node(state):
    df = state["data"]
    intent = state["intent"]

    message = build_natural_response(intent, row_count=len(df))
    return {"message": message}