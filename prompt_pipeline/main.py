# prompt_pipeline/main.py
#
# USDM Extraction — single document pass.
#
# Called once per document type (synopsis, protocol, sap, mop, csr)
# by the top-level run.py orchestrator.
#
# Three-state class logic
# ────────────────────────
# For every USDM class the pass checks the current state in master_usdm:
#
#   FULL    — every leaf value is already filled → skip, no LLM call
#   EMPTY   — all leaf values are null/[] → extract and merge normally
#   PARTIAL — some leaves filled, some null → extract, then LLM judge
#             picks the more complete version; winner replaces current value
#
# Returns the updated master_usdm dict.

from __future__ import annotations

import copy
import json
import os
import sys
import time
from typing import Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_pipeline.subsection import (
    get_subschema,
    ALL_USDM_CLASSES,
    USDM_CLASS_PATHS,
    CUSTOM_CLASS_SCHEMAS,
    get_nested_value,
    set_nested_value,
)
from prompt_pipeline.prompt_builder import build_messages
from prompt_pipeline.llm_caller     import extract_usdm_section
from prompt_pipeline.judge          import judge_extraction
from prompt_pipeline.merger         import merge_usdm
from prompt_pipeline.validator      import validate_usdm, print_validation_report
from prompt_pipeline.deduplicator   import deduplicate_usdm

from retrieval.retriever import (
    get_relevant_chunks,
    get_relevant_chunks_from_memory,
    index_chunks_by_id,
    build_context,
)

from preprocessing.extractor_text  import extract_text
from preprocessing.chunk_manager   import chunk_document
from preprocessing.memory_builder  import build_semantic_memory

import config


# ── Classes that get a larger token budget and fewer context chunks ────────────

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


# ── Three-state helpers ────────────────────────────────────────────────────────

def _count_leaves(obj: Any) -> tuple[int, int]:
    """
    Recursively count (filled_leaves, total_leaves).

    A leaf is filled when it is not None and not an empty string.
    An empty list or empty dict counts as one unfilled leaf.
    """
    if obj is None:
        return 0, 1
    if isinstance(obj, bool):
        return 1, 1          # False is a valid fill value
    if isinstance(obj, (int, float)):
        return 1, 1
    if isinstance(obj, str):
        return (1, 1) if obj.strip() else (0, 1)
    if isinstance(obj, list):
        if not obj:
            return 0, 1      # empty list = one unfilled slot
        f, t = 0, 0
        for item in obj:
            lf, lt = _count_leaves(item)
            f += lf
            t += lt
        return f, t
    if isinstance(obj, dict):
        if not obj:
            return 0, 1      # empty dict = one unfilled slot
        f, t = 0, 0
        for v in obj.values():
            lf, lt = _count_leaves(v)
            f += lf
            t += lt
        return f, t
    return 0, 1


def _classify_state(current_value: Any) -> str:
    """
    Return "empty", "partial", or "full" for a class's current value.
    """
    if current_value is None:
        return "empty"
    filled, total = _count_leaves(current_value)
    if total == 0 or filled == 0:
        return "empty"
    if filled >= total:
        return "full"
    return "partial"


def _get_class_current_value(
    usdm_class:  str,
    master_usdm: dict,
) -> Any:
    """
    Retrieve the current value of a USDM class from master_usdm.

    Custom extension classes sit at the top level of master_usdm.
    Base USDM classes are nested — their path is in USDM_CLASS_PATHS.
    """
    if usdm_class in CUSTOM_CLASS_SCHEMAS:
        return master_usdm.get(usdm_class)

    if usdm_class in USDM_CLASS_PATHS:
        return get_nested_value(master_usdm, USDM_CLASS_PATHS[usdm_class])

    return None


def _set_class_value(
    usdm_class:   str,
    master_usdm:  dict,
    winner_dict:  dict,
) -> dict:
    """
    Hard-replace the class's value in master_usdm with the judge winner.

    Unlike merge_usdm (which never overwrites a non-null value), this
    function unconditionally replaces — needed for the PARTIAL path where
    the judge has chosen a superior version.

    winner_dict is subschema-shaped, e.g.:
        {"eligibilityCriteria": [...]}
        {"statisticalAnalysis": {...}}
        {"study": {"versions": [{"studyDesigns": [{"objectives": [...]}]}]}}
    """
    result = copy.deepcopy(master_usdm)

    if usdm_class in CUSTOM_CLASS_SCHEMAS:
        if usdm_class in winner_dict:
            result[usdm_class] = winner_dict[usdm_class]
        return result

    if usdm_class in USDM_CLASS_PATHS:
        path = USDM_CLASS_PATHS[usdm_class]
        winner_value = get_nested_value(winner_dict, path)
        if winner_value is not None:
            set_nested_value(result, path, winner_value)

    return result


def _is_all_null(extracted: dict) -> bool:
    """True if every leaf in extracted is None, [], or {}."""
    def _null(v: Any) -> bool:
        if v is None:
            return True
        if isinstance(v, (list, dict)) and len(v) == 0:
            return True
        if isinstance(v, dict):
            return all(_null(x) for x in v.values())
        if isinstance(v, list):
            return all(_null(x) for x in v)
        return False
    return all(_null(v) for v in extracted.values())


# ── Chunk normalizer ───────────────────────────────────────────────────────────

def _normalize_chunks(raw_chunks: list[dict]) -> list[dict]:
    """Ensure every chunk has chunk_id, section, subsection, text."""
    normalized = []
    for idx, chunk in enumerate(raw_chunks):
        normalized.append({
            "chunk_id":   chunk.get("chunk_id",   f"chunk_{idx + 1:04d}"),
            "section":    chunk.get("section",    "UNKNOWN"),
            "subsection": chunk.get("subsection", ""),
            "text":       chunk.get("text",       ""),
        })
    return normalized


# ── Main pass ──────────────────────────────────────────────────────────────────

def run_document_pass(
    document_path: str,
    doc_type:      str,
    master_usdm:   dict,
    strategy:      str = "recursive",
) -> dict:
    """
    Run a full extraction pass for one document and merge results into
    master_usdm using three-state logic.

    Parameters
    ----------
    document_path : path to the PDF/TXT file
    doc_type      : folder label, e.g. "synopsis", "protocol"
    master_usdm   : accumulated USDM dict from previous passes (may be empty)
    strategy      : chunking strategy (recursive | section | hybrid | ...)

    Returns
    -------
    Updated master_usdm dict.
    """

    # Per-document output directory
    doc_output_dir = os.path.join(config.OUTPUT_DIR, doc_type)
    os.makedirs(doc_output_dir, exist_ok=True)

    print(f"\n{'─'*70}")
    print(f"  DOCUMENT PASS: {doc_type.upper()}")
    print(f"  File   : {document_path}")
    print(f"  Output : {doc_output_dir}")
    print(f"{'─'*70}")

    # ── Stage 1: Extract raw text ──────────────────────────────────────────────
    print("\n📄  Extracting text ...")
    raw_text = extract_text(document_path)
    txt_path = os.path.join(doc_output_dir, "raw_text.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(raw_text)
    print(f"✅  Raw text saved → {txt_path}")

    # ── Stage 2: Chunk ─────────────────────────────────────────────────────────
    print(f"\n🧩  Chunking (strategy={strategy}) ...")
    raw_chunks = chunk_document(raw_text, strategy=strategy)
    chunks     = _normalize_chunks(raw_chunks)

    chunks_path = os.path.join(doc_output_dir, "raw_chunks.json")
    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"✅  {len(chunks)} chunks saved → {chunks_path}")

    chunk_index = index_chunks_by_id(chunks)

    # Section distribution
    from collections import Counter
    section_counts = Counter(c["section"] for c in chunks)
    print("\n  Section breakdown:")
    for sec, cnt in sorted(section_counts.items()):
        print(f"    {cnt:>3}x  {sec}")

    # ── Stage 3: Build semantic memory ─────────────────────────────────────────
    print("\n🧠  Building semantic memory ...")
    memory = build_semantic_memory(chunks)

    if not isinstance(memory, dict):
        print("  ⚠  Memory generation returned non-dict — using empty memory")
        memory = {}

    memory_path = os.path.join(doc_output_dir, "semantic_memory.json")
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    print(f"✅  Memory saved → {memory_path} ({len(memory)} topics)")

    # ── Stage 4: Iterate by USDM class ────────────────────────────────────────
    print(f"\n🔄  Processing {len(ALL_USDM_CLASSES)} USDM classes ...\n")

    stats = {
        "total":    len(ALL_USDM_CLASSES),
        "skipped":  0,   # fully filled from a prior pass
        "empty":    0,   # extracted and merged normally
        "partial":  0,   # extracted + judged
        "no_data":  0,   # no relevant chunks or LLM returned nothing
        "error":    0,   # LLM or parse error
        "via_mem":  0,
        "via_kw":   0,
    }

    debug_dir = os.path.join(doc_output_dir, "debug")

    for i, usdm_class in enumerate(ALL_USDM_CLASSES, 1):

        prefix = f"  [{i:>3}/{stats['total']}] {usdm_class:<40}"

        # ── Always fetch empty subschema first ─────────────────────────────────
        subschema = get_subschema(
            usdm_class,
            template_path=config.TEMPLATE_PATH,
        )

        # ── Classify current state ─────────────────────────────────────────────
        current_value = _get_class_current_value(usdm_class, master_usdm)
        state         = _classify_state(current_value)

        if state == "full":
            print(f"{prefix} ⏭  fully filled — skip")
            stats["skipped"] += 1
            continue

        # ── Retrieve relevant chunks ───────────────────────────────────────────
        adaptive_top_k = (
            config.TOP_K_CHUNKS_LARGE
            if usdm_class in LARGE_CLASSES
            else config.TOP_K_CHUNKS
        )

        relevant, source = get_relevant_chunks_from_memory(
            chunk_index = chunk_index,
            memory      = memory,
            usdm_class  = usdm_class,
            all_chunks  = chunks,
            threshold   = config.RELEVANCE_THRESHOLD,
            top_k       = adaptive_top_k,
        )

        if source == "memory":
            stats["via_mem"] += 1
            src_label = f"🧠 {len(relevant)} chunk(s) via memory"
        elif source == "keyword":
            stats["via_kw"] += 1
            src_label = f"🔑 {len(relevant)} chunk(s) via keyword"
        else:
            print(f"{prefix} ⬜ no relevant chunks — keeping {'empty' if state == 'empty' else 'partial'} schema")
            # Always keep the class present in output
            master_usdm = merge_usdm(master_usdm, subschema)
            master_usdm = deduplicate_usdm(master_usdm)
            stats["no_data"] += 1
            continue

        # ── LLM call ───────────────────────────────────────────────────────────
        context_text = build_context(relevant)
        messages     = build_messages(usdm_class, context_text, subschema)
        max_tokens   = (
            config.LLM_MAX_TOKENS_LARGE
            if usdm_class in LARGE_CLASSES
            else config.LLM_MAX_TOKENS
        )

        extracted = extract_usdm_section(messages, max_tokens=max_tokens)

        # ── Handle LLM error ───────────────────────────────────────────────────
        if "error" in extracted:
            print(f"{prefix} ❌ LLM error — {src_label}")
            os.makedirs(debug_dir, exist_ok=True)
            with open(
                os.path.join(debug_dir, f"{usdm_class}_failed.txt"),
                "w", encoding="utf-8",
            ) as f:
                f.write(extracted.get("raw_response", ""))
            # Keep whatever is already in master_usdm; stamp key if absent
            master_usdm = merge_usdm(master_usdm, subschema)
            stats["error"] += 1
            continue

        # ── Handle all-null LLM response ──────────────────────────────────────
        if _is_all_null(extracted):
            print(f"{prefix} ⬜ LLM returned no data — {src_label}")
            master_usdm = merge_usdm(master_usdm, subschema)
            stats["no_data"] += 1
            continue

        # ── Apply state-specific merge strategy ───────────────────────────────

        if state == "empty":
            master_usdm = merge_usdm(
                master_usdm,
                extracted
            )

            master_usdm = deduplicate_usdm(
                master_usdm
            )
            print(f"{prefix} ✅ extracted (empty→filled) — {src_label}")
            stats["empty"] += 1

        else:   # state == "partial"
            winner = judge_extraction(usdm_class, current_value, extracted)
            master_usdm = _set_class_value(
                usdm_class,
                master_usdm,
                winner
            )

            master_usdm = deduplicate_usdm(
                master_usdm
            )
            print(f"{prefix} ⚖  judged (partial→updated) — {src_label}")
            stats["partial"] += 1

        time.sleep(0.3)

    # ── Validate ──────────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  VALIDATION — {doc_type.upper()} PASS")
    validation = validate_usdm(master_usdm)
    print_validation_report(validation)

    # ── Pass summary ──────────────────────────────────────────────────────────
    print(f"\n  PASS SUMMARY — {doc_type.upper()}")
    print(f"  {'Total classes':25}: {stats['total']}")
    print(f"  {'Skipped (full)':25}: {stats['skipped']}  ⏭")
    print(f"  {'Extracted (empty→full)':25}: {stats['empty']}  ✅")
    print(f"  {'Judged (partial→updated)':25}: {stats['partial']}  ⚖")
    print(f"  {'No data (kept as-is)':25}: {stats['no_data']}  ⬜")
    print(f"  {'Errors':25}: {stats['error']}  ❌")
    print(f"  {'Via memory':25}: {stats['via_mem']}")
    print(f"  {'Via keyword fallback':25}: {stats['via_kw']}")

    return master_usdm