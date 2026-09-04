import whisper
import json
import os

model = whisper.load_model("small")

audios = os.listdir("audios")

for audio in audios:

    if "_" in audio:

        number = audio.split("_")[0]
        title = audio.split("_", 1)[1][:-4]

        print(f"\nProcessing: {number} - {title}")

        result = model.transcribe(
            audio=f"audios/{audio}",
            language="hi",
            task="translate",
            word_timestamps=False,
            fp16=False
        )

        chunks = []

        for segment in result["segments"]:
            chunks.append({
                "source_type": "video",
                "number": number,
                "title": title,
                "start": segment["start"],
                "end": segment["end"],
                "page": None,
                "text": segment["text"].strip()
            })

        chunks_with_metadata = {
            "chunks": chunks,
            "text": result["text"]
        }

        with open(f"jsons/{audio}.json", "w", encoding="utf-8") as f:
            json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=4)

        print(f"Completed: {audio}")
        print(f"Total chunks: {len(chunks)}")