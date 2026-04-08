# embedder.py

#from openai import OpenAI
# from config import EMBED_MODEL


# client = OpenAI(api_key="key")
from sentence_transformers import SentenceTransformer

# Choose model
model = SentenceTransformer("BAAI/bge-m3")

def get_embeddings(texts: list):
    """
    Generate embeddings locally (FREE)
    """
    embeddings = model.encode(
        texts,
        normalize_embeddings=True  # important for cosine similarity
    )

    return embeddings.tolist()
# def get_embeddings(texts: list):
#     """
#     Generate embeddings for list of texts
#     """
#     response = client.embeddings.create(
#         model=EMBED_MODEL,
#         input=texts
#     )

#     return [e.embedding for e in response.data]