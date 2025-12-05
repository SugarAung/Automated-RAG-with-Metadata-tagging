# question_rag/config.py

import os
from dotenv import load_dotenv

# Find the project root (one folder above this file)
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(ROOT_DIR, ".env")

# Load the .env file from the project root
load_dotenv(ENV_PATH, override=True)

# GCP / Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True") == "True"

# RAG settings
BUCKET_NAME = os.getenv("RAG_BUCKET_NAME")
CORPUS_NAME = os.getenv("RAG_CORPUS_NAME")
CORPUS_FILE = os.getenv("RAG_CORPUS_FILE", "metadata_tagging_file.txt")

# (Optional for later)
CONCEPT_THRESHOLD = float(os.getenv("CONCEPT_SCORE_THRESHOLD", 0.1))
DEFAULT_MAIN_CONCEPT = os.getenv("DEFAULT_MAIN_CONCEPT", "UNKNOWN")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-1.5-flash")

if __name__ == "__main__":
    print("PROJECT_ID:", PROJECT_ID)
    print("LOCATION:", LOCATION)
    print("BUCKET_NAME:", BUCKET_NAME)
    print("CORPUS_NAME:", CORPUS_NAME)
