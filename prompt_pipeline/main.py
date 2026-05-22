# prompt_pipeline/main.py
#
# USDM Extraction Pipeline — class-driven iteration
#
# Input : raw_chunking.json      — pre-chunked document (required)
#          semantic_memory.json   — topic → chunk_ids map (optional, improves precision)
# Output: output/final_usdm.json
#
# Expected shape of raw_chunking.json:
#   A JSON array of chunk objects, each with at minimum:
#     { "chunk_id": "chunk_0001", "section": "...", "text": "..." }
#
# Expected shape of semantic_memory.json:
#   {
#     "<topic_key>": {
#       "summary":   "<string>",
#       "chunk_ids": ["chunk_0001", "chunk_0005", ...]
#     }, ...
#   }
#
# Flow:
#   1. Load chunks → build { chunk_id → chunk } index
#   2. Load semantic memory (optional; soft-fails to keyword-only mode)
#   3. For every USDM class (base + custom extension):
#        a. Fetch empty sub-schema (always — ensures key present even if no data)
#        b. Retrieve chunks:
#             PRIMARY   — look up memory keys for this class → resolve chunk IDs
#             FALLBACK  — keyword score all chunks if memory has no mapping/hits
#             NONE      — merge empty schema and continue
#        c. Build concatenated context string from retrieved chunks
#        d. Send ONE LLM call → filled JSON
#        e. If LLM all-null → merge empty schema; else merge filled result
#   4. Validate → save

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

# ── Project root on path so sibling packages resolve ──────────────────────────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt_pipeline.subsection import (
    get_subschema,
    ALL_USDM_CLASSES,
)
from prompt_pipeline.prompt_builder   import build_messages
from prompt_pipeline.llm_caller       import extract_usdm_section
from prompt_pipeline.merger           import merge_usdm
from prompt_pipeline.validator        import validate_usdm, print_validation_report

from retrieval.retriever import (
    get_relevant_chunks,
    get_relevant_chunks_from_memory,
    index_chunks_by_id,
    build_context,
)
import config

# ── Large extraction classes ─────────────────────────────────────────────

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

# Optional:
# Temporarily skip problematic huge classes
# to allow stable end-to-end pipeline execution.

SKIP_CLASSES = {

    # Uncomment while debugging huge generations

    "estimand",
    "activity",
    "encounter",
    # "eligibilityCriterion",
}
SPLIT_CLASSES = {
    "endpoint",
    "objective"
}

# ── Default paths ──────────────────────────────────────────────────────────────

DEFAULT_CHUNKS_PATH = "raw_chunking.json"
DEFAULT_MEMORY_PATH = "semantic_memory.json"   # optional — pass "" to disable


# ── Memory loader ──────────────────────────────────────────────────────────────

def load_memory(path: str) -> dict:
    """
    Load semantic_memory.json.

    Expected shape:
      {
        "<topic_key>": {
          "summary":   "<string>",
          "chunk_ids": ["chunk_0001", ...]
        },
        ...
      }

    Returns an empty dict if path is empty string (memory disabled)
    or the file does not exist (soft failure with a warning).
    """
    if not path:
        return {}

    if not os.path.exists(path):
        print(f"  ⚠  Memory file not found: {path} — running keyword-only mode")
        return {}

    with open(path, "r", encoding="utf-8") as f:
        memory = json.load(f)

    if not isinstance(memory, dict):
        print(f"  ⚠  Memory file is not a JSON object — running keyword-only mode")
        return {}

    # Validate each entry has expected keys; drop malformed ones with a warning
    clean: dict = {}
    for key, entry in memory.items():
        if not isinstance(entry, dict):
            print(f"  ⚠  Memory entry '{key}' is not a dict — skipped")
            continue
        if "chunk_ids" not in entry:
            print(f"  ⚠  Memory entry '{key}' missing 'chunk_ids' — skipped")
            continue
        clean[key] = entry

    print(f"✅  Memory loaded: {len(clean)} topic entries")
    return clean


# ── Chunk loader ───────────────────────────────────────────────────────────────

def load_chunks(path: str) -> list[dict]:
    """
    Load and validate a pre-chunked JSON file.

    Accepts two shapes:
      - A bare JSON array:  [ {chunk}, {chunk}, ... ]
      - A wrapped object:   { "chunks": [ {chunk}, ... ] }
        (any other top-level key whose value is a list also works)

    Each chunk must have at minimum a "text" key.
    A missing "section" key is backfilled with "unknown".

    Raises
    ------
    ValueError  if the file cannot be parsed as a list of chunk dicts.
    FileNotFoundError if the path does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Chunks file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw: Any = json.load(f)

    # Unwrap if the file is a dict with one list-valued key
    if isinstance(raw, dict):
        list_keys = [k for k, v in raw.items() if isinstance(v, list)]
        if not list_keys:
            raise ValueError(
                f"Expected a JSON array or a dict containing a list, got dict "
                f"with keys: {list(raw.keys())}"
            )
        # Prefer "chunks" key; fall back to first list key found
        key = "chunks" if "chunks" in list_keys else list_keys[0]
        raw = raw[key]
        print(f"  ℹ  Unwrapped chunks from key '{key}'")

    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array of chunks, got {type(raw).__name__}")

    # Validate + normalise
    chunks: list[dict] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"Chunk at index {i} is not a dict (got {type(item).__name__})")
        if "text" not in item:
            raise ValueError(f"Chunk at index {i} is missing required key 'text'")
        # Backfill missing section so downstream scorer always has one
        if "section" not in item or not item["section"]:
            item = {**item, "section": "unknown"}
        chunks.append(item)

    return chunks


# ── Helpers ────────────────────────────────────────────────────────────────────

def _is_all_null(extracted: dict) -> bool:
    """
    Return True if every leaf value in the extracted dict is None, [], or {}.
    Used to detect when the LLM found nothing meaningful in the context.
    """
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


# ── Pipeline ───────────────────────────────────────────────────────────────────

def run_pipeline(
    chunks_path: str = DEFAULT_CHUNKS_PATH,
    memory_path: str = DEFAULT_MEMORY_PATH,
) -> dict:

    print("\n" + "=" * 70)
    print("  USDM EXTRACTION PIPELINE  —  class-driven")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 1 — Load pre-chunked JSON + semantic memory
    # ──────────────────────────────────────────────────────────────────────────
    print(f"\n📂  Loading chunks from: {chunks_path}")
    chunks = load_chunks(chunks_path)
    print(f"✅  {len(chunks)} chunks loaded")

    # Build { chunk_id → chunk } index for O(1) memory-based lookup
    chunk_index = index_chunks_by_id(chunks)
    print(f"    {len(chunk_index)} chunks indexed by ID")

    print(f"\n🧠  Loading semantic memory from: {memory_path}")
    memory = load_memory(memory_path)
    if memory:
        print(f"    Memory topics loaded: {len(memory)}")
    else:
        print(f"    No memory — will use keyword-only retrieval")

    # Quick peek at section distribution
    from collections import Counter
    section_counts = Counter(c.get("section", "unknown") for c in chunks)
    print("\n  Section breakdown:")
    for section, count in sorted(section_counts.items()):
        print(f"    {count:>3}x  {section}")

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 2 — Iterate by USDM class
    # ──────────────────────────────────────────────────────────────────────────
    print(f"\n🔄  Processing {len(ALL_USDM_CLASSES)} USDM classes ...\n")

    master_usdm: dict = {}

    stats = {
        "total":        len(ALL_USDM_CLASSES),
        "extracted":    0,
        "null":         0,
        "error":        0,
        "empty_llm":    0,
        "via_memory":   0,
        "via_keyword":  0,
    }

    null_classes:    list[str] = []
    error_classes:   list[str] = []
    success_classes: list[str] = []

    for i, usdm_class in enumerate(ALL_USDM_CLASSES, 1):

        print(f"  [{i:>3}/{stats['total']}] {usdm_class}")

        # ── 2a: Fetch sub-schema for this class (needed for both filled and
        #        empty paths — empty schema is merged so the key always appears
        #        in the final output even when no source text is found) ─────────
        subschema = get_subschema(usdm_class, template_path=config.TEMPLATE_PATH)

        # ── 2b: Retrieve relevant chunks (memory-first, keyword fallback) ────────
        # ── Skip extremely large classes if configured ─────────────────────────

        if usdm_class in SKIP_CLASSES:
            stats["null"] += 1
            null_classes.append(usdm_class)

            print("          ⏭ skipped large class")

            continue

        # ── Adaptive retrieval depth ───────────────────────────────────────────

        adaptive_top_k = (
            3
            if usdm_class in LARGE_CLASSES
            else config.TOP_K_CHUNKS
        )

        relevant, source = get_relevant_chunks_from_memory(
            chunk_index  = chunk_index,
            memory       = memory,
            usdm_class   = usdm_class,
            all_chunks   = chunks,
            threshold    = config.RELEVANCE_THRESHOLD,
            top_k        = adaptive_top_k,
        )

        if source == "memory":
            stats["via_memory"] += 1
            print(f"          🧠 {len(relevant)} chunk(s) via memory")

        elif source == "keyword":
            stats["via_keyword"] += 1
            print(f"          🔑 {len(relevant)} chunk(s) via keyword fallback")

        else:
            print(f"          ⬜ no relevant chunks → keeping empty schema")

            master_usdm = merge_usdm(
                master_usdm,
                subschema
            )

            null_classes.append(usdm_class)

            stats["null"] += 1

            continue


        # ── Reduce context for huge high-cardinality classes ─────────────────

        if usdm_class in SPLIT_CLASSES:

            relevant = relevant[:1]

            print(
                "          ✂ reduced context "
                "for high-cardinality class"
            )


        # ── Empty retrieval protection ───────────────────────────────────────

        if not relevant:

            print("          ⬜ empty retrieval")

            master_usdm = merge_usdm(
                master_usdm,
                subschema
            )

            stats["null"] += 1

            continue

        # ── 2c: Build context string ──────────────────────────────────────────
        if not relevant:

            print("          ⬜ empty retrieval")

            master_usdm = merge_usdm(
                master_usdm,
                subschema
            )

            stats["null"] += 1

            continue
        context_text = build_context(relevant)

        # ── 2d: Build prompt ──────────────────────────────────────────────────
        messages = build_messages(usdm_class, context_text, subschema)

        # ── 2e: LLM call ──────────────────────────────────────────────────────
        # ── Adaptive token budget ──────────────────────────────────────────────

        max_tokens = (
            10000
            if usdm_class in LARGE_CLASSES
            else 4000
        )
        extracted = extract_usdm_section(messages, max_tokens=max_tokens)

        # ── 2f: Handle LLM errors ─────────────────────────────────────────────
        if "error" in extracted:

            try:

                os.makedirs("debug", exist_ok=True)

                raw_response = extracted.get(
                    "raw_response",
                    ""
                )

                with open(

                    f"debug/{usdm_class}_failed.txt",

                    "w",

                    encoding="utf-8"

                ) as f:

                    f.write(raw_response)

            except Exception:
                pass

            print(
                f"          ❌ error: "
                f"{extracted['error']}"
            )

            error_classes.append(usdm_class)

            stats["error"] += 1

            # merge empty schema instead
            master_usdm = merge_usdm(
                master_usdm,
                subschema
            )

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
        time.sleep(1)

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
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(master_usdm, f, indent=2, ensure_ascii=False)

    print(f"\n💾  USDM saved → {config.OUTPUT_FILE}")

    # ──────────────────────────────────────────────────────────────────────────
    # STEP 5 — Run summary
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  RUN SUMMARY")
    print("=" * 70)
    print(f"  Total classes  : {stats['total']}")
    print(f"  Extracted      : {stats['extracted']}  ✅")
    print(f"    via memory   : {stats['via_memory']}")
    print(f"    via keyword  : {stats['via_keyword']}")
    print(f"  Empty (no data): {stats['null'] + stats['empty_llm']}  ⬜  (present in output, values null)")
    print(f"  Errors         : {stats['error']}  ❌  (absent from output)")

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
        description="Extract USDM JSON from a pre-chunked JSON file."
    )
    parser.add_argument(
        "chunks",
        nargs="?",
        default=DEFAULT_CHUNKS_PATH,
        help=f"Path to raw_chunking.json (default: {DEFAULT_CHUNKS_PATH})",
    )
    parser.add_argument(
        "memory",
        nargs="?",
        default=DEFAULT_MEMORY_PATH,
        help=f"Path to semantic_memory.json (default: {DEFAULT_MEMORY_PATH}); omit or pass '' to disable",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=config.RELEVANCE_THRESHOLD,
        help="Minimum relevance score for keyword fallback (default: %(default)s)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=config.TOP_K_CHUNKS,
        help="Max chunks per USDM class (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        default=config.OUTPUT_FILE,
        help=f"Output path for final USDM JSON (default: {config.OUTPUT_FILE})",
    )

    args = parser.parse_args()

    import config as _cfg
    _cfg.RELEVANCE_THRESHOLD = args.threshold
    _cfg.TOP_K_CHUNKS        = args.top_k
    _cfg.OUTPUT_FILE         = args.output

    run_pipeline(chunks_path=args.chunks, memory_path=args.memory)