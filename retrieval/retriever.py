# retrieval/retriever.py
#
# Keyword-based chunk retrieval.
# No vector embeddings — scoring is fully deterministic and explainable.
#
# Score for a (chunk, usdm_class) pair is:
#
#   keyword_score  — fraction of the class's keywords present in the chunk
#   section_bonus  — +0.25 if the chunk's section is known to contain this class
#   density_bonus  — rewards chunks where keyword hits are dense relative to length
#                    (capped at 0.15 to prevent very short chunks dominating)
#
# Total score is unbounded above 1.0 when multiple bonuses stack, which is fine
# because we rank, not gate on an absolute value.

from __future__ import annotations

import sys
import os

# Allow running as a standalone script from the project root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, List, Tuple

from retrieval.class_keywords import CLASS_KEYWORDS
from prompt_pipeline.chunker import SECTION_TO_USDM
from config import RELEVANCE_THRESHOLD, TOP_K_CHUNKS


# ── Build inverted section → USDM class map once at import time ───────────────
# USDM_CLASS_TO_SECTIONS[cls] = list of section names that typically hold it.

USDM_CLASS_TO_SECTIONS: Dict[str, List[str]] = {}

for _section, _classes in SECTION_TO_USDM.items():
    for _cls in _classes:
        # Dotted paths like "studyVersion.rationale" → base class "studyVersion"
        _base = _cls.split(".")[0]
        USDM_CLASS_TO_SECTIONS.setdefault(_base, [])
        if _section not in USDM_CLASS_TO_SECTIONS[_base]:
            USDM_CLASS_TO_SECTIONS[_base].append(_section)


# ── Scoring ────────────────────────────────────────────────────────────────────

def _keyword_hits(text_lower: str, keywords: List[str]) -> int:
    """Count how many distinct keywords appear in text_lower."""
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def score_chunk(chunk: Dict, usdm_class: str) -> float:
    """
    Return a relevance score for one (chunk, usdm_class) pair.

    Parameters
    ----------
    chunk       : dict with keys "text" and "section"
    usdm_class  : name of the USDM class being scored against

    Returns
    -------
    float — higher is more relevant; 0.0 means no signal found
    """
    text_lower = chunk.get("text", "").lower()
    section    = chunk.get("section", "").lower()
    keywords   = CLASS_KEYWORDS.get(usdm_class, [])

    # 1. Keyword hit-rate ──────────────────────────────────────────────────────
    if not keywords:
        keyword_score = 0.0
    else:
        hits = _keyword_hits(text_lower, keywords)
        keyword_score = hits / len(keywords)

    # 2. Section bonus ─────────────────────────────────────────────────────────
    mapped_sections = USDM_CLASS_TO_SECTIONS.get(usdm_class, [])
    section_bonus   = 0.25 if section in mapped_sections else 0.0

    # 3. Density bonus ─────────────────────────────────────────────────────────
    # Reward chunks where the same keywords appear densely
    # (hits per 500 characters of text, scaled and capped).
    text_len      = max(len(text_lower), 1)
    hits_for_den  = _keyword_hits(text_lower, keywords)
    density_bonus = min((hits_for_den / (text_len / 500)) * 0.05, 0.15)

    return keyword_score + section_bonus + density_bonus


# ── Retrieval ──────────────────────────────────────────────────────────────────

def get_relevant_chunks(
    chunks: List[Dict],
    usdm_class: str,
    threshold: float = RELEVANCE_THRESHOLD,
    top_k: int = TOP_K_CHUNKS,
) -> List[Dict]:
    """
    Return the top-k most relevant chunks for a given USDM class.

    Chunks are filtered by threshold first, then ranked by score descending.
    Returns an empty list when no chunk clears the threshold — the caller
    should write null for that class rather than making an LLM call.

    Parameters
    ----------
    chunks     : all document chunks produced by the chunker
    usdm_class : USDM class name to retrieve for
    threshold  : minimum score for inclusion
    top_k      : maximum number of chunks to return

    Returns
    -------
    List[Dict] — ordered best-first; may be empty
    """
    scored: List[Tuple[float, Dict]] = []

    for chunk in chunks:
        s = score_chunk(chunk, usdm_class)
        if s >= threshold:
            scored.append((s, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [c for _, c in scored[:top_k]]


# ── Context builder ────────────────────────────────────────────────────────────

def build_context(chunks: List[Dict]) -> str:
    """
    Concatenate retrieved chunks into a single labelled text block
    ready for injection into an LLM prompt.

    Each chunk is wrapped with a section label so the model knows
    which part of the document each passage comes from.
    """
    if not chunks:
        return ""

    parts: List[str] = []
    for i, chunk in enumerate(chunks, 1):
        section = chunk.get("section", "UNKNOWN").upper()
        text    = chunk.get("text", "").strip()
        parts.append(f"--- CHUNK {i} [{section}] ---\n{text}")

    return "\n\n".join(parts)


# ── Debug helper ───────────────────────────────────────────────────────────────

def explain_scores(
    chunks: List[Dict],
    usdm_class: str,
    top_k: int = 10,
) -> None:
    """
    Print a ranked score table for all chunks against one USDM class.
    Useful for tuning thresholds and keyword lists.
    """
    scored = [(score_chunk(c, usdm_class), c) for c in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'='*60}")
    print(f"Scores for USDM class: {usdm_class}")
    print(f"{'='*60}")
    print(f"{'Rank':<5} {'Score':>6}  Section")
    print("-" * 40)
    for rank, (score, chunk) in enumerate(scored[:top_k], 1):
        section = chunk.get("section", "?")[:30]
        print(f"{rank:<5} {score:>6.3f}  {section}")
    print()


# ── Self-test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _sample_chunks = [
        {
            "section": "objectives",
            "text": (
                "Primary Objective: To evaluate the potential efficacy "
                "of psilocybin compared to niacin, assessed as the difference "
                "in MADRS score from Baseline to Day 43."
            ),
        },
        {
            "section": "eligibility",
            "text": (
                "Inclusion Criteria: Patients must be 21–65 years old "
                "with a current depressive episode of at least 60 days. "
                "MADRS score ≥ 28 at Screening."
            ),
        },
        {
            "section": "statistics",
            "text": (
                "Sample size of 100 participants will result in 92% power "
                "for primary Day 43 endpoint and 98% power for key secondary "
                "Day 8 endpoint. MMRM with unstructured covariance matrix."
            ),
        },
    ]

    for _cls in ["objective", "eligibilityCriterion", "statisticalAnalysis"]:
        explain_scores(_sample_chunks, _cls)
        hits = get_relevant_chunks(_sample_chunks, _cls)
        print(f"  → {len(hits)} chunk(s) retrieved\n")