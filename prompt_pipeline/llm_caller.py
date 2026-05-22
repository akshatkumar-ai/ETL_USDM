# prompt_pipeline/llm_caller.py

from __future__ import annotations

import json
import re
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from utils.llm_call import llm_call
from config import (
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    ANTHROPIC_MODEL,
)


# ─────────────────────────────────────────────────────────────
# JSON CLEANING
# ─────────────────────────────────────────────────────────────

def _clean_json(text: str) -> str:

    text = text.strip()

    # Remove markdown fences
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


# ─────────────────────────────────────────────────────────────
# SAFE JSON PARSER
# ─────────────────────────────────────────────────────────────

def _safe_json_loads(text: str):

    cleaned = _clean_json(text)

    # ---------------------------------------------------------
    # Attempt 1
    # ---------------------------------------------------------

    try:
        return json.loads(cleaned)

    except Exception:
        pass

    # ---------------------------------------------------------
    # Attempt 2 — extract largest JSON object
    # ---------------------------------------------------------

    start = cleaned.find("{")
    end   = cleaned.rfind("}")

    if start != -1 and end != -1:

        candidate = cleaned[start:end + 1]

        try:
            return json.loads(candidate)

        except Exception:
            pass

    # ---------------------------------------------------------
    # Attempt 3 — common truncation repair
    # ---------------------------------------------------------

    repaired = cleaned

    # remove trailing commas
    repaired = re.sub(r",\s*}", "}", repaired)
    repaired = re.sub(r",\s*]", "]", repaired)

    # close missing braces
    open_curly  = repaired.count("{")
    close_curly = repaired.count("}")

    if open_curly > close_curly:
        repaired += "}" * (open_curly - close_curly)

    open_square  = repaired.count("[")
    close_square = repaired.count("]")

    if open_square > close_square:
        repaired += "]" * (open_square - close_square)

    try:
        return json.loads(repaired)

    except Exception as exc:

        raise json.JSONDecodeError(
            msg=str(exc),
            doc=cleaned,
            pos=0
        )


# ─────────────────────────────────────────────────────────────
# MAIN EXTRACTION
# ─────────────────────────────────────────────────────────────

def extract_usdm_section(
    messages: list[dict],
    retry_attempts: int = 1,
    max_tokens: int = 4000,
) -> dict:

    system_prompt = messages[0].get("content", "")
    user_prompt   = messages[1].get("content", "")

    raw_response: str | None = None

    if max_tokens is None:
        max_tokens = LLM_MAX_TOKENS

    for attempt in range(retry_attempts + 1):

        try:

            raw_response = llm_call(

                prompt=user_prompt,

                system_prompt=system_prompt,

                temperature=LLM_TEMPERATURE,

                max_tokens=max_tokens,

                model_id=ANTHROPIC_MODEL,
            )

            parsed = _safe_json_loads(raw_response)

            return parsed

        except json.JSONDecodeError as exc:

            print(
                f"\n  ⚠ JSON parse failed "
                f"(attempt {attempt + 1}/{retry_attempts + 1})"
            )

            print(f"    Error: {exc}")

            # Save raw response for debugging
            try:

                os.makedirs("debug", exist_ok=True)

                with open(
                    f"debug/failed_response_attempt_{attempt + 1}.txt",
                    "w",
                    encoding="utf-8"
                ) as f:

                    f.write(raw_response or "")

            except Exception:
                pass

            if attempt < retry_attempts:

                user_prompt += """

IMPORTANT:
- Return STRICT valid JSON
- Return ONLY JSON
- No markdown
- No explanations
- Escape all quotes correctly
- Never truncate output
"""

            else:

                return {
                    "error": str(exc),
                    "raw_response": raw_response,
                }

        except Exception as exc:

            print(
                f"\n  ✗ LLM call failed "
                f"(attempt {attempt + 1}): {exc}"
            )

            if attempt >= retry_attempts:

                return {
                    "error": str(exc),
                    "raw_response": raw_response,
                }