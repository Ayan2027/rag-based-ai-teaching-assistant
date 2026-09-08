import requests
import os
import json
import pandas as pd
import joblib


# --------------------------------------------------
# Create embeddings using Ollama
# --------------------------------------------------

def create_embedding(text_list):

    response = requests.post(
        "http://localhost:11434/api/embed",
        json={
            "model": "bge-m3",
            "input": text_list
        }
    )

    if response.status_code != 200:
        print("Ollama Error:")
        print(response.text)
        response.raise_for_status()

    return response.json()["embeddings"]


# --------------------------------------------------
# Read all JSON files
# --------------------------------------------------

json_files = os.listdir("jsons")

my_dicts = []

chunk_id = 0

# Send only 20 chunks to Ollama at a time
BATCH_SIZE = 20


# --------------------------------------------------
# Process every JSON file
# --------------------------------------------------

for json_file in json_files:

    if not json_file.endswith(".json"):
        continue

    # Open JSON file
    with open(
        f"jsons/{json_file}",
        "r",
        encoding="utf-8"
    ) as f:

        content = json.load(f)

    print(f"\nCreating embeddings for {json_file}")

    chunks = content["chunks"]

    print(f"Total chunks: {len(chunks)}")


    # --------------------------------------------------
    # Create embeddings in batches
    # --------------------------------------------------

    for start in range(0, len(chunks), BATCH_SIZE):

        end = min(start + BATCH_SIZE, len(chunks))

        batch_chunks = chunks[start:end]

        # Extract only text
        text_list = [
            chunk["text"]
            for chunk in batch_chunks
        ]

        print(
            f"Embedding chunks {start + 1} - {end}"
        )

        # Create embeddings
        embeddings = create_embedding(text_list)


        # --------------------------------------------------
        # Add embedding + chunk ID
        # --------------------------------------------------

        for i, chunk in enumerate(batch_chunks):

            chunk["chunk_id"] = chunk_id

            chunk["embedding"] = embeddings[i]

            chunk_id += 1

            my_dicts.append(chunk)


# --------------------------------------------------
# Convert chunks into DataFrame
# --------------------------------------------------

df = pd.DataFrame.from_records(my_dicts)


# --------------------------------------------------
# Save DataFrame permanently
# --------------------------------------------------

joblib.dump(df, "embeddings.joblib")


# --------------------------------------------------
# Final information
# --------------------------------------------------

print("\n======================================")
print("All embeddings created successfully!")
print("======================================")

print(f"Total chunks: {len(df)}")

print("\nColumns:")
print(df.columns.tolist())

print("\nEmbeddings saved to:")
print("embeddings.joblib")