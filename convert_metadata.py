import joblib
import json

# Load metadata
metadata_df = joblib.load("metadata.joblib")

print(f"Loaded {len(metadata_df)} chunks")

# Convert DataFrame to JSON
metadata_df.to_json(
    "metadata.json",
    orient="records",
    force_ascii=False,
    indent=2
)

print("Saved metadata.json successfully!")