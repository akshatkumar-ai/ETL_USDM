import boto3
import json
import os

from dotenv import load_dotenv

load_dotenv()


DEFAULT_MODEL_ID = (
    "arn:aws:bedrock:us-east-1:533267065792:"
    "inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
)


def get_bedrock_client():

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

    return boto3.client(
        "bedrock-runtime",
        region_name="us-east-1",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        aws_session_token=AWS_SESSION_TOKEN,
        config=boto3.session.Config(read_timeout=2000),
    )


def llm_call(
    prompt,
    system_prompt="",
    temperature=0.0,
    max_tokens=4000,
):

    client = get_bedrock_client()

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    if system_prompt:
        body["system"] = system_prompt

    response = client.invoke_model(
        modelId=DEFAULT_MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    response_body = json.loads(response["body"].read())

    return response_body["content"][0]["text"]