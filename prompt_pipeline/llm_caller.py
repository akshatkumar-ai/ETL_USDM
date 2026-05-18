import json

from utils.llm_call import llm_call


# =========================================================
# CLEAN JSON RESPONSE
# =========================================================

def clean_json_response(text):

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")

    if text.startswith("```"):
        text = text.replace("```", "")

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# =========================================================
# PARSE JSON
# =========================================================

def parse_json_response(text):

    cleaned = clean_json_response(text)

    return json.loads(cleaned)


# =========================================================
# EXTRACT SECTION
# =========================================================

def extract_usdm_section(
    messages,
    retry_attempts=1
):

    system_prompt = messages[0]["content"]

    user_prompt = messages[1]["content"]

    for attempt in range(retry_attempts + 1):

        try:

            raw_response = llm_call(

                prompt=user_prompt,

                system_prompt=system_prompt,

                temperature=0.0,

                max_tokens=4000
            )

            parsed = parse_json_response(
                raw_response
            )

            return parsed

        except Exception as e:

            print(f"\n JSON Parse Failed")
            print(f"Attempt: {attempt + 1}")
            print(f"Error: {e}")

            if attempt < retry_attempts:

                user_prompt += """

IMPORTANT:
Return ONLY raw JSON.
No markdown.
No explanations.
"""

            else:

                return {
                    "error": str(e),
                    "raw_response": raw_response if 'raw_response' in locals() else None
                }