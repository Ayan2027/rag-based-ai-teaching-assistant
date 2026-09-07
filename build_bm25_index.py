import joblib
import re
from rank_bm25 import BM25Okapi


def tokenize(text):
    return re.findall(r"\w+", text.lower())


metadata_df = joblib.load("metadata.joblib")

print(f"Loaded {len(metadata_df)} chunks")

tokenized_corpus = [tokenize(text) for text in metadata_df["text"].tolist()]

bm25 = BM25Okapi(tokenized_corpus)

joblib.dump(bm25, "bm25_index.joblib")

print("BM25 index saved to bm25_index.joblib")