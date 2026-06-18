# utils/llm_call.py

import os
import json
import boto3

from dotenv import load_dotenv


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()


# =========================================================
# DEFAULT MODEL
# =========================================================

DEFAULT_MODEL_ID = (
    "arn:aws:bedrock:us-east-1:533267065792:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
)


# =========================================================
# BEDROCK CLIENT
# =========================================================

def get_bedrock_client():

    print("*" * 80)
    print("Connecting to AWS Bedrock...")
    print("*" * 80)

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

    AWS_REGION = "us-east-1"

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not AWS_ACCESS_KEY_ID:
        raise ValueError(
            "AWS_ACCESS_KEY_ID missing in .env"
        )

    if not AWS_SECRET_ACCESS_KEY:
        raise ValueError(
            "AWS_SECRET_ACCESS_KEY missing in .env"
        )

    if not AWS_SESSION_TOKEN:
        raise ValueError(
            "AWS_SESSION_TOKEN missing in .env"
        )

    # -----------------------------------------------------
    # CLIENT
    # -----------------------------------------------------

    try:
        
        client = boto3.client(
            "bedrock-runtime",

            region_name=AWS_REGION,

            aws_access_key_id=AWS_ACCESS_KEY_ID,

            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,

            aws_session_token=AWS_SESSION_TOKEN,

            config=boto3.session.Config(
                read_timeout=2000
            ),
        )

        print("Bedrock client connected.")

        return client

    except Exception as e:

        print("\nERROR INITIALIZING BEDROCK CLIENT")
        print(e)

        raise


# =========================================================
# GENERIC LLM CALL
# =========================================================

def llm_call(
    prompt: str,
    system_prompt: str = "",
    temperature: float = 0.0,
    max_tokens: int = 4000,
    top_p: float = 1.0,
    stop: list = None,

    model: str = None,
    model_id: str = None,
) -> str:

    # -----------------------------------------------------
    # MODEL
    # -----------------------------------------------------

    if model_id is None:

        model_id = model

    if model_id is None:

        model_id = os.getenv(
            
            DEFAULT_MODEL_ID
        )

    # -----------------------------------------------------
    # CLIENT
    # -----------------------------------------------------

    client = get_bedrock_client()
    

    # -----------------------------------------------------
    # REQUEST BODY
    # -----------------------------------------------------

    body = {

        "anthropic_version": "bedrock-2023-05-31",

        "max_tokens": max_tokens,

        "temperature": temperature,

        "top_p": top_p,

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    # -----------------------------------------------------
    # SYSTEM PROMPT
    # -----------------------------------------------------

    if system_prompt.strip():

        body["system"] = system_prompt.strip()

    # -----------------------------------------------------
    # STOP SEQUENCES
    # -----------------------------------------------------

    if stop:

        body["stop_sequences"] = stop

    # -----------------------------------------------------
    # API CALL
    # -----------------------------------------------------

    try:
        
        response = client.invoke_model(

            modelId=model_id,

            body=json.dumps(body),

            contentType="application/json",

            accept="application/json"
        )

        response_body = json.loads(
            response["body"].read()
        )

        return response_body["content"][0]["text"]

    except Exception as e:

        print("\nBEDROCK API ERROR")
        print(e)

        return ""