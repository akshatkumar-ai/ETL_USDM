from utils.llm_call import llm_call


SYSTEM_PROMPT = """
You are a clinical protocol segmentation expert.

Split the document into semantically coherent
USDM extraction units.

Return ONLY JSON list:

[
  {
    "header": "...",
    "text": "..."
  }
]
"""


def llm_dynamic_chunking(raw_text):

    response = llm_call(

        prompt=raw_text[:50000],

        system_prompt=SYSTEM_PROMPT,

        temperature=0
    )

    return response