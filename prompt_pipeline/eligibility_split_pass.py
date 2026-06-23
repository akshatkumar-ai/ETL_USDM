# prompt_pipeline/eligibility_split_pass.py
#
# Splits eligibilityCriterion extraction into two LLM calls — INCLUSION and
# EXCLUSION separately — to reduce per-call extraction burden and make the
# completeness instruction unambiguous for each category.
#
# PREREQUISITE: retriever_fix.py must be applied first. Without it, both
# calls below will receive the same truncated 3-chunk context and you'll
# still be missing data — just split across two calls instead of one.

from __future__ import annotations
import json


INCLUSION_SYSTEM = """You are a clinical trial data extraction expert specializing in CDISC USDM v4.0.

Extract ONLY INCLUSION CRITERIA from the provided text.

STRICT RULES:
1. Extract every inclusion criterion — do not skip any, including sub-items
   and tables (e.g. drug names with washout periods listed under a criterion).
2. One JSON object per distinct criterion. Never merge two into one object.
3. category must be exactly "INCLUSION" for every object.
4. text must be verbatim from the source — no paraphrasing.
5. identifier must be the criterion number/letter exactly as written (e.g. "1", "9", "17a").
6. If a criterion contains a list (e.g. excluded/allowed medications), include
   the full list in the text field — do not drop list items.
7. Return ONLY valid JSON. No markdown, no backticks, no commentary.
8. If no inclusion criteria appear in the text, return {"eligibilityCriteria": []}.
"""

EXCLUSION_SYSTEM = """You are a clinical trial data extraction expert specializing in CDISC USDM v4.0.

Extract ONLY EXCLUSION CRITERIA from the provided text.

STRICT RULES:
1. Extract every exclusion criterion — do not skip any, including sub-items
   and tables (e.g. drug names with washout periods listed under a criterion).
2. One JSON object per distinct criterion. Never merge two into one object.
3. category must be exactly "EXCLUSION" for every object.
4. text must be verbatim from the source — no paraphrasing.
5. identifier must be the criterion number/letter exactly as written (e.g. "1", "9", "17a").
6. If a criterion contains a list (e.g. prohibited medication classes with
   washout periods), include the full list in the text field — do not drop
   list items even if they span many lines or look like a table.
7. Return ONLY valid JSON. No markdown, no backticks, no commentary.
8. If no exclusion criteria appear in the text, return {"eligibilityCriteria": []}.
"""

CRITERION_SCHEMA = {
    "eligibilityCriteria": [
        {
            "id":          None,
            "name":        None,
            "label":       None,
            "description": None,
            "identifier":  None,
            "category":    None,
            "notes":       None,
            "text":        None,
        }
    ]
}


def _build_eligibility_prompt(category_label: str, context_text: str) -> str:
    schema_json = json.dumps(CRITERION_SCHEMA, indent=2)
    return f"""EXTRACT: {category_label} CRITERIA ONLY

USDM SUB-SCHEMA (fill this array — one object per criterion):
{schema_json}

RETRIEVED DOCUMENT PASSAGES:
\"\"\"
{context_text}
\"\"\"

⚠ COMPLETENESS CHECK before returning:
- Have you captured every numbered criterion?
- Have you captured every lettered sub-item (a, b, c ...) as its own object?
- Have you captured every item in any embedded list or table within a criterion
  (e.g. medication names with washout periods)?
- Is category exactly "{category_label}" on every object?
- Is the text field verbatim from the source?

Return ONLY the populated JSON object — no markdown, no commentary."""


def extract_eligibility_split(
    context_text: str,
    extract_fn,          # extract_usdm_section from llm_caller
    max_tokens: int,
) -> dict:
    """
    Run two LLM calls — INCLUSION and EXCLUSION — and merge into a single
    dict with key "eligibilityCriteria", matching the normal extracted shape
    so the rest of main.py's merge/dedup logic is unchanged.
    """
    all_criteria = []

    for category_label, system_prompt in [
        ("INCLUSION", INCLUSION_SYSTEM),
        ("EXCLUSION", EXCLUSION_SYSTEM),
    ]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": _build_eligibility_prompt(
                category_label, context_text
            )},
        ]

        result = extract_fn(messages, max_tokens=max_tokens)

        if "error" in result:
            print(f"          ⚠  eligibility split: {category_label} call failed — {result['error']}")
            continue

        criteria = result.get("eligibilityCriteria", [])
        if isinstance(criteria, list):
            for item in criteria:
                if isinstance(item, dict):
                    item["category"] = category_label   # enforce, don't trust LLM drift
            all_criteria.extend(criteria)

        print(f"          ✅ {category_label}: {len(criteria)} criteria extracted")

    return {"eligibilityCriteria": all_criteria}