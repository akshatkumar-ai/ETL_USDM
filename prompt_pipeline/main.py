import os
import json

from extractor_text import extract_text

from chunker import chunk_document

from subsection import get_subschema

from prompt_builder import build_messages

from llm_caller import extract_usdm_section

from merger import merge_usdm

from validator import (
    validate_usdm,
    print_validation_report
)


# =========================================================
# CONFIG
# =========================================================

PDF_PATH = "sample_protocol.pdf"

OUTPUT_DIR = "output"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "final_usdm.json"
)

TEMPLATE_PATH = "templates/usdm_empty.json"


# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline():

    print("\n" + "=" * 60)
    print("USDM EXTRACTION PIPELINE")
    print("=" * 60)


    # -----------------------------------------------------
    # STEP 1 — EXTRACT TEXT
    # -----------------------------------------------------

    print("\n📄 Extracting text from PDF...")

    raw_text = extract_text(PDF_PATH)

    print("✅ Text extraction complete")


    # -----------------------------------------------------
    # STEP 2 — CHUNK DOCUMENT
    # -----------------------------------------------------

    print("\n🧩 Creating semantic chunks...")

    chunks = chunk_document(raw_text)

    print(f"✅ Total chunks found: {len(chunks)}")


    # -----------------------------------------------------
    # STEP 3 — INITIALIZE MASTER USDM
    # -----------------------------------------------------

    master_usdm = {}


    # -----------------------------------------------------
    # STEP 4 — PROCESS EACH CHUNK
    # -----------------------------------------------------

    for i, chunk in enumerate(chunks):

        print("\n" + "-" * 60)

        print(f"🔹 Processing chunk {i+1}/{len(chunks)}")

        print(f"SECTION: {chunk['section']}")

        print(f"USDM TARGETS: {chunk['usdm_targets']}")


        # -------------------------------------------------
        # GET TARGET SUBSCHEMA
        # -------------------------------------------------

        subschema = get_subschema(
            chunk["usdm_targets"],
            template_path=TEMPLATE_PATH
        )


        # -------------------------------------------------
        # BUILD PROMPT
        # -------------------------------------------------

        messages = build_messages(
            section_name=chunk["section"],
            chunk_text=chunk["text"],
            subschema=subschema
        )


        # -------------------------------------------------
        # EXTRACT STRUCTURED DATA
        # -------------------------------------------------

        extracted_json = extract_usdm_section(
            messages
        )


        # -------------------------------------------------
        # HANDLE EXTRACTION ERRORS
        # -------------------------------------------------

        if "error" in extracted_json:

            print("❌ Extraction failed")

            continue


        print("✅ Extraction successful")


        # -------------------------------------------------
        # MERGE INTO MASTER USDM
        # -------------------------------------------------

        master_usdm = merge_usdm(
            master_usdm,
            extracted_json
        )

        print("✅ Merged into master USDM")


    # -----------------------------------------------------
    # STEP 5 — VALIDATE FINAL USDM
    # -----------------------------------------------------

    print("\n" + "=" * 60)

    print("🔎 VALIDATING FINAL USDM")

    validation_results = validate_usdm(
        master_usdm
    )

    print_validation_report(
        validation_results
    )


    # -----------------------------------------------------
    # STEP 6 — SAVE OUTPUT
    # -----------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            master_usdm,
            f,
            indent=2
        )

    print(f"\n💾 Final USDM saved to:")
    print(OUTPUT_FILE)

    print("\n✅ PIPELINE COMPLETE")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_pipeline()