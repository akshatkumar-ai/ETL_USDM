# config.py
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# ── Chunking ───────────────────────────────────────────────────────────────────
CHUNK_SIZE    = 2000
CHUNK_OVERLAP = 200

# ── Retrieval (keyword-based scorer) ──────────────────────────────────────────
# A chunk must score at or above this value to be included for a USDM class.
# Score is composed of:
#   keyword hit-rate (0–1) + section bonus (0.25) + density bonus (0–0.15)
# A threshold of 0.05 means at least ~one keyword match per 20 keywords.
RELEVANCE_THRESHOLD = 0.05

# Maximum chunks concatenated per USDM class LLM call.
TOP_K_CHUNKS = 5

# ── LLM ───────────────────────────────────────────────────────────────────────
ANTHROPIC_MODEL   = "arn:aws:bedrock:us-east-1:533267065792:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
LLM_MAX_TOKENS    = 4000
LLM_TEMPERATURE   = 0.0

# ── Paths ─────────────────────────────────────────────────────────────────────
TEMPLATE_PATH = (
    BASE_DIR
    / "template"
    / "usdm_schema.json"
)
OUTPUT_DIR    = BASE_DIR / "output"
OUTPUT_FILE   = OUTPUT_DIR / "final_usdm.json"
CHUNKING_STRATEGY = "hybrid"   # options: 'fixed', 'section_headers'