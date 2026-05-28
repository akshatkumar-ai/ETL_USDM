# prompt_pipeline/judge.py
#
# LLM judge for resolving partial USDM class fills.
#
# When a USDM class is partially filled from a prior document pass,
# and a new document pass produces a fresh extraction for that same class,
# this judge asks Claude to evaluate both versions and return the more
# complete one.
#
# The judge does NOT merge — it picks one winner wholesale.
# The caller is responsible for writing the winner back into master_usdm.

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_call import llm_call
from config import ANTHROPIC_MODEL, LLM_TEMPERATURE


# ── System prompt ──────────────────────────────────────────────────────────────

_JUDGE_SYSTEM = """You are a clinical data quality judge specializing in CDISC USDM v4.0.

You will be shown two JSON extractions of the same USDM class from different
clinical trial documents. Your task is to evaluate which extraction is more
complete and accurate, then return it unchanged.

EVALUATION CRITERIA (in order of importance):
1. Completeness — more non-null fields is better; more array items is better.
2. Accuracy     — values must match the source text; no hallucinated data.
3. Detail       — richer description fields are better than sparse ones.
4. Verbatim     — exact criterion text, exact dose strings, exact visit names.

STRICT RULES:
- Return ONLY the winning JSON object. No commentary. No markdown.
- Do NOT merge the two versions. Pick one winner entirely.
- If both are equally complete, return VERSION_B (the newer extraction).
- The output structure must be identical to the input structures.
"""


# ── Judge prompt ───────────────────────────────────────────────────────────────

def _build_judge_prompt(
    usdm_class:   str,
    version_a:    object,  # current partial value from master_usdm
    version_b:    dict,    # new extraction dict in subschema shape
) -> str:
    a_json = json.dumps(version_a, indent=2)
    b_json = json.dumps(version_b,  indent=2)

    return f"""USDM CLASS: {usdm_class}

VERSION_A (existing — from a prior document pass, may be partial):
{a_json}

VERSION_B (new extraction — from the current document pass):
{b_json}

Which version is more complete and accurate for USDM class "{usdm_class}"?

Return ONLY the winning JSON object with no markdown or commentary.
If equally complete, return VERSION_B."""


# ── Main judge call ────────────────────────────────────────────────────────────

def judge_extraction(
    usdm_class:     str,
    existing_value: object,
    new_extraction: dict,
    retry_attempts: int = 1,
) -> dict:
    """
    Ask Claude to pick the more complete extraction between existing and new.

    Parameters
    ----------
    usdm_class      : Name of the USDM class being judged.
    existing_value  : Current value in master_usdm (partial fill).
                      This is the raw value, NOT wrapped in a subschema dict.
    new_extraction  : Full subschema-shaped dict from the new document pass,
                      e.g. {"eligibilityCriteria": [...]} or
                           {"statisticalAnalysis": {...}}.
    retry_attempts  : JSON parse retries on failure.

    Returns
    -------
    dict — the winning subschema-shaped dict, ready to be set into master_usdm.
           Falls back to new_extraction on any error so the pipeline never stalls.
    """
    prompt = _build_judge_prompt(usdm_class, existing_value, new_extraction)

    raw: str | None = None

    for attempt in range(retry_attempts + 1):
        try:
            raw = llm_call(
                prompt=prompt,
                system_prompt=_JUDGE_SYSTEM,
                temperature=LLM_TEMPERATURE,
                max_tokens=8000,
                model=ANTHROPIC_MODEL,
            )

            # Strip markdown fences if present
            cleaned = raw.strip()
            for fence in ("```json", "```"):
                if cleaned.startswith(fence):
                    cleaned = cleaned[len(fence):]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            winner = json.loads(cleaned)

            # Validate winner has the expected top-level key or is a plain value.
            # If the judge returned just the raw value (not wrapped), re-wrap it.
            if isinstance(winner, dict) and usdm_class not in winner:
                # Judge may have returned the inner value directly — wrap it.
                winner = {usdm_class: winner}

            print(f"          ⚖  Judge picked a winner for {usdm_class}")
            return winner

        except Exception as exc:
            print(f"          ⚠  Judge attempt {attempt + 1} failed: {exc}")
            if attempt < retry_attempts:
                prompt += (
                    "\n\nIMPORTANT: Return ONLY raw JSON — no markdown, "
                    "no commentary, no backticks."
                )

    # Fallback: return new extraction so the pipeline never stalls
    print(f"          ⚠  Judge failed — falling back to new extraction")
    return new_extraction