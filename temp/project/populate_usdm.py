# populate_usdm.py

import json
from tqdm import tqdm

from llm import llm_call

from utils import (
    load_text_file,
    load_json,
    save_json,
    clean_json_response,
    deep_merge
)

from config.class_groups import CLASS_GROUPS
from config.class_query_map import CLASS_QUERY_MAP

from config.prompts import (
    SYSTEM_PROMPT,
    RETRIEVAL_EXTRACTION_TEMPLATE
)

from retrieval.chunker import chunk_text
from retrieval.retriever import retrieve_chunks


# =========================================================
# PATHS
# =========================================================

PROTOCOL_PATH = "/home/riya/USDM/ETL_USDM/temp/project/data/protocol.txt"

USDM_SHELL_PATH = "/home/riya/USDM/ETL_USDM/temp/project/data/usdm_shell.json"

OUTPUT_PATH = "/home/riya/USDM/ETL_USDM/temp/project/output/populated_usdm.json"


# =========================================================
# LOAD DATA
# =========================================================

print("\nLoading protocol text...")

protocol_text = load_text_file(PROTOCOL_PATH)

print("Loading USDM shell...")

usdm_shell = load_json(USDM_SHELL_PATH)


# =========================================================
# CHUNK PROTOCOL
# =========================================================

print("\nChunking protocol...")

protocol_chunks = chunk_text(
    protocol_text,
    chunk_size=3000,
    overlap=300
)

print(f"Created {len(protocol_chunks)} chunks")


# =========================================================
# EXTRACTION LOOP
# =========================================================

for class_name in tqdm(CLASS_GROUPS.keys()):

    print("\n" + "=" * 80)
    print(f"PROCESSING CLASS: {class_name}")
    print("=" * 80)

    # -----------------------------------------------------
    # GET CLASS SCHEMA
    # -----------------------------------------------------

    schema = CLASS_GROUPS[class_name]

    # -----------------------------------------------------
    # GET RETRIEVAL QUERY
    # -----------------------------------------------------

    retrieval_query = CLASS_QUERY_MAP.get(
        class_name,
        class_name
    )

    # -----------------------------------------------------
    # RETRIEVE RELEVANT CHUNKS
    # -----------------------------------------------------

    retrieved_chunks = retrieve_chunks(
        query=retrieval_query,
        chunks=protocol_chunks,
        top_k=5
    )

    combined_chunks = "\n\n".join(retrieved_chunks)

    print(f"\nRetrieved {len(retrieved_chunks)} chunks")

    # -----------------------------------------------------
    # BUILD PROMPT
    # -----------------------------------------------------

    prompt = RETRIEVAL_EXTRACTION_TEMPLATE.format(
        class_name=class_name,
        schema=json.dumps(schema, indent=2),
        retrieved_chunks=combined_chunks
    )

    # -----------------------------------------------------
    # CALL LLM
    # -----------------------------------------------------

    print("\nCalling LLM...")

    response = llm_call(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0,
        max_tokens=4000
    )

    # -----------------------------------------------------
    # CLEAN RESPONSE
    # -----------------------------------------------------

    response = clean_json_response(response)

    # -----------------------------------------------------
    # PARSE JSON
    # -----------------------------------------------------

    try:

        extracted_json = json.loads(response)

        print("\nExtraction successful")

    except Exception as e:

        print("\nJSON PARSE FAILED")
        print(e)

        print("\nRAW RESPONSE:")
        print(response[:2000])

        continue

    # -----------------------------------------------------
    # MERGE INTO MASTER USDM
    # -----------------------------------------------------

    deep_merge(
        usdm_shell,
        extracted_json
    )

    print("\nMerged into USDM")


# =========================================================
# SAVE OUTPUT
# =========================================================

print("\nSaving populated USDM...")

save_json(
    usdm_shell,
    OUTPUT_PATH
)

print(f"\nDONE")
print(f"\nSaved to:\n{OUTPUT_PATH}")