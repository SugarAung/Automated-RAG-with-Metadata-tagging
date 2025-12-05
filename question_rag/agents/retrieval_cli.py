# question_rag/agents/retrieval_cli.py

from __future__ import annotations

from question_rag.agents.retrieval_tools import search_questions


def main() -> None:
    print("=== Question RAG Retrieval CLI ===")
    query = input("Enter a search query (e.g. 'strategic risks SSBR'): ").strip()
    if not query:
        print("No query entered, exiting.")
        return

    try:
        top_k = int(input("How many results? (default 5): ").strip() or "5")
    except ValueError:
        top_k = 5

    print("\nSearching RAG corpus...\n")
    hits = search_questions(query=query, top_k=top_k)

    if not hits:
        print("No results found.")
        return

    for i, h in enumerate(hits, start=1):
        concepts_str = ", ".join(h.concepts) if h.concepts else "(none)"
        print(f"---- Result {i} ----")
        print(f"ID          : {h.id}")
        print(f"Main concept: {h.main_concept}")
        print(f"Concepts    : {concepts_str}")
        print(f"Score       : {h.score}")
        print("\nQuestion text:")
        print(h.text)
        print("-" * 20 + "\n")


if __name__ == "__main__":
    main()
