# vectordb.py

import chromadb
import hashlib
import time
import os

from config import VECTOR_DB_DIR, COLLECTION_NAME

client = chromadb.PersistentClient(path=VECTOR_DB_DIR)



def get_collection(doc_id):
    
    collection_name = f"{COLLECTION_NAME}_{doc_id}"
    print(f"Using collection: {collection_name}")
    return client.get_or_create_collection(name=collection_name)


def store_chunks(chunks, embeddings, doc_id):
    collection = get_collection(doc_id)

    ids = []
    for i, chunk in enumerate(chunks):
        content_hash = hashlib.md5(chunk["text"].encode()).hexdigest()[:8]
        timestamp = str(int(time.time() * 1000000))
        unique_id = f"{content_hash}_{timestamp}_{i}"
        ids.append(unique_id)

    documents = [c["text"] for c in chunks]
    metadatas = [{"section": c["section"]} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

def query_chunks(query_embedding, doc_id, top_k=5):
    collection = get_collection(doc_id)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results
