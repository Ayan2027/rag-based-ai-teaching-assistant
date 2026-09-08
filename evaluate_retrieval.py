import json
import numpy as np
import faiss
from retrieval import hybrid_search, create_embedding, _load_all


def dense_only_search(query, top_k=5):
    index, metadata_df, _, _ = _load_all()
    q_emb = np.array(create_embedding([query]), dtype="float32")
    faiss.normalize_L2(q_emb)
    _, indices = index.search(q_emb, top_k)
    return metadata_df.iloc[indices.flatten()]


def evaluate(method_name, search_fn, eval_set, top_k=5):
    hits = 0
    reciprocal_ranks = []

    print(f"\n--- {method_name} ---")

    for item in eval_set:
        question = item["question"]
        expected = str(item["expected_number"])

        results = search_fn(question)
        retrieved_numbers = results["number"].astype(str).tolist()

        is_hit = expected in retrieved_numbers
        hits += is_hit

        rank = retrieved_numbers.index(expected) + 1 if is_hit else 0
        reciprocal_ranks.append(1 / rank if rank else 0)

        status = "HIT " if is_hit else "MISS"
        print(f"[{status}] \"{question}\" -> {retrieved_numbers}")

    hit_rate = hits / len(eval_set)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    print(f"Hit-Rate@{top_k}: {hits}/{len(eval_set)} = {hit_rate:.1%}")
    print(f"MRR@{top_k}: {mrr:.3f}")

    return hit_rate, mrr


with open("eval_questions.json", "r", encoding="utf-8") as f:
    eval_set = json.load(f)

baseline_hit, baseline_mrr = evaluate("Dense-only (FAISS)", dense_only_search, eval_set)
hybrid_hit, hybrid_mrr = evaluate(
    "Hybrid Search + Rerank",
    lambda q: hybrid_search(q, top_k_final=5),
    eval_set
)

print("\n======================================")
print("Comparison")
print("======================================")
print(f"Dense-only    : Hit-Rate={baseline_hit:.1%}, MRR={baseline_mrr:.3f}")
print(f"Hybrid+Rerank : Hit-Rate={hybrid_hit:.1%}, MRR={hybrid_mrr:.3f}")