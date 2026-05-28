# run.py
#
# Thin entrypoint for complete USDM extraction pipeline
#
# Usage:
#
#   python run.py protocol.pdf
#
# Optional:
#
#   python run.py protocol.pdf --threshold 0.2
#   python run.py protocol.pdf --top-k 5
#

from __future__ import annotations

import os
import sys
import argparse

# ─────────────────────────────────────────────────────────
# Project root
# ─────────────────────────────────────────────────────────

ROOT_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

sys.path.insert(0, ROOT_DIR)

# ─────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────

from prompt_pipeline.main import run_pipeline

import config


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():

    parser = argparse.ArgumentParser(
        description="Complete USDM extraction pipeline"
    )

    parser.add_argument(
        "document",
        help="Path to protocol PDF/TXT document"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=config.RELEVANCE_THRESHOLD,
        help="Keyword relevance threshold"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=config.TOP_K_CHUNKS,
        help="Maximum retrieved chunks per class"
    )

    parser.add_argument(
        "--output",
        default=config.OUTPUT_FILE,
        help="Final USDM output path"
    )

    args = parser.parse_args()

    # ─────────────────────────────────────────────────────
    # Apply runtime config overrides
    # ─────────────────────────────────────────────────────

    config.RELEVANCE_THRESHOLD = args.threshold

    config.TOP_K_CHUNKS = args.top_k

    config.OUTPUT_FILE = args.output

    # ─────────────────────────────────────────────────────
    # Run pipeline
    # ─────────────────────────────────────────────────────

    run_pipeline(
        document_path=args.document
    )


# ─────────────────────────────────────────────────────────
# Entry
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":

    main()