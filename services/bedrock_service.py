import os
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from prompts.sales_prompt import SYSTEM_PROMPT

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
MODEL_ID = os.getenv("MODEL_ID")
AWS_PROFILE = os.getenv("AWS_PROFILE")


def _extract_json(text: str) -> dict:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        return json.loads(candidate)

    raise json.JSONDecodeError("No JSON object found", text, 0)


def parse_intent_with_bedrock(
    user_prompt: str,
    previous_intent: dict | None = None
) -> dict:
    if not AWS_REGION or not MODEL_ID or not AWS_PROFILE:
        return {
            "error": "Faltan AWS_REGION, MODEL_ID o AWS_PROFILE en el archivo .env."
        }

    try:
        session = boto3.Session(
            profile_name=AWS_PROFILE,
            region_name=AWS_REGION
        )
        client = session.client("bedrock-runtime")

        user_message = f"""
Solicitud actual del usuario:
{user_prompt}

Última intención válida previa:
{json.dumps(previous_intent, ensure_ascii=False) if previous_intent else "null"}

Reglas de seguimiento:
- Si la nueva solicitud modifica la anterior, reutiliza el contexto previo.
- Si solo cambia la presentación, conserva filtros, dimensiones, orden y límite.
- Si el usuario dice cosas como "ahora en gráfico", "en excel", "solo 2024", "solo Bogotá", "por mes", "quita el filtro", interpreta eso como follow-up.
- Devuelve únicamente JSON válido.
""".strip()

        response = client.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT}],
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_message}]
                }
            ],
            inferenceConfig={
                "maxTokens": 500,
                "temperature": 0.1
            }
        )

        text = "".join(
            block["text"]
            for block in response["output"]["message"]["content"]
            if "text" in block
        ).strip()

        return _extract_json(text)

    except ClientError as e:
        return {"error": f"Error de Bedrock/AWS: {e.response['Error']['Message']}"}
    except json.JSONDecodeError:
        return {"error": "Bedrock no devolvió JSON válido."}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}