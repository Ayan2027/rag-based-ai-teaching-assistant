import joblib
import numpy as np
import faiss


# ============================================================
# 1. Load existing embeddings
# ============================================================

df = joblib.load("embeddings.joblib")

print(f"Loaded {len(df)} chunks")


# ============================================================
# 2. Stack embeddings into a matrix
# ============================================================

embeddings = np.vstack(df["embedding"].values).astype("float32")

dimension = embeddings.shape[1]

print(f"Embedding dimension: {dimension}")


# ============================================================
# 3. Normalize embeddings (so inner product = cosine similarity)
# ============================================================

faiss.normalize_L2(embeddings)


# ============================================================
# 4. Build a FAISS index (flat = exact search, good up to
#    millions of vectors at this dimension size)
# ============================================================

index = faiss.IndexFlatIP(dimension)  # IP = inner product
index.add(embeddings)

print(f"FAISS index built with {index.ntotal} vectors")


# ============================================================
# 5. Save the index and the metadata (everything except the
#    raw embedding column, which now lives inside the index)
# ============================================================

faiss.write_index(index, "faiss_index.bin")

metadata_df = df.drop(columns=["embedding"])
joblib.dump(metadata_df, "metadata.joblib")

print("Saved: faiss_index.bin, metadata.joblib")