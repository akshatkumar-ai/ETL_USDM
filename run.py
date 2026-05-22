# run.py
#
# COMPLETE END-TO-END USDM PIPELINE
#
# Flow:
#   1. Extract text from PDF
#   2. Create chunks
#   3. Save raw_chunks.json
#   4. Build semantic_memory.json
#   5. Run USDM extraction pipeline
#   6. Save final USDM
#
# Usage:
#
# python run.py protocol.pdf
#
# Optional:
#
# python run.py protocol.pdf --chunking recursive
# python run.py protocol.pdf --chunking hybrid
#

from __future__ import annotations

import os
import json
import argparse
import sys

# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, ROOT_DIR)

# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

from preprocessing.extractor_text import extract_text
from preprocessing.chunk_manager import chunk_document

from preprocessing.memory_builder import (
    build_semantic_memory
)

from prompt_pipeline.main import run_pipeline

# ---------------------------------------------------------
# OUTPUT PATHS
# ---------------------------------------------------------

OUTPUT_DIR = "output"

RAW_TEXT_PATH = os.path.join(
    OUTPUT_DIR,
    "raw_protocol_text.txt"
)

RAW_CHUNKS_PATH = os.path.join(
    OUTPUT_DIR,
    "raw_chunks.json"
)

MEMORY_PATH = os.path.join(
    OUTPUT_DIR,
    "semantic_memory.json"
)

# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------

def save_json(data, path):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="Complete USDM extraction pipeline"
    )

    parser.add_argument(
        "pdf",
        help="Path to clinical protocol PDF"
    )

    parser.add_argument(
        "--chunking",
        default="recursive",
        choices=[
            "section",
            "semantic",
            "hierarchical",
            "recursive",
            "llm_dynamic",
            "hybrid"
        ],
        help="Chunking strategy"
    )

    args = parser.parse_args()

    pdf_path = args.pdf

    chunking_strategy = args.chunking

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n" + "=" * 80)
    print(" COMPLETE USDM PIPELINE ")
    print("=" * 80)

    # =====================================================
    # STEP 1 — EXTRACT TEXT
    # =====================================================

    print("\n📄 STEP 1 — Extracting text from PDF")

    raw_text = extract_text(pdf_path)

    with open(
        RAW_TEXT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(raw_text)

    print("✅ Text extraction complete")

    # =====================================================
    # STEP 2 — CHUNK DOCUMENT
    # =====================================================

    print("\n🧩 STEP 2 — Creating chunks")

    chunks = chunk_document(
        raw_text,
        strategy=chunking_strategy
    )

    # normalize chunk IDs
    normalized_chunks = []

    for idx, chunk in enumerate(chunks):

        normalized_chunks.append({

            "chunk_id":
                f"chunk_{idx+1:04d}",

            "section":
                chunk.get(
                    "section",
                    "UNKNOWN"
                ),

            "subsection":
                chunk.get(
                    "subsection",
                    ""
                ),

            "text":
                chunk.get(
                    "text",
                    ""
                )
        })

    save_json(
        normalized_chunks,
        RAW_CHUNKS_PATH
    )

    print(f"✅ {len(normalized_chunks)} chunks created")

    # =====================================================
    # STEP 3 — BUILD SEMANTIC MEMORY
    # =====================================================

    print("\n🧠 STEP 3 — Building semantic memory")

    memory_response = build_semantic_memory(
        normalized_chunks
    )

    try:

        semantic_memory = memory_response

    except Exception:

        print("\n❌ Failed to parse semantic memory")

        print(memory_response)

        return

    save_json(
        semantic_memory,
        MEMORY_PATH
    )

    print("✅ semantic_memory.json created")

    # =====================================================
    # STEP 4 — RUN USDM PIPELINE
    # =====================================================

    print("\n🏗 STEP 4 — Running USDM extraction")

    final_usdm = run_pipeline(
        chunks_path=RAW_CHUNKS_PATH,
        memory_path=MEMORY_PATH
    )

    print("\n" + "=" * 80)
    print(" PIPELINE COMPLETE ")
    print("=" * 80)

    print("\nFinal output:")

    print("output/final_usdm.json")

# ---------------------------------------------------------
# ENTRY
# ---------------------------------------------------------

if __name__ == "__main__":

    main()