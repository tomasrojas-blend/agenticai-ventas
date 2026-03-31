from agent.graph import sales_graph


def run_orchestrator(user_prompt: str, previous_intent: dict | None = None) -> dict:
    result = sales_graph.invoke(
        {
            "user_prompt": user_prompt,
            "previous_intent": previous_intent,
            "intent": None,
            "sql": None,
            "data": None,
            "message": None,
            "error": None,
        }
    )

    if result.get("error"):
        return {"ok": False, "error": result["error"]}

    return {
        "ok": True,
        "intent": result["intent"],
        "sql": result["sql"],
        "data": result["data"],
        "message": result["message"],
    }