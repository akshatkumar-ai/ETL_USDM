# config/prompts.py

# =========================================================
# GLOBAL SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are an expert clinical trial USDM extraction system.

Your job is to extract structured USDM-compatible data
from clinical protocol text.

RULES:

1. Extract ONLY information explicitly supported by text.
2. Never hallucinate.
3. Return STRICT valid JSON only.
4. Do not explain anything.
5. Do not include markdown.
6. Preserve hierarchy and arrays.
7. Use null when information is unavailable.
8. Keep extracted text concise.
9. Prefer structured values over free text.
10. Preserve protocol terminology exactly when possible.

IMPORTANT:

- Arrays should be dynamically generated.
- Do NOT invent additional fields.
- Output must exactly follow requested schema.
- Never return prose outside JSON.
"""


# =========================================================
# CLASS EXTRACTION PROMPT
# =========================================================

CLASS_EXTRACTION_TEMPLATE = """
Extract the following USDM class from the protocol text.

CLASS NAME:
{class_name}

EXPECTED USDM STRUCTURE:
{schema}

PROTOCOL TEXT:
{protocol_text}

INSTRUCTIONS:

- Extract ONLY explicitly stated information.
- Return STRICT valid JSON.
- Preserve arrays and nested objects.
- If no information exists, return null or empty arrays.
- Do not include explanations.
- Do not include markdown.

OUTPUT:
"""


# =========================================================
# RETRIEVAL-AWARE EXTRACTION PROMPT
# =========================================================

RETRIEVAL_EXTRACTION_TEMPLATE = """
You are extracting structured USDM information from
retrieved clinical protocol chunks.

USDM CLASS:
{class_name}

EXPECTED STRUCTURE:
{schema}

RETRIEVED PROTOCOL CHUNKS:
{retrieved_chunks}

RULES:

- Use ONLY the retrieved text.
- Do not infer unsupported information.
- Preserve study terminology exactly.
- Return STRICT JSON only.
- Maintain schema hierarchy.
- Create arrays dynamically.
- Use null when unavailable.

OUTPUT JSON:
"""


# =========================================================
# ARRAY ENTITY EXTRACTION PROMPTS
# =========================================================

ARMS_PROMPT = """
Extract all study arms from the protocol.

Return STRICT JSON.

Expected schema:
{
  "arms": [
    {
      "name": "",
      "label": "",
      "description": "",
      "type": ""
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


ENCOUNTERS_PROMPT = """
Extract all study encounters / visits.

Return STRICT JSON.

Expected schema:
{
  "encounters": [
    {
      "name": "",
      "label": "",
      "description": "",
      "type": ""
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


ACTIVITIES_PROMPT = """
Extract all study activities and associated procedures.

Return STRICT JSON.

Expected schema:
{
  "activities": [
    {
      "name": "",
      "description": "",
      "definedProcedures": []
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


OBJECTIVES_PROMPT = """
Extract study objectives and endpoints.

Return STRICT JSON.

Expected schema:
{
  "objectives": [
    {
      "name": "",
      "description": "",
      "text": "",
      "level": "",
      "endpoints": []
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


ELIGIBILITY_PROMPT = """
Extract inclusion and exclusion criteria.

Return STRICT JSON.

Expected schema:
{
  "eligibilityCriteria": [
    {
      "identifier": "",
      "category": "",
      "text": ""
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


INTERVENTIONS_PROMPT = """
Extract study interventions and administrations.

Return STRICT JSON.

Expected schema:
{
  "studyInterventions": [
    {
      "name": "",
      "description": "",
      "role": "",
      "type": "",
      "administrations": []
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


TIMELINE_PROMPT = """
Extract study schedule timelines and timings.

Return STRICT JSON.

Expected schema:
{
  "scheduleTimelines": [
    {
      "name": "",
      "description": "",
      "timings": []
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


ESTIMANDS_PROMPT = """
Extract estimands and intercurrent events.

Return STRICT JSON.

Expected schema:
{
  "estimands": [
    {
      "name": "",
      "description": "",
      "populationSummary": "",
      "intercurrentEvents": []
    }
  ]
}

PROTOCOL TEXT:
{protocol_text}
"""


POPULATION_PROMPT = """
Extract study population and cohorts.

Return STRICT JSON.

Expected schema:
{
  "population": {
    "plannedEnrollmentNumberQuantity": null,
    "plannedSex": "",
    "plannedAge": "",
    "cohorts": []
  }
}

PROTOCOL TEXT:
{protocol_text}
"""


# =========================================================
# VALIDATION / REPAIR PROMPT
# =========================================================

JSON_REPAIR_PROMPT = """
Fix the following malformed JSON.

RULES:
- Return ONLY valid JSON.
- Do not change values.
- Do not add explanations.
- Preserve structure exactly.

MALFORMED JSON:
{bad_json}
"""


# =========================================================
# CONFIDENCE SCORING PROMPT
# =========================================================

CONFIDENCE_EXTRACTION_PROMPT = """
Extract USDM information and provide confidence scores.

Return STRICT JSON.

Expected format:
{
  "field_name": {
    "value": "...",
    "confidence": 0.95,
    "evidence": "exact supporting text"
  }
}

USDM CLASS:
{class_name}

SCHEMA:
{schema}

PROTOCOL TEXT:
{protocol_text}
"""