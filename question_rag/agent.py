# question_rag/agent.py

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from question_rag.agents.retrieval_tools import (
    search_questions,
    search_questions_by_concept,
    get_question_by_id,
    QuestionHit,
)

# ---------- System prompt ----------

SYSTEM_PROMPT_PATH = Path(__file__).parent / "agents" / "retrieval_agent_system_prompt.txt"
SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


# ---------- Tool functions (plain Python) ----------

def retrieve_exam_questions(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search the exam-question RAG corpus using a free-text query.

    Args:
        query: What the teacher types, e.g. "strategic risks SSBR".
        top_k: Maximum number of hits to return.

    Returns:
        A list of dicts with: id, text, main_concept, concepts, score.
    """
    hits: List[QuestionHit] = search_questions(query=query, top_k=top_k)
    return [
        {
            "id": h.id,
            "text": h.text,
            "main_concept": h.main_concept,
            "concepts": h.concepts,
            "score": h.score,
        }
        for h in hits
    ]


def retrieve_questions_by_concept(concept: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve questions that are tagged with the given concept name.
    """
    hits: List[QuestionHit] = search_questions_by_concept(concept=concept, top_k=top_k)
    return [
        {
            "id": h.id,
            "text": h.text,
            "main_concept": h.main_concept,
            "concepts": h.concepts,
            "score": h.score,
        }
        for h in hits
    ]


def retrieve_question_by_id(question_id: str) -> Dict[str, Any] | None:
    """
    Retrieve a single question by its ID (e.g. "q_001").
    """
    hit = get_question_by_id(question_id)
    if not hit:
        return None

    return {
        "id": hit.id,
        "text": hit.text,
        "main_concept": hit.main_concept,
        "concepts": hit.concepts,
        "score": hit.score,
    }

# ---------- Wrap them as ADK tools (very old ADK API: only function) ----------

retrieve_exam_questions_tool = FunctionTool(retrieve_exam_questions)
retrieve_questions_by_concept_tool = FunctionTool(retrieve_questions_by_concept)
retrieve_question_by_id_tool = FunctionTool(retrieve_question_by_id)



# ---------- Root agent ADK will load ----------

root_agent = Agent(
    name="question_rag",          # must match the app name in ADK dropdown
    model="gemini-2.5-pro",
    instruction=SYSTEM_PROMPT,
    tools=[
        retrieve_exam_questions_tool,
        retrieve_questions_by_concept_tool,
        retrieve_question_by_id_tool,
    ],
)
