import re
import numpy as np
import joblib
import faiss
import requests
from sentence_transformers import CrossEncoder


# ============================================================
# Embedding (Ollama, unchanged)
# ============================================================

def create_embedding(text_list):
    response = requests.post(
        "http://localhost:11434/api/embed",
        json={"model": "bge-m3", "input": text_list}
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def tokenize(text):
    return re.findall(r"\w+", text.lower())


# ============================================================
# Lazy-loaded singletons (load once, reuse across calls)
# ============================================================

_index = None
_metadata_df = None
_bm25 = None
_reranker = None


def _load_all():
    global _index, _metadata_df, _bm25, _reranker

    if _index is None:
        _index = faiss.read_index("faiss_index.bin")
        _metadata_df = joblib.load("metadata.joblib")
        _bm25 = joblib.load("bm25_index.joblib")
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    return _index, _metadata_df, _bm25, _reranker


# ============================================================
# Reciprocal Rank Fusion — merges dense + sparse rankings
# ============================================================

def reciprocal_rank_fusion(dense_ranks, bm25_ranks, k=60):
    scores = {}

    for rank, idx in enumerate(dense_ranks):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)

    for rank, idx in enumerate(bm25_ranks):
        scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)

    return scores


# ============================================================
# Hybrid search: FAISS (dense) + BM25 (sparse) -> fuse -> rerank
# ============================================================

def hybrid_search(query, top_k_candidates=20, top_k_final=5, use_rerank=True):

    index, metadata_df, bm25, reranker = _load_all()

    # ---- Dense retrieval ----
    query_embedding = np.array(create_embedding([query]), dtype="float32")
    faiss.normalize_L2(query_embedding)

    _, dense_indices = index.search(query_embedding, top_k_candidates)
    dense_indices = dense_indices.flatten().tolist()

    # ---- Sparse retrieval ----
    bm25_scores = bm25.get_scores(tokenize(query))
    bm25_indices = np.argsort(bm25_scores)[::-1][:top_k_candidates].tolist()

    # ---- Fuse ----
    fused_scores = reciprocal_rank_fusion(dense_indices, bm25_indices)
    fused_sorted = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    candidate_indices = [idx for idx, _ in fused_sorted[:top_k_candidates]]

    candidates_df = metadata_df.iloc[candidate_indices].copy()

    # ---- Rerank with cross-encoder ----
    if use_rerank:
        pairs = [[query, text] for text in candidates_df["text"].tolist()]
        rerank_scores = reranker.predict(pairs)
        candidates_df["rerank_score"] = rerank_scores
        candidates_df = candidates_df.sort_values("rerank_score", ascending=False)

    return candidates_df.head(top_k_final)