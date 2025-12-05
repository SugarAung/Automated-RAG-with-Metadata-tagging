# question_rag/agents/retrieval_tools.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Dict, Any

import vertexai
from vertexai import rag

from question_rag.config import PROJECT_ID, LOCATION, CORPUS_NAME


@dataclass
class QuestionHit:
    id: str
    text: str
    main_concept: str
    concepts: List[str]
    score: float


def _get_corpus_name() -> str:
    return f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_NAME}"


def _parse_block(raw: str) -> Dict[str, Any]:
    """
    Parse one block from metadata_tagging_file.txt.

    Expected shape:

        [ID: q_001]
        [MAIN_CONCEPT: ...]
        [CONCEPTS: A; B; C]

        Question text...

        ---
    """
    lines = raw.splitlines()
    if len(lines) < 1:
        return {
            "id": "UNKNOWN_ID",
            "main_concept": "UNKNOWN",
            "concepts": [],
            "text": raw.strip(),
        }

    def extract(bracket_line: str, label: str, default: str = "UNKNOWN") -> str:
        prefix = f"[{label}:"
        if bracket_line.startswith(prefix):
            return bracket_line[len(prefix):].rstrip("]").strip()
        return default

    id_ = extract(lines[0], "ID", "UNKNOWN_ID") if len(lines) > 0 else "UNKNOWN_ID"
    main_concept = (
        extract(lines[1], "MAIN_CONCEPT", "UNKNOWN") if len(lines) > 1 else "UNKNOWN"
    )
    concepts_raw = extract(lines[2], "CONCEPTS", "") if len(lines) > 2 else ""
    concepts = [c.strip() for c in concepts_raw.split(";") if c.strip()]

    # Find the '---' line that ends this block
    try:
        sep_index = lines.index("---")
    except ValueError:
        sep_index = len(lines)

    question_lines = lines[4:sep_index]  # skip 0,1,2 header + 3 blank
    question_text = "\n".join(question_lines).strip() or raw.strip()

    return {
        "id": id_,
        "main_concept": main_concept,
        "concepts": concepts,
        "text": question_text,
    }


def search_questions(query: str, top_k: int = 5) -> List[QuestionHit]:
    """
    Query the RAG corpus by free-text `query`.

    Returns a list of QuestionHit objects containing:
      - id
      - text (question text)
      - main_concept
      - concepts (list)
      - score (retrieval score)
    """
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    corpus_name = _get_corpus_name()

    retrieval_config = rag.RagRetrievalConfig(top_k=top_k)
    response = rag.retrieval_query(
        rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
        text=query,
        rag_retrieval_config=retrieval_config,
    )

    contexts_obj = response.contexts
    contexts = getattr(contexts_obj, "contexts", contexts_obj)

    hits: List[QuestionHit] = []
    for ctx in contexts:
        raw_text = getattr(ctx, "text", "") or ""
        score = float(getattr(ctx, "score", 0.0))

        parsed = _parse_block(raw_text)
        hits.append(
            QuestionHit(    
                id=parsed["id"],
                text=parsed["text"],
                main_concept=parsed["main_concept"],
                concepts=parsed["concepts"],
                score=score,
            )
        )

    return hits


from typing import List, Optional

# ... existing imports and code (including QuestionHit and search_questions) ...


def search_questions_by_concept(concept: str, top_k: int = 5) -> List[QuestionHit]:
    """
    Search questions that are tagged with a given concept.

    Strategy:
    - First, use the concept text as a normal RAG query.
    - Then, filter results where the concept appears in main_concept or concepts list.
    """
    # Ask RAG for a bit more than we need, then filter down
    raw_hits: List[QuestionHit] = search_questions(query=concept, top_k=top_k * 3)

    target = concept.strip().lower()
    filtered: List[QuestionHit] = []
    for h in raw_hits:
        concepts_lower = [c.lower() for c in (h.concepts or [])]
        main_lower = (h.main_concept or "").lower()
        if target == main_lower or target in concepts_lower:
            filtered.append(h)

    # Fallback: if filtering removed everything, just return the raw hits
    return (filtered or raw_hits)[:top_k]


def get_question_by_id(question_id: str) -> Optional[QuestionHit]:
    """
    Try to retrieve a single question by its ID (e.g. 'q_001').

    Strategy:
    - Query RAG using the ID string.
    - Look for an exact ID match in the parsed hits.
    """
    qid = question_id.strip().lower()

    # Ask RAG for a small batch
    hits: List[QuestionHit] = search_questions(query=question_id, top_k=10)
    for h in hits:
        if (h.id or "").strip().lower() == qid:
            return h

    return None
