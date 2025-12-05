# question_rag/ingestion.py

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

from google.cloud import storage
import vertexai
from vertexai import rag

from .config import PROJECT_ID, LOCATION, BUCKET_NAME, CORPUS_NAME, CORPUS_FILE

# ---------- Paths ----------

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

INPUT_METADATA_PATH = INPUT_DIR / "metadata_input.json"
NORMALIZED_METADATA_PATH = INPUT_DIR / "normalized_metadata.json"
LOCAL_CORPUS_PATH = BASE_DIR / CORPUS_FILE  # usually "metadata_tagging_file.txt"


# ---------- Step 1: Load teacher/matcher JSON ----------

def load_raw_metadata() -> Dict:
    """Load the teacher/matcher JSON from input/metadata_input.json."""
    if not INPUT_METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Input metadata JSON not found at: {INPUT_METADATA_PATH}. "
            "This file should contain the 'questions' + 'matches' structure."
        )

    with INPUT_METADATA_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "questions" not in data or not isinstance(data["questions"], list):
        raise ValueError(
            f"Invalid format in {INPUT_METADATA_PATH}: expected a top-level key 'questions' "
            "containing a list."
        )

    return data


# ---------- Step 2: Normalize into a stable format ----------

def normalize_metadata(raw: Dict) -> List[Dict]:
    """
    Convert the input structure:

      {
        "questions": [
          {
            "question": "...",
            "matches": [
              {"concept": "...", "score": 0.13},
              ...
            ]
          },
          ...
        ]
      }

    into a list like:

      [
        {
          "id": "q_001",
          "text": "...",
          "main_concept": "...",
          "concepts": ["...", "...", "..."]
        },
        ...
      ]
    """
    normalized: List[Dict] = []

    questions = raw.get("questions", [])
    for idx, item in enumerate(questions, start=1):
        q_text = item.get("question", "").strip()
        matches = item.get("matches", []) or []

        # ID: q_001, q_002, ...
        q_id = f"q_{idx:03d}"

        # Main concept = best match (if any)
        if matches:
            main_concept = matches[0].get("concept", "UNKNOWN")
            # Keep up to top 3 concepts
            concept_list = [
                m.get("concept", "").strip()
                for m in matches[:3]
                if m.get("concept")
            ]
        else:
            main_concept = "UNKNOWN"
            concept_list = []

        normalized.append(
            {
                "id": q_id,
                "text": q_text,
                "main_concept": main_concept,
                "concepts": concept_list,
            }
        )

    return normalized


def save_normalized_metadata(entries: List[Dict]) -> None:
    """Write normalized metadata to input/normalized_metadata.json."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    with NORMALIZED_METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"[INGEST] Wrote normalized metadata to: {NORMALIZED_METADATA_PATH}")
    print(f"[INGEST] Total questions: {len(entries)}")


# ---------- Step 3: Build corpus text file ----------

def build_corpus_text(entries: List[Dict]) -> str:
    """
    Build the text that will go into metadata_tagging_file.txt, e.g.:

    [ID: q_001]
    [MAIN_CONCEPT: ...]
    [CONCEPTS: A; B; C]

    Question text...

    ---
    """
    blocks: List[str] = []

    for e in entries:
        q_id = e.get("id", "").strip()
        text = e.get("text", "").strip()
        main_concept = e.get("main_concept", "UNKNOWN").strip()
        concepts = e.get("concepts") or []

        concepts_str = "; ".join(c for c in concepts if c)

        header_lines = [
            f"[ID: {q_id}]",
            f"[MAIN_CONCEPT: {main_concept}]",
            f"[CONCEPTS: {concepts_str}]",
            "",
            text,
            "",
            "---",
        ]

        blocks.append("\n".join(header_lines))

    return "\n\n".join(blocks).strip() + "\n"


def save_corpus_file(corpus_text: str) -> None:
    """Save corpus text to the local CORPUS_FILE (e.g. metadata_tagging_file.txt)."""
    with LOCAL_CORPUS_PATH.open("w", encoding="utf-8") as f:
        f.write(corpus_text)
    print(f"[INGEST] Wrote corpus file to: {LOCAL_CORPUS_PATH}")


# ---------- Step 4: Upload to GCS ----------

def upload_corpus_to_gcs() -> str:
    """
    Upload the local corpus file to the configured bucket.
    Returns the GCS URI (gs://...).
    """
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(CORPUS_FILE)

    blob.upload_from_filename(str(LOCAL_CORPUS_PATH))
    gcs_uri = f"gs://{BUCKET_NAME}/{CORPUS_FILE}"
    print(f"[INGEST] Uploaded corpus file to: {gcs_uri}")
    return gcs_uri


# ---------- Step 5: Re-import into RAG corpus ----------

def import_into_rag(gcs_uri: str) -> None:
    """Call Vertex RAG to (re)import the corpus file from GCS using your SDK's signature."""
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    rag_corpus_name = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_NAME}"
    )
    print(f"[INGEST] Re-importing into RAG corpus: {rag_corpus_name}")

    # Most minimal signature: (rag_corpus_name, [uris])
    rag.import_files(
        rag_corpus_name,
        [gcs_uri],
    )

    print("[INGEST] RAG import request sent using minimal signature rag.import_files(name, [uri]).")



# ---------- Orchestrator ----------

def run_ingestion() -> None:
    """End-to-end ingestion: input JSON -> normalized -> corpus -> GCS -> RAG."""
    print("=== Question RAG Ingestion ===")

    # 1) Load raw teacher/matcher JSON
    print("[STEP 1] Loading raw metadata from:", INPUT_METADATA_PATH)
    raw = load_raw_metadata()

    # 2) Normalize and save JSON
    print("[STEP 2] Normalizing metadata...")
    entries = normalize_metadata(raw)
    save_normalized_metadata(entries)

    # 3) Build corpus text and save
    print("[STEP 3] Building corpus text file...")
    corpus_text = build_corpus_text(entries)
    save_corpus_file(corpus_text)

    # 4) Upload to GCS
    print("[STEP 4] Uploading corpus file to Cloud Storage...")
    gcs_uri = upload_corpus_to_gcs()

    # 5) Import into existing RAG corpus
    print("[STEP 5] Importing file into RAG corpus...")
    import_into_rag(gcs_uri)

    print("=== Ingestion complete ===")


if __name__ == "__main__":
    run_ingestion()
