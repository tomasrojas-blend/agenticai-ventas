from typing import Any, TypedDict


class AgentState(TypedDict):
    user_prompt: str
    previous_intent: dict | None
    intent: dict | None
    sql: str | None
    data: Any
    message: str | None
    error: str | None