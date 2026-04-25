from pathlib import Path

from services.text_extraction_service import extract_text
from services.text_cleaning_service import clean_text
from services.chunking_service import chunk_text
from services.document_db_service import (
    insert_document,
    insert_chunks,
    get_all_documents,
    get_chunks_by_document_id
)


BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "data" / "docs" / "demo"


def get_existing_filenames():
    documents = get_all_documents()
    return {doc["filename"] for doc in documents}


def ingest_document(filename: str):
    file_path = DOCS_DIR / filename

    raw_text = extract_text(str(file_path))

    cleaned_text = clean_text(raw_text)

    chunks = chunk_text(cleaned_text, chunk_size=120, overlap=20)

    if not chunks:
        raise ValueError(f"Aucun chunk généré pour {filename}")

    title = file_path.stem
    file_type = file_path.suffix.replace(".", "").upper()

    document_id = insert_document(
        title=title,
        filename=file_path.name,
        file_type=file_type
    )

    # 6. Insertion chunks
    insert_chunks(document_id, chunks)

    return document_id, len(chunks)


def main():
    existing_filenames = get_existing_filenames()

    all_files = sorted([
        file_path.name
        for file_path in DOCS_DIR.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in {".txt", ".docx", ".pdf"}
    ])

    inserted_count = 0
    skipped_count = 0

    print("Début ingestion multiple...")
    print("=" * 60)

    for filename in all_files:
        if filename in existing_filenames:
            print(f"[SKIP] Déjà en base : {filename}")
            skipped_count += 1
            continue

        try:
            document_id, chunk_count = ingest_document(filename)
            inserted_count += 1
            print(f"[OK] {filename} | document_id={document_id} | chunks={chunk_count}")
        except Exception as e:
            print(f"[ERREUR] {filename} | {str(e)}")

    print("\n" + "=" * 60)
    print(f"Documents insérés : {inserted_count}")
    print(f"Documents ignorés : {skipped_count}")

    documents = get_all_documents()
    print(f"\nTotal documents en base : {len(documents)}")

    for doc in documents[:20]:
        print(f"- {doc['id']} | {doc['title']} | {doc['filename']} | {doc['file_type']}")


if __name__ == "__main__":
    main()