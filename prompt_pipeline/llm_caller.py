# prompt_pipeline/llm_caller.py
#
# Thin wrapper around utils.llm_call.
# Handles JSON cleaning, parsing, and one automatic retry on parse failure.

from __future__ import annotations

import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.llm_call import llm_call
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE, ANTHROPIC_MODEL


# ── JSON cleaning ──────────────────────────────────────────────────────────────

def _clean_json(text: str) -> str:
    """
    Strip markdown fences and surrounding whitespace that models
    sometimes emit even when told not to.
    """
    text = text.strip()
    for fence in ("```json", "```"):
        if text.startswith(fence):
            text = text[len(fence):]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


# ── Main extraction call ───────────────────────────────────────────────────────

def extract_usdm_section(
    messages: list[dict],
    retry_attempts: int = 1,
    max_tokens: int = LLM_MAX_TOKENS,
) -> dict:
    """
    Send a prepared message payload to Claude and return parsed JSON.

    Parameters
    ----------
    messages       : list with two dicts — system message (index 0) and
                     user message (index 1), following the build_messages format.
    retry_attempts : how many times to retry on JSON parse failure before
                     returning an error dict.
    max_tokens     : override the default token budget for large classes.

    Returns
    -------
    dict — extracted JSON, or {"error": ..., "raw_response": ...} on failure.
    """

    # build_messages returns [{"role": "system", ...}, {"role": "user", ...}]
    system_prompt = messages[0].get("content", "")
    user_prompt   = messages[1].get("content", "")

    raw_response: str | None = None

    for attempt in range(retry_attempts + 1):
        try:
            raw_response = llm_call(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=LLM_TEMPERATURE,
                max_tokens=max_tokens,
                model=ANTHROPIC_MODEL,
            )

            cleaned = _clean_json(raw_response)
            return json.loads(cleaned)

        except json.JSONDecodeError as exc:
            print(f"\n  ⚠ JSON parse failed (attempt {attempt + 1}/{retry_attempts + 1})")
            print(f"    Error: {exc}")

            if attempt < retry_attempts:
                # Append a stricter instruction to the user prompt for the retry.
                user_prompt += (
                    "\n\nIMPORTANT: Your previous response could not be parsed as JSON. "
                    "Return ONLY raw JSON — no markdown, no backticks, no explanations."
                )
            else:
                return {
                    "error": str(exc),
                    "raw_response": raw_response,
                }

        except Exception as exc:
            print(f"\n  ✗ LLM call failed (attempt {attempt + 1}): {exc}")
            if attempt >= retry_attempts:
                return {
                    "error": str(exc),
                    "raw_response": raw_response,
                }