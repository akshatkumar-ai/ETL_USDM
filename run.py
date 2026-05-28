# # run.py
# #
# # Thin entrypoint for complete USDM extraction pipeline
# #
# # Usage:
# #
# #   python run.py protocol.pdf
# #
# # Optional:
# #
# #   python run.py protocol.pdf --threshold 0.2
# #   python run.py protocol.pdf --top-k 5
# #

# from __future__ import annotations

# import os
# import sys
# import argparse

# # ─────────────────────────────────────────────────────────
# # Project root
# # ─────────────────────────────────────────────────────────

# ROOT_DIR = os.path.abspath(
#     os.path.dirname(__file__)
# )

# sys.path.insert(0, ROOT_DIR)

# # ─────────────────────────────────────────────────────────
# # Imports
# # ─────────────────────────────────────────────────────────

# from prompt_pipeline.main import run_pipeline

# import config


# # ─────────────────────────────────────────────────────────
# # Main
# # ─────────────────────────────────────────────────────────

# def main():

#     parser = argparse.ArgumentParser(
#         description="Complete USDM extraction pipeline"
#     )

#     parser.add_argument(
#         "document",
#         help="Path to protocol PDF/TXT document"
#     )

#     parser.add_argument(
#         "--threshold",
#         type=float,
#         default=config.RELEVANCE_THRESHOLD,
#         help="Keyword relevance threshold"
#     )

#     parser.add_argument(
#         "--top-k",
#         type=int,
#         default=config.TOP_K_CHUNKS,
#         help="Maximum retrieved chunks per class"
#     )

#     parser.add_argument(
#         "--output",
#         default=config.OUTPUT_FILE,
#         help="Final USDM output path"
#     )

#     args = parser.parse_args()

#     # ─────────────────────────────────────────────────────
#     # Apply runtime config overrides
#     # ─────────────────────────────────────────────────────

#     config.RELEVANCE_THRESHOLD = args.threshold

#     config.TOP_K_CHUNKS = args.top_k

#     config.OUTPUT_FILE = args.output

#     # ─────────────────────────────────────────────────────
#     # Run pipeline
#     # ─────────────────────────────────────────────────────

#     run_pipeline(
#         document_path=args.document
#     )


# # ─────────────────────────────────────────────────────────
# # Entry
# # ─────────────────────────────────────────────────────────

# if __name__ == "__main__":

#     main()





# run.py
#
# Top-level USDM extraction orchestrator.
#
# Scans document folders in priority order, runs a full extraction pass
# for each document found, and accumulates results into one master USDM.
#
# DOCUMENT PRIORITY (highest → lowest):
#   synopsis  →  protocol  →  sap  →  mop  →  csr
#
# Each folder must contain exactly ONE PDF. Multiple PDFs → error.
# Missing folders or empty folders → skipped silently.
#
# THREE-STATE MERGE LOGIC (per USDM class, per pass):
#   FULL    — already filled from a prior pass → skip
#   EMPTY   — not yet populated → extract and merge
#   PARTIAL — some fields filled → extract then LLM judge picks best version
#
# OUTPUT LAYOUT:
#   output/
#     synopsis/
#       raw_text.txt
#       raw_chunks.json
#       semantic_memory.json
#       debug/                   ← LLM error dumps
#       usdm_after_synopsis.json ← intermediate checkpoint
#     protocol/
#       ...
#       usdm_after_protocol.json
#     sap/ mop/ csr/ ...
#     final_usdm.json            ← final accumulated result
#
# USAGE:
#   python run.py                          # scan default folder layout
#   python run.py --strategy hybrid        # override chunking strategy
#   python run.py --output-dir my_output   # custom output root

from __future__ import annotations

import argparse
import json
import os
import sys
import glob

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import config
from prompt_pipeline.main import run_document_pass


# ── Document priority ──────────────────────────────────────────────────────────
#
# (folder_name, doc_type_label)
# folder_name  : directory to scan for a PDF
# doc_type_label: used for output subdirectory name and log messages

DOCUMENT_PRIORITY: list[tuple[str, str]] = [
    ("synopsis", "synopsis"),
    ("protocol", "protocol"),
    ("sap",      "sap"),
    ("mop",      "mop"),
    ("csr",      "csr"),
]


# ── Document discovery ─────────────────────────────────────────────────────────

def find_document(folder_name: str) -> str | None:
    """
    Scan folder_name for a single PDF.

    Returns
    -------
    str  — absolute path to the PDF if exactly one found
    None — if the folder does not exist or contains no PDFs

    Raises
    ------
    ValueError  if the folder contains more than one PDF
    """
    if not os.path.isdir(folder_name):
        return None

    pdfs = glob.glob(os.path.join(folder_name, "*.pdf"))
    pdfs += glob.glob(os.path.join(folder_name, "*.PDF"))

    # Deduplicate (case-insensitive FS might double-count)
    pdfs = sorted(set(os.path.abspath(p) for p in pdfs))

    if len(pdfs) == 0:
        return None

    if len(pdfs) > 1:
        names = "\n  ".join(pdfs)
        raise ValueError(
            f"Folder '{folder_name}' contains {len(pdfs)} PDFs — "
            f"expected exactly 1:\n  {names}\n"
            f"Please keep only one PDF per folder."
        )

    return pdfs[0]


# ── Intermediate checkpoint ────────────────────────────────────────────────────

def save_checkpoint(
    master_usdm: dict,
    doc_type:    str,
    output_dir:  str,
) -> None:
    """Save usdm_after_<doc_type>.json inside the per-document output dir."""
    path = os.path.join(output_dir, doc_type, f"usdm_after_{doc_type}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(master_usdm, f, indent=2, ensure_ascii=False)
    print(f"💾  Checkpoint saved → {path}")


# ── Orchestrator ───────────────────────────────────────────────────────────────

def run(
    strategy:   str = "recursive",
    output_dir: str = config.OUTPUT_DIR,
) -> dict:
    """
    Run the full multi-document USDM extraction pipeline.

    Parameters
    ----------
    strategy   : chunking strategy passed to every document pass
    output_dir : root output directory (default: from config)

    Returns
    -------
    Final accumulated master_usdm dict.
    """

    print("\n" + "=" * 70)
    print("  USDM MULTI-DOCUMENT EXTRACTION PIPELINE")
    print("=" * 70)
    print(f"\n  Priority order: {' → '.join(f for f, _ in DOCUMENT_PRIORITY)}")
    print(f"  Chunking strategy: {strategy}")
    print(f"  Output root: {output_dir}")

    # Override config so all sub-modules write to the right place
    config.OUTPUT_DIR = output_dir
    config.OUTPUT_FILE = os.path.join(output_dir, "final_usdm.json")

    os.makedirs(output_dir, exist_ok=True)

    # ── Scan folders ──────────────────────────────────────────────────────────
    print("\n  Scanning document folders ...\n")

    found_documents: list[tuple[str, str, str]] = []   # (folder, doc_type, pdf_path)

    for folder_name, doc_type in DOCUMENT_PRIORITY:
        try:
            pdf_path = find_document(folder_name)
        except ValueError as e:
            # Multiple PDFs in one folder → hard stop
            print(f"\n❌  ERROR in '{folder_name}':\n    {e}")
            sys.exit(1)

        if pdf_path is None:
            print(f"  ⬜  {folder_name:<12} — not found, skipping")
        else:
            print(f"  ✅  {folder_name:<12} — {pdf_path}")
            found_documents.append((folder_name, doc_type, pdf_path))

    if not found_documents:
        print(
            "\n❌  No documents found in any priority folder.\n"
            "    Create at least one of: "
            + ", ".join(f for f, _ in DOCUMENT_PRIORITY)
            + "\n    and place one PDF inside it."
        )
        sys.exit(1)

    print(f"\n  {len(found_documents)} document(s) will be processed.\n")

    # ── Run passes ────────────────────────────────────────────────────────────
    master_usdm: dict = {}

    for folder_name, doc_type, pdf_path in found_documents:

        print(f"\n{'='*70}")
        print(f"  STARTING PASS: {doc_type.upper()}")
        print(f"{'='*70}")

        master_usdm = run_document_pass(
            document_path = pdf_path,
            doc_type      = doc_type,
            master_usdm   = master_usdm,
            strategy      = strategy,
        )

        # Save intermediate checkpoint immediately after each pass
        save_checkpoint(master_usdm, doc_type, output_dir)

    # ── Save final output ─────────────────────────────────────────────────────
    final_path = os.path.join(output_dir, "final_usdm.json")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(master_usdm, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"💾  FINAL USDM saved → {final_path}")
    print(f"\n  Passes completed : {len(found_documents)}")
    print(f"  Documents        : {', '.join(dt for _, dt, _ in found_documents)}")
    print("\n✅  PIPELINE COMPLETE\n")

    return master_usdm


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "USDM multi-document extraction pipeline.\n"
            "Scans synopsis/, protocol/, sap/, mop/, csr/ folders in priority order."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--strategy",
        default   = "recursive",
        choices   = ["section", "semantic", "hierarchical",
                     "recursive", "llm_dynamic", "hybrid"],
        help      = "Chunking strategy to use for all documents (default: recursive)",
    )
    parser.add_argument(
        "--output-dir",
        default = config.OUTPUT_DIR,
        dest    = "output_dir",
        help    = f"Root output directory (default: {config.OUTPUT_DIR})",
    )
    parser.add_argument(
        "--threshold",
        type    = float,
        default = config.RELEVANCE_THRESHOLD,
        help    = "Keyword relevance threshold for chunk retrieval (default: %(default)s)",
    )
    parser.add_argument(
        "--top-k",
        type    = int,
        default = config.TOP_K_CHUNKS,
        dest    = "top_k",
        help    = "Max chunks per USDM class (default: %(default)s)",
    )

    args = parser.parse_args()

    # Apply CLI overrides to config before any imports read them
    config.RELEVANCE_THRESHOLD = args.threshold
    config.TOP_K_CHUNKS        = args.top_k

    run(
        strategy   = args.strategy,
        output_dir = args.output_dir,
    )