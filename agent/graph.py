from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import (
    parse_intent_node,
    generate_sql_node,
    run_query_node,
    refine_chart_node,
    build_response_node,
)


def route_after_query(state: AgentState) -> str:
    if state.get("error"):
        return "end"

    intent = state["intent"]
    df = state["data"]

    if intent.get("presentation") == "chart" and (df is None or len(df) < 2):
        return "refine_chart"

    return "build_response"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("run_query", run_query_node)
    graph.add_node("refine_chart", refine_chart_node)
    graph.add_node("build_response", build_response_node)

    graph.add_edge(START, "parse_intent")
    graph.add_edge("parse_intent", "generate_sql")
    graph.add_edge("generate_sql", "run_query")

    graph.add_conditional_edges(
        "run_query",
        route_after_query,
        {
            "refine_chart": "refine_chart",
            "build_response": "build_response",
            "end": END,
        },
    )

    graph.add_edge("refine_chart", "build_response")
    graph.add_edge("build_response", END)

    return graph.compile()


sales_graph = build_graph()