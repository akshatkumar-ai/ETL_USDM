import json
import re


def safe_json_load(response):

    if not response:
        return {}

    response = response.strip()

    # remove markdown fences
    response = re.sub(r"^```json", "", response)
    response = re.sub(r"^```", "", response)
    response = re.sub(r"```$", "", response)

    response = response.strip()

    # try direct parse
    try:
        return json.loads(response)

    except Exception:

        pass

    # fallback: extract first json object
    match = re.search(r"\{.*\}", response, re.DOTALL)

    if match:

        try:

            return json.loads(match.group())

        except Exception:

            pass

    print("\nFAILED RESPONSE:\n")
    print(response)

    return {}