# rag_retrieval_test.py

import vertexai
from vertexai import rag

from config import PROJECT_ID, LOCATION, CORPUS_NAME


def test_retrieval(query: str):
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    rag_corpus_name = (
        f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{CORPUS_NAME}"
    )

    print("Using RAG corpus:", rag_corpus_name)

    retrieval_config = rag.RagRetrievalConfig(
        top_k=3,
    )

    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=rag_corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=retrieval_config,
    )

    print("🔎 Retrieval results:")

    # 👉 The actual list is here:
    contexts = response.contexts.contexts

    if not contexts:
        print("No contexts returned.")
        return

    for i, ctx in enumerate(contexts, start=1):
        print(f"\n---- Context {i} ----")
        # ctx.text is the chunk text
        print(ctx.text[:1000])  # show first 1000 chars
        print("--------------------")


if __name__ == "__main__":
    test_retrieval("[TEST UPDATE 1]")
