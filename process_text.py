import os
import json
from pypdf import PdfReader


# ============================================================
# Word-based chunking with overlap (works for any plain text)
# ============================================================

def chunk_text(text, chunk_size=200, overlap=50):
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = end - overlap  # move forward with overlap

    return chunks


# ============================================================
# Extract text from a PDF, page by page (so we keep page numbers)
# ============================================================

def extract_pdf_pages(path):
    reader = PdfReader(path)
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append({"page": i + 1, "text": text})

    return pages


# ============================================================
# Process every file in documents/
# ============================================================

documents = os.listdir("documents")

for doc in documents:

    path = f"documents/{doc}"
    number, ext = os.path.splitext(doc)
    ext = ext.lower()

    all_chunks = []
    full_text_parts = []

    print(f"\nProcessing: {doc}")

    if ext == ".pdf":
        pages = extract_pdf_pages(path)

        for page_info in pages:
            page_chunks = chunk_text(page_info["text"])

            for c in page_chunks:
                all_chunks.append({
                    "source_type": "document",
                    "number": number,
                    "title": doc,
                    "start": None,
                    "end": None,
                    "page": page_info["page"],
                    "text": c
                })

            full_text_parts.append(page_info["text"])

    elif ext == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        text_chunks = chunk_text(text)

        for c in text_chunks:
            all_chunks.append({
                "source_type": "document",
                "number": number,
                "title": doc,
                "start": None,
                "end": None,
                "page": None,
                "text": c
            })

        full_text_parts.append(text)

    else:
        print(f"Skipping unsupported file: {doc}")
        continue

    chunks_with_metadata = {
        "chunks": all_chunks,
        "text": " ".join(full_text_parts)
    }

    with open(f"jsons/{doc}.json", "w", encoding="utf-8") as f:
        json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=4)

    print(f"Completed: {doc}")
    print(f"Total chunks: {len(all_chunks)}")