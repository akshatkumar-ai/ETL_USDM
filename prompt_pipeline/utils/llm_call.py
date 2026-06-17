import boto3
import json
import os

from dotenv import load_dotenv

load_dotenv()


# =========================================================
# BEDROCK CLIENT
# =========================================================

def get_bedrock_client():
    print("*" * 50)
    print("Connecting to AWS BEDROCK....")

    import boto3
    from dotenv import load_dotenv

    load_dotenv(".env")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
    AWS_REGION = "us-east-1"

    if not AWS_ACCESS_KEY_ID:
        raise ValueError("AWS_ACCESS_KEY_ID is missing in the environment variables.")
    if not AWS_SECRET_ACCESS_KEY:
        raise ValueError("AWS_SECRET_ACCESS_KEY is missing in the environment variables.")
    if not AWS_SESSION_TOKEN:
        raise ValueError("AWS_SESSION_TOKEN is missing in the environment variables.")

    try:
        client = boto3.client(
            "bedrock-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN,
            config=boto3.session.Config(read_timeout=2000),
        )
        print("*" * 50)
        return client
    except Exception as e:
        print(e)
        raise ValueError("Error in loading BEDROCK client!")


DEFAULT_MODEL_ID = (
    "arn:aws:bedrock:us-east-1:533267065792:"
    "inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
)

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
    model_id: str = None
):

    if model_id is None:

        model_id = os.getenv("MODEL_ID", DEFAULT_MODEL_ID)

    client = get_bedrock_client()

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

    # Add system prompt separately
    if system_prompt.strip():
        body["system"] = system_prompt.strip()

    # Optional stop sequences
    if stop:
        body["stop_sequences"] = stop

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

        print(f"\n Bedrock API Error: {e}")

        return ""