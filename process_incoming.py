import numpy as np
import joblib
import requests
import json
import faiss


# ============================================================
# 1. Create embedding using Ollama + bge-m3
# ============================================================

def create_embedding(text_list):

    response = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )

    if response.status_code != 200:
        print("Ollama Embedding Error:")
        print(response.text)
        response.raise_for_status()

    return response.json()["embeddings"]


# ============================================================
# 2. Generate answer using Ollama + llama3.2
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

    if response.status_code != 200:
        print("Ollama LLM Error:")
        print(response.text)
        response.raise_for_status()

    return response.json()


# ============================================================
# 3. Load FAISS index + metadata (instead of the raw joblib df)
# ============================================================

index = faiss.read_index("faiss_index.bin")
metadata_df = joblib.load("metadata.joblib")

print(f"Loaded FAISS index with {index.ntotal} chunks")


# ============================================================
# 4. Ask the user a question
# ============================================================

incoming_query = input("\nAsk a Question: ")


# ============================================================
# 5. Create embedding for user's question
# ============================================================

question_embedding = np.array(
    create_embedding([incoming_query]),
    dtype="float32"
)

faiss.normalize_L2(question_embedding)


# ============================================================
# 6. Search FAISS index for top 5 matches
# ============================================================

top_results = 5

similarities, indices = index.search(question_embedding, top_results)

similarities = similarities.flatten()
indices = indices.flatten()

new_df = metadata_df.iloc[indices].copy()
new_df["similarity"] = similarities


# ============================================================
# 7. Prepare context for the LLM (source-aware)
# ============================================================

context_chunks = []

for _, row in new_df.iterrows():

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

context = json.dumps(context_chunks, ensure_ascii=False, indent=2)


# ============================================================
# 8. Create prompt (source-aware)
# ============================================================

prompt = f"""
You are an AI teaching assistant for a web development course.

The knowledge base contains two kinds of sources:
1. Video chunks — each has a video title, video number, and a
   start/end timestamp in seconds.
2. Document chunks — each has a document title and a page number.

Below are the most relevant chunks retrieved for the user's question.

Retrieved chunks:

{context}

--------------------------------------------------

User's question:
"{incoming_query}"

--------------------------------------------------

Instructions:

1. Answer the user's question using only the retrieved chunks.
2. Explain the answer in a clear and human-friendly way.
3. If the answer comes from a VIDEO chunk, mention the video number,
   video title, and the approximate timestamp in minutes and seconds.
4. If the answer comes from a DOCUMENT chunk, mention the document
   title and the page number. Do NOT invent a timestamp for document
   chunks.
5. If multiple sources are relevant, mention all of them clearly,
   labeled by type.
6. Do not mention embeddings, cosine similarity, FAISS, JSON,
   retrieval, DataFrame, or the internal implementation.
7. Do not invent information that is not supported by the retrieved
   chunks.
8. If the question is unrelated to the knowledge base, politely say
   so.
"""


# ============================================================
# 9. Save prompt for debugging
# ============================================================

with open("prompt.txt", "w", encoding="utf-8") as f:
    f.write(prompt)


# ============================================================
# 10. Ask Llama to generate the final answer
# ============================================================

response = inference(prompt)
answer = response["response"]


# ============================================================
# 11. Display + save the answer
# ============================================================

print("\n======================================")
print("Answer")
print("======================================")
print(answer)

with open("response.txt", "w", encoding="utf-8") as f:
    f.write(answer)