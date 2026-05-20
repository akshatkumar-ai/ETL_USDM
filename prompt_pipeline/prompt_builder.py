# prompt_pipeline/prompt_builder.py
#
# Builds the two-message payload (system + user) sent to Claude for each
# USDM class extraction call.

from __future__ import annotations

import json


# ── Classes where every discrete item MUST become its own array object ─────────
# The LLM is given a named list so the instruction is unambiguous.

MULTI_POINT_CLASSES = {
    "eligibilityCriterion",
    "objective",
    "endpoint",
    "studyArm",
    "studyEpoch",
    "studyElement",
    "encounter",
    "activity",
    "Procedure",
    "scheduleTimeline",
    "timing",
    "studyIntervention",
    "administration",
    "Organisation",
    "studyRole",
    "studySite",
    "BiomedicalConcept",
    "BiomedicalConceptCategory",
    "analysisPopulation",
    "estimand",
    "intercurrentEvent",
    "GovernanceDate",
    "GeographicScope",
    "narrativeContent",
    "studyAmendment",
    "studyChange",
    # custom extension classes that are arrays
    "labValueThresholds",
    "regulatorySubmissions",
    "cellTherapyManufacturing",
    "lymphodepletingChemotherapy",
    "stepUpDosingSchedules",
    "diseaseRiskDefinitions",
    "minimalResidualDiseaseAssessment",
    "biomarkerDefinitions",
    "immuneMediatedToxicityMonitoring",
    "priorTherapyRequirements",
    "stemCellCollectionRequirements",
}


# ── System prompt ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a clinical trial data extraction expert specializing in CDISC USDM v4.0.

Your task is to populate a provided USDM JSON sub-schema using information extracted
verbatim from the clinical trial document passages supplied.

STRICT EXTRACTION RULES:
1.  Extract ONLY information explicitly stated in the provided text.
2.  NEVER invent, infer, or hallucinate values.
3.  Do NOT paraphrase criteria, doses, or outcome text. Copy exact wording.
4.  Leave fields null / empty arrays if the information is absent from the text.
5.  Preserve the provided JSON structure exactly — do not add or remove keys.
6.  Return ONLY valid JSON. No markdown. No backticks. No explanations.
7.  Generate deterministic IDs using the pattern CLASS-NNN (e.g. INC-001, ARM-002).

MULTI-POINT SECTION RULES (critical — violations cause data loss):
8.  For ANY array field: create one separate JSON object per distinct item.
    NEVER merge multiple items into a single object.
    NEVER drop or skip an item because it seems similar to another.
9.  Eligibility criteria specifically:
      - One object per criterion line, sub-clause, or lettered sub-item.
      - category must be exactly "INCLUSION" or "EXCLUSION".
      - text must contain the verbatim criterion text including all notes/sub-clauses.
      - Do NOT combine two criteria into one object under any circumstances.
10. Objectives and endpoints:
      - One object per stated objective or outcome measure.
      - Do not collapse primary, secondary, and exploratory into one object.
11. Arms, epochs, elements, encounters, activities, procedures:
      - One object per named arm / period / visit / procedure.
      - Preserve the sequence and naming exactly as in the source text.

DESCRIPTION FIELD RULES:
12. The "description" field must be populated with a concise factual summary
    drawn directly from the retrieved text. Guidelines:
      - Use complete sentences.
      - Include key facts: drug names, doses, routes, timing, criteria thresholds,
        visit schedules, or other quantitative details relevant to that object.
      - Maximum 200 words. Do not pad or repeat information.
      - If no meaningful description can be formed from the text, set to null.
13. The "label" field should be a short (≤ 10 words) human-readable name for
    the object. It is separate from description — do not duplicate.

FALLBACK:
14. If the passages contain no relevant information for the requested class,
    return the schema unchanged with all values null or empty arrays.
"""


# ── Multi-point instruction block injected into the user prompt ────────────────

def _multipoint_instruction(usdm_class: str) -> str:
    """
    Return an extra instruction block for classes where item-level completeness
    is critical. Empty string for scalar / single-object classes.
    """
    if usdm_class not in MULTI_POINT_CLASSES:
        return ""

    return f"""
⚠ COMPLETENESS REQUIREMENT for {usdm_class}:
This section likely contains MULTIPLE distinct items in the source text.
You MUST create one JSON array object for EVERY item found.
Check your output before returning:
  - Have you captured every numbered / lettered item?
  - Have you captured every sub-clause (a, b, c ...) as its own object where applicable?
  - Have you populated the "description" field for each object?
  - Zero items merged? Zero items dropped?
If you find N items in the text, your output array must contain exactly N objects.
"""


# ── User prompt ────────────────────────────────────────────────────────────────

def build_prompt(
    usdm_class: str,
    context_text: str,
    subschema: dict,
) -> str:
    """
    Build the user-turn extraction prompt.

    Parameters
    ----------
    usdm_class   : The name of the USDM class being populated.
    context_text : Concatenated chunk text retrieved for this class.
    subschema    : The JSON template slice the LLM must fill.

    Returns
    -------
    str — formatted prompt string.
    """
    schema_json       = json.dumps(subschema, indent=2)
    multipoint_block  = _multipoint_instruction(usdm_class)

    return f"""USDM CLASS TO POPULATE: {usdm_class}

USDM SUB-SCHEMA (fill this, preserve all keys):
{schema_json}

RETRIEVED DOCUMENT PASSAGES:
\"\"\"
{context_text}
\"\"\"
{multipoint_block}
TASK:
Populate the USDM sub-schema above using ONLY information present in the
retrieved passages. Follow all rules in the system prompt.

DESCRIPTION FIELD reminder: populate every "description" field with a factual
summary extracted from the passages (max 200 words per object). Do not leave
description null if relevant content exists in the passages.

Return ONLY the populated JSON object — no markdown, no commentary."""


# ── Message payload ────────────────────────────────────────────────────────────

def build_messages(
    usdm_class: str,
    context_text: str,
    subschema: dict,
) -> list[dict]:
    """
    Build a two-element message list compatible with extract_usdm_section().

    Returns
    -------
    [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": <populated prompt>},
    ]
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_prompt(usdm_class, context_text, subschema),
        },
    ]


# ── Self-test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _sample_subschema = {
        "eligibilityCriteria": [
            {
                "id": None,
                "name": None,
                "label": None,
                "description": None,
                "identifier": None,
                "category": None,
                "text": None,
                "notes": None,
            }
        ]
    }

    _sample_context = (
        "--- CHUNK 1 [ELIGIBILITY] ---\n"
        "Inclusion Criteria:\n"
        "1. Are 21 to 65 years old at the time of written informed consent.\n"
        "2. Meet DSM-5 criteria for a diagnosis of major depressive disorder "
        "with a current episode of at least 60 days duration.\n"
        "3. MADRS total score >= 28 at Screening on both central rater and "
        "computer assessments.\n"
        "\n"
        "Exclusion Criteria:\n"
        "1. Women who are pregnant as indicated by a positive urine pregnancy test.\n"
        "2. Currently receiving ECT or TMS. Note: Previous ECT/TMS allowed if "
        "last treatment >= 90 days before Screening."
    )

    msgs = build_messages("eligibilityCriterion", _sample_context, _sample_subschema)
    print(msgs[1]["content"])