import json


# =========================================================
# SYSTEM INSTRUCTIONS
# =========================================================

SYSTEM_PROMPT = """
You are a clinical trial data extraction expert specializing in CDISC USDM v4.0.

Your task is to extract structured information from clinical trial documents
and populate a provided USDM JSON sub-schema.

STRICT RULES:

1. Extract ONLY information explicitly stated in the text
2. NEVER invent, infer, or hallucinate values
3. Leave fields empty/null if information is missing
4. Preserve the provided JSON structure exactly
5. Maintain all existing keys and nesting
6. Return ONLY valid JSON
7. Do NOT include markdown
8. Do NOT include explanations
9. Do NOT remove fields
10. Populate only fields relevant to the document section

You must behave as a deterministic structured extraction engine.
"""


# =========================================================
# BUILD USER PROMPT
# =========================================================

def build_prompt(section_name,
                 chunk_text,
                 subschema):
    """
    Build extraction prompt for Claude.

    Args:
        section_name (str)
        chunk_text (str)
        subschema (dict)

    Returns:
        str
    """

    schema_json = json.dumps(
        subschema,
        indent=2
    )

    prompt = f"""
USDM SUB-SCHEMA TO POPULATE:

{schema_json}


DOCUMENT SECTION:
{section_name}


DOCUMENT TEXT:
\"\"\"
{chunk_text}
\"\"\"


TASK:

Populate the USDM sub-schema using ONLY information explicitly present
in the document section.

If information is absent:
- leave arrays empty
- leave objects unchanged
- do not invent values

Return ONLY valid JSON.
"""

    return prompt


# =========================================================
# FULL MESSAGE PAYLOAD
# =========================================================

def build_messages(section_name,
                   chunk_text,
                   subschema):
    """
    Build Claude-compatible message payload.
    """

    user_prompt = build_prompt(
        section_name,
        chunk_text,
        subschema
    )

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": user_prompt
        }
    ]

    return messages


# =========================================================
# TEST
# =========================================================

# if __name__ == "__main__":

#     sample_chunk = """
# OBJECTIVES

# Primary Objective:
# To evaluate efficacy of Drug X compared to placebo.

# Secondary Objective:
# To assess safety and tolerability.
# """

#     sample_schema = {
#         "study": {
#             "versions": [
#                 {
#                     "studyDesigns": [
#                         {
#                             "objectives": []
#                         }
#                     ]
#                 }
#             ]
#         }
#     }

#     messages = build_messages(
#         section_name="objectives",
#         chunk_text=sample_chunk,
#         subschema=sample_schema
#     )

#     print(messages[1]["content"])