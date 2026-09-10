import sys
import json
import requests
import joblib

from retrieval import hybrid_search


# ============================================================
# Load Query Classification Model
# ============================================================

classifier = joblib.load("query_classifier.joblib")


# ============================================================
# Ollama Llama 3.2 Inference
# ============================================================

def inference(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Answer Question
# ============================================================

def answer_question(question):

    # ========================================================
    # Query Classification
    # ========================================================

    category = classifier.predict([question])[0]

    # Print to terminal for testing/debugging.
    # stderr is used so it does not interfere with JSON output.
    print(
        f"Predicted category: {category}",
        file=sys.stderr
    )

    # ========================================================
    # Hybrid Search + Reranking
    # ========================================================

    results = hybrid_search(
        question,
        top_k_candidates=20,
        top_k_final=5
    )

    # ========================================================
    # Prepare retrieved chunks for Llama
    # ========================================================

    context_chunks = []

    for _, row in results.iterrows():

        if row["source_type"] == "video":

            context_chunks.append({
                "source_type": "video",
                "title": row["title"],
                "number": row["number"],
                "start": row["start"],
                "end": row["end"],
                "text": row["text"]
            })

        else:

            context_chunks.append({
                "source_type": "document",
                "title": row["title"],
                "number": row["number"],
                "page": row["page"],
                "text": row["text"]
            })

    context = json.dumps(
        context_chunks,
        ensure_ascii=False,
        indent=2
    )

    # ========================================================
    # Prompt
    # ========================================================

    prompt = f"""
You are an AI teaching assistant for a web development course.

The knowledge base contains two kinds of sources:
1. Video chunks — video title, video number, start/end timestamp in seconds.
2. Document chunks — document title, page number.

Retrieved chunks:
{context}

User's question:
"{question}"

Instructions:
1. Answer using only the retrieved chunks.
2. Explain clearly and in a human-friendly way.
3. For VIDEO chunks, mention video number, title, and timestamp (minutes/seconds).
4. For DOCUMENT chunks, mention title and page number. Never invent a timestamp.
5. If multiple sources are relevant, mention all, labeled by type.
6. Do not mention embeddings, cosine similarity, FAISS, JSON, or internal implementation.
7. Do not invent information not in the retrieved chunks.
8. If unrelated to the knowledge base, say so politely.
"""

    # ========================================================
    # Generate Answer using Ollama Llama 3.2
    # ========================================================

    response = inference(prompt)

    return response["response"]


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    question = sys.argv[1]

    answer = answer_question(question)

    print(
        json.dumps(
            {"answer": answer},
            ensure_ascii=False
        )
    )