# retrieval/retriever.py
#
# Hybrid retrieval system for USDM extraction.
#
# FEATURES:
# - deterministic keyword scoring
# - semantic-memory retrieval
# - keyword fallback retrieval
# - context-size control
# - duplicate suppression
# - adaptive retrieval for large classes
#
# Optimized for:
# - stable JSON extraction
# - reduced prompt explosion
# - large protocol documents
# - Bedrock Claude Sonnet pipelines

from __future__ import annotations

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

from typing import Dict, List, Tuple

from retrieval.class_keywords import CLASS_KEYWORDS
from prompt_pipeline.chunker import SECTION_TO_USDM
from config import (
    RELEVANCE_THRESHOLD,
    TOP_K_CHUNKS,
)

# =============================================================================
# CONFIG
# =============================================================================

MAX_CHARS_PER_CHUNK = 2500

LARGE_CLASSES = {

    "eligibilityCriterion",

    "activity",

    "encounter",

    "objective",

    "estimand",

    "analysisPopulation",

    "studyCell",

    "studyElement",

    "studyEpoch",

    "scheduleTimeline",
}

# =============================================================================
# SECTION → CLASS MAP
# =============================================================================

USDM_CLASS_TO_SECTIONS: Dict[str, List[str]] = {}

for _section, _classes in SECTION_TO_USDM.items():

    for _cls in _classes:

        _base = _cls.split(".")[0]

        USDM_CLASS_TO_SECTIONS.setdefault(
            _base,
            []
        )

        if _section not in USDM_CLASS_TO_SECTIONS[_base]:

            USDM_CLASS_TO_SECTIONS[_base].append(
                _section
            )

# =============================================================================
# SCORING
# =============================================================================

def _keyword_hits(
    text_lower: str,
    keywords: List[str]
) -> int:

    return sum(
        1
        for kw in keywords
        if kw.lower() in text_lower
    )


def score_chunk(
    chunk: Dict,
    usdm_class: str
) -> float:
    """
    Score one chunk against one USDM class.
    """

    text_lower = chunk.get(
        "text",
        ""
    ).lower()

    section = chunk.get(
        "section",
        ""
    ).lower()

    keywords = CLASS_KEYWORDS.get(
        usdm_class,
        []
    )

    # -------------------------------------------------------------------------
    # Keyword score
    # -------------------------------------------------------------------------

    if not keywords:

        keyword_score = 0.0

    else:

        hits = _keyword_hits(
            text_lower,
            keywords
        )

        keyword_score = hits / len(keywords)

    # -------------------------------------------------------------------------
    # Section bonus
    # -------------------------------------------------------------------------

    mapped_sections = USDM_CLASS_TO_SECTIONS.get(
        usdm_class,
        []
    )

    section_bonus = (
        0.35
        if section in mapped_sections
        else 0.0
    )

    # -------------------------------------------------------------------------
    # Density bonus
    # -------------------------------------------------------------------------

    text_len = max(
        len(text_lower),
        1
    )

    hits_for_den = _keyword_hits(
        text_lower,
        keywords
    )

    density_bonus = min(
        (
            hits_for_den
            / (text_len / 500)
        ) * 0.05,
        0.15
    )

    return (
        keyword_score
        + section_bonus
        + density_bonus
    )

# =============================================================================
# KEYWORD RETRIEVAL
# =============================================================================

def get_relevant_chunks(
    chunks: List[Dict],
    usdm_class: str,
    threshold: float = RELEVANCE_THRESHOLD,
    top_k: int = TOP_K_CHUNKS,
) -> List[Dict]:
    """
    Deterministic keyword retrieval.
    """

    scored: List[Tuple[float, Dict]] = []

    for chunk in chunks:

        s = score_chunk(
            chunk,
            usdm_class
        )

        if s >= threshold:

            scored.append(
                (s, chunk)
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        c
        for _, c in scored[:top_k]
    ]

# =============================================================================
# MEMORY MAPPING
# =============================================================================

USDM_CLASS_TO_MEMORY_KEYS: Dict[str, List[str]] = {

    # -------------------------------------------------------------------------
    # Study identity
    # -------------------------------------------------------------------------

    "study":                        ["study_overview", "organizations"],
    "studyVersion":                 ["study_overview"],
    "studyTitle":                   ["study_overview"],
    "studyIdentifier":              ["organizations"],
    "referenceIdentifier":          ["organizations"],
    "Organization":                 ["organizations"],
    "address":                      ["organizations"],
    "studyRole":                    ["organizations"],
    "GovernanceDate":               ["organizations"],
    "GeographicScope":              ["organizations"],

    # -------------------------------------------------------------------------
    # Design
    # -------------------------------------------------------------------------

    "studyDesign":                  ["study_design"],
    "interventionalStudyDesign":    ["study_design"],
    "studyArm":                     ["study_design", "interventions"],
    "studyEpoch":                   ["study_design"],
    "studyElement":                 ["study_design"],
    "studyCell":                    ["study_design"],
    "scheduleTimeline":             ["study_design"],
    "timing":                       ["study_design"],
    "encounter":                    ["study_design"],
    "scheduleTimelineExit":         ["study_design"],

    # -------------------------------------------------------------------------
    # Interventions
    # -------------------------------------------------------------------------

    "studyIntervention":            ["interventions"],
    "administrableProduct":         ["interventions"],
    "administration":               ["interventions"],
    "substance":                    ["interventions"],
    "strength":                     ["interventions"],
    "ingredient":                   ["interventions"],

    # -------------------------------------------------------------------------
    # Objectives / endpoints
    # -------------------------------------------------------------------------

    "objective":                    ["objectives"],
    "endpoint":                     ["endpoints"],
    "estimand":                     ["statistics", "objectives"],
    "intercurrentEvent":            ["statistics"],
    "analysisPopulation":           ["statistics"],

    # -------------------------------------------------------------------------
    # Eligibility
    # -------------------------------------------------------------------------

    "eligibilityCriterion":         ["eligibility"],
    "studyDesignPopulation":        ["eligibility", "study_design"],
    "populationDefinition":         ["eligibility", "study_design"],
    "indication":                   ["study_overview", "eligibility"],

    # -------------------------------------------------------------------------
    # Assessments / safety
    # -------------------------------------------------------------------------

    "activity":                     ["assessments", "safety"],
    "Procedure":                    ["assessments", "safety"],
    "BiomedicalConcept":            ["assessments", "endpoints"],
    "BiomedicalConceptCategory":    ["assessments"],
    "BiospecimenRetention":         ["safety"],

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    "statisticalAnalysis":          ["statistics"],
    "randomization":                ["study_design", "statistics"],

    # -------------------------------------------------------------------------
    # Narrative
    # -------------------------------------------------------------------------

    "narrativeContent":             ["study_overview"],
    "DocumentContentReference":     ["study_overview"],
}

# =============================================================================
# INDEXING
# =============================================================================

def index_chunks_by_id(
    chunks: List[Dict]
) -> Dict[str, Dict]:
    """
    Build chunk_id → chunk map.
    """

    return {

        c["chunk_id"]: c

        for c in chunks

        if "chunk_id" in c
    }

# =============================================================================
# MEMORY RETRIEVAL
# =============================================================================

def get_relevant_chunks_from_memory(

    chunk_index: Dict[str, Dict],

    memory: Dict[str, Dict],

    usdm_class: str,

    all_chunks: List[Dict],

    threshold: float = RELEVANCE_THRESHOLD,

    top_k: int = TOP_K_CHUNKS,

) -> Tuple[List[Dict], str]:
    """
    Primary retrieval:
        semantic memory

    Fallback:
        keyword scoring
    """

    # -------------------------------------------------------------------------
    # Reduce retrieval for huge extraction classes
    # -------------------------------------------------------------------------

    memory_keys = USDM_CLASS_TO_MEMORY_KEYS.get(
        usdm_class,
        []
    )

    # -------------------------------------------------------------------------
    # MEMORY RETRIEVAL
    # -------------------------------------------------------------------------

    if memory_keys:

        seen_ids = set()

        seen_texts = set()

        retrieved = []

        for key in memory_keys:

            entry = memory.get(key)

            if not entry:
                continue

            for chunk_id in entry.get(
                "chunk_ids",
                []
            ):

                if chunk_id in seen_ids:
                    continue

                seen_ids.add(chunk_id)

                chunk = chunk_index.get(
                    chunk_id
                )

                if not chunk:
                    continue

                # -------------------------------------------------------------
                # Deduplicate overlapping chunks
                # -------------------------------------------------------------

                text_sig = chunk.get(
                    "text",
                    ""
                )[:500]

                if text_sig in seen_texts:
                    continue

                seen_texts.add(text_sig)

                retrieved.append(chunk)

        if retrieved:

            return (
                retrieved[:top_k],
                "memory"
            )

    # -------------------------------------------------------------------------
    # KEYWORD FALLBACK
    # -------------------------------------------------------------------------

    keyword_hits = get_relevant_chunks(

        all_chunks,

        usdm_class,

        threshold=threshold,

        top_k=top_k,
    )

    if keyword_hits:

        return (
            keyword_hits,
            "keyword"
        )

    return [], "none"

# =============================================================================
# CONTEXT BUILDER
# =============================================================================

def build_context(
    chunks: List[Dict]
) -> str:
    """
    Build bounded prompt context.
    """

    if not chunks:
        return ""

    parts = []

    total_chars = 0

    for i, chunk in enumerate(chunks, 1):

        section = chunk.get(
            "section",
            "UNKNOWN"
        ).upper()

        text = chunk.get(
            "text",
            ""
        ).strip()

        # ---------------------------------------------------------------------
        # Prevent prompt explosion
        # ---------------------------------------------------------------------

        if len(text) > MAX_CHARS_PER_CHUNK:

            text = (
                text[:MAX_CHARS_PER_CHUNK]
                + "\n...[TRUNCATED]"
            )

        total_chars += len(text)

        parts.append(
            f"--- CHUNK {i} [{section}] ---\n{text}"
        )

    print(
        f"          📏 Context size: "
        f"{total_chars:,} chars"
    )

    return "\n\n".join(parts)

# =============================================================================
# DEBUGGING
# =============================================================================

def explain_scores(
    chunks: List[Dict],
    usdm_class: str,
    top_k: int = 10,
) -> None:
    """
    Print ranked chunk scores.
    """

    scored = [

        (
            score_chunk(c, usdm_class),
            c
        )

        for c in chunks
    ]

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    print(f"\n{'='*60}")
    print(f"Scores for: {usdm_class}")
    print(f"{'='*60}")

    print(
        f"{'Rank':<5} "
        f"{'Score':>6}  "
        f"Section"
    )

    print("-" * 40)

    for rank, (score, chunk) in enumerate(
        scored[:top_k],
        1
    ):

        section = chunk.get(
            "section",
            "?"
        )[:30]

        print(
            f"{rank:<5} "
            f"{score:>6.3f}  "
            f"{section}"
        )

    print()

# =============================================================================
# SELF TEST
# =============================================================================

if __name__ == "__main__":

    _sample_chunks = [

        {
            "section": "objectives",
            "text": (
                "Primary Objective: "
                "Evaluate efficacy."
            ),
        },

        {
            "section": "eligibility",
            "text": (
                "Subjects must be "
                "18-65 years old."
            ),
        },
    ]

    for _cls in [

        "objective",

        "eligibilityCriterion",
    ]:

        explain_scores(
            _sample_chunks,
            _cls
        )

        hits = get_relevant_chunks(
            _sample_chunks,
            _cls
        )

        print(
            f"→ {len(hits)} chunk(s)\n"
        )