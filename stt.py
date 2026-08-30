import whisper
import json

# Load Whisper model
model = whisper.load_model("small")

# Transcribe audio
result = model.transcribe(
    audio="audios/6_SEO and Core Web Vitals in HTML.mp3",
    language="hi",
    task="translate",
    word_timestamps=False,
    fp16=False
)

# Create chunks with timestamps
chunks = []

for segment in result["segments"]:
    chunks.append({
        "start": segment["start"],
        "end": segment["end"],
        "text": segment["text"].strip()
    })

# Save chunks to JSON
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=4)

print(f"Transcription completed!")
print(f"Total chunks: {len(chunks)}")
print("Saved to: output.json")