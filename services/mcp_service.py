import os
import json
import asyncio
import pandas as pd
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
POSTGRES_URL = os.getenv("POSTGRES_URL")


def _build_client():
    if not POSTGRES_URL:
        raise ValueError("Falta POSTGRES_URL en .env")

    return MultiServerMCPClient({
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", POSTGRES_URL],
            "transport": "stdio",
        }
    })


def _to_dataframe(result) -> pd.DataFrame:
    # Caso 1: lista de bloques MCP
    if isinstance(result, list) and len(result) > 0:
        first = result[0]

        if isinstance(first, dict) and "text" in first:
            parsed = json.loads(first["text"])
            df = pd.DataFrame(parsed)

            # convertir números si vienen como texto
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="ignore")

            return df

    # Caso 2: dict con artifact
    if isinstance(result, dict):
        if "artifact" in result and result["artifact"] is not None:
            artifact = result["artifact"]
            df = pd.DataFrame(artifact if isinstance(artifact, list) else [artifact])
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            return df

        if "content" in result and isinstance(result["content"], str):
            parsed = json.loads(result["content"])
            df = pd.DataFrame(parsed if isinstance(parsed, list) else [parsed])
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            return df

    # Caso 3: string JSON directo
    if isinstance(result, str):
        parsed = json.loads(result)
        df = pd.DataFrame(parsed if isinstance(parsed, list) else [parsed])
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")
        return df

    raise ValueError(f"No pude convertir la respuesta MCP a DataFrame: {result}")


async def _run_query_async(sql: str) -> pd.DataFrame:
    client = _build_client()
    tools = await client.get_tools()

    query_tool = None
    for tool in tools:
        if tool.name == "query":
            query_tool = tool
            break

    if query_tool is None:
        raise ValueError("No se encontró la tool 'query' del MCP")

    result = await query_tool.ainvoke({"sql": sql})
    return _to_dataframe(result)


def run_query_mcp(sql: str) -> pd.DataFrame:
    return asyncio.run(_run_query_async(sql))