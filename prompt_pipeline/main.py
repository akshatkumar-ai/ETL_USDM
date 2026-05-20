# prompt_pipeline/main.py
#
# USDM Extraction Pipeline — class-driven iteration
#
# Flow:
#   1. Extract raw text from PDF
#   2. Chunk document into labelled sections
#   3. For every USDM class (base + custom extension):
#        a. Score all chunks against this class using keyword retriever
#        b. If no chunk clears the relevance threshold → mark class null, skip
#        c. Concatenate top-k chunks into one context string
#        d. Fetch the class sub-schema
#        e. Send ONE LLM call: (system + context + sub-schema) → filled JSON
#        f. Merge result into master USDM
#   4. Validate final structure
#   5. Save to disk

from __future__ import annotations

import json
import os
import sys
import time

# ── Project root on path so sibling packages resolve ──────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_pipeline.extractor_text   import extract_text
from chunker          import chunk_document
from subsection       import get_subschema, ALL_USDM_CLASSES
from prompt_builder   import build_messages
from llm_caller       import extract_usdm_section
from prompt_pipeline.merger  import merge_usdm 
from prompt_pipeline.validator        import validate_usdm, print_validation_report

from retrieval.retriever import get_relevant_chunks, build_context
from config import (
    TEMPLATE_PATH,
    OUTPUT_DIR,
    OUTPUT_FILE,
    RELEVANCE_THRESHOLD,
    TOP_K_CHUNKS,
)


# ── Configuration ──────────────────────────────────────────────────────────────

PDF_PATH = "sample_protocol.pdf"     # ← change to your PDF path


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_null_entry(usdm_class: str) -> dict:
    """
    Return a minimal dict that records this class as null in the master USDM.
    The merger ignores null values, so this is only used for the run report.
    """
    return {usdm_class: None}


def _is_all_null(extracted: dict) -> bool:
    """
    Return True if every value in the extracted dict is None, [], or {}.
    Used to detect when the LLM found nothing meaningful in the context.
    """
    def _null(v) -> bool:
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


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(
    chunks_path: str = "raw_chunks.json"
) -> dict:
    print("\n" + "=" * 70)
    print("  USDM EXTRACTION PIPELINE  —  class-driven")
    print("=" * 70)

    # STEP 1 — Load precomputed chunks
    print("\n📦  Loading precomputed chunks ...")

    with open(chunks_path, "r", encoding="utf-8") as f:
        raw_chunks = json.load(f)

    # Normalize chunk schema
    chunks = [
        {
            "section": chunk.get("header", "UNKNOWN").lower(),
            "text": chunk.get("text", "")
        }
        for chunk in raw_chunks
    ]

    print(f"✅  {len(chunks)} chunks loaded")

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 2 — Iterate by USDM class
    # ──────────────────────────────────────────────────────────────────────────
    print(f"\n🔄  Processing {len(ALL_USDM_CLASSES)} USDM classes ...\n")
 
    master_usdm: dict = {}
 
    stats = {
        "total":     len(ALL_USDM_CLASSES),
        "extracted": 0,
        "null":      0,
        "error":     0,
        "empty_llm": 0,
    }
 
    null_classes:    list[str] = []
    error_classes:   list[str] = []
    success_classes: list[str] = []
 
    for i, usdm_class in enumerate(ALL_USDM_CLASSES, 1):
 
        print(f"  [{i:>3}/{stats['total']}] {usdm_class}")
 
        # ── 2a: Fetch sub-schema for this class (needed for both filled and
        #        empty paths — empty schema is merged so the key always appears
        #        in the final output even when no source text is found) ─────────
        subschema = get_subschema(usdm_class, template_path=TEMPLATE_PATH)
 
        # ── 2b: Retrieve relevant chunks ──────────────────────────────────────
        relevant = get_relevant_chunks(
            chunks,
            usdm_class,
            threshold=RELEVANCE_THRESHOLD,
            top_k=TOP_K_CHUNKS,
        )
 
        if not relevant:
            print(f"          ⬜ no relevant chunks → keeping empty schema")
            # Merge the empty subschema so the class key exists in the output
            # with its full null-valued structure (merger rule: null never
            # overwrites a value already set, so this is always safe).
            master_usdm = merge_usdm(master_usdm, subschema)
            null_classes.append(usdm_class)
            stats["null"] += 1
            continue
 
        print(f"          📎 {len(relevant)} chunk(s) retrieved")
 
        # ── 2c: Build context string ──────────────────────────────────────────
        context_text = build_context(relevant)
 
        # ── 2d: Build prompt ──────────────────────────────────────────────────
        messages = build_messages(usdm_class, context_text, subschema)
 
        # ── 2e: LLM call ──────────────────────────────────────────────────────
        extracted = extract_usdm_section(messages)
 
        # ── 2f: Handle LLM errors ─────────────────────────────────────────────
        if "error" in extracted:
            print(f"          ❌ error: {str(extracted['error'])[:80]}")
            error_classes.append(usdm_class)
            stats["error"] += 1
            continue
 
        # ── 2g: Detect all-null LLM response ──────────────────────────────────
        if _is_all_null(extracted):
            print(f"          ⬜ LLM returned no data → keeping empty schema")
            # Still merge the empty subschema so the class key is present
            master_usdm = merge_usdm(master_usdm, subschema)
            null_classes.append(usdm_class)
            stats["empty_llm"] += 1
            continue
 
        # ── 2h: Merge into master USDM ────────────────────────────────────────
        master_usdm = merge_usdm(master_usdm, extracted)
        success_classes.append(usdm_class)
        stats["extracted"] += 1
        print(f"          ✅ merged")
 
        # Brief pause to stay within API rate limits
        time.sleep(0.3)

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 3 — Validate
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("🔎  VALIDATING FINAL USDM")

    validation = validate_usdm(master_usdm)
    print_validation_report(validation)

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 4 — Save output
    # ──────────────────────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(master_usdm, f, indent=2, ensure_ascii=False)

    print(f"\n💾  USDM saved → {OUTPUT_FILE}")

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 5 — Run summary
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  RUN SUMMARY")
    print("=" * 70)
    print(f"  Total classes  : {stats['total']}")
    print(f"  Extracted      : {stats['extracted']}  ✅")
    print(f"  Null (no data) : {stats['null'] + stats['empty_llm']}  ⬜")
    print(f"  Errors         : {stats['error']}  ❌")

    if null_classes:
        print(f"\n  Classes with no relevant content:")
        for cls in null_classes:
            print(f"    ⬜ {cls}")

    if error_classes:
        print(f"\n  Classes that errored:")
        for cls in error_classes:
            print(f"    ❌ {cls}")

    print("\n✅  PIPELINE COMPLETE\n")

    return master_usdm


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract USDM JSON from a clinical protocol PDF."
    )
    parser.add_argument(
        "chunks",
        nargs="?",
        default="raw_chunks.json",
        help="Path to the chunks file (default: %(default)s)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=RELEVANCE_THRESHOLD,
        help="Minimum relevance score for chunk inclusion (default: %(default)s)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K_CHUNKS,
        help="Max chunks per USDM class (default: %(default)s)",
    )

    args = parser.parse_args()

    # Allow CLI overrides without touching config.py
    import config as _cfg
    _cfg.RELEVANCE_THRESHOLD = args.threshold
    _cfg.TOP_K_CHUNKS        = args.top_k

    run_pipeline(chunks_path=args.chunks)