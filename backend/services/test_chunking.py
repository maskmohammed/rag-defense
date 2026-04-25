from pathlib import Path
from services.text_extraction_service import extract_text
from services.text_cleaning_service import clean_text
from services.chunking_service import chunk_text


BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "data" / "docs" / "demo"


def test_chunking(filename: str):
    file_path = DOCS_DIR / filename

    raw_text = extract_text(str(file_path))
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text, chunk_size=120, overlap=20)

    print(f"Fichier : {filename}")
    print(f"Nombre total de chunks : {len(chunks)}")
    print("=" * 60)

    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index']}")
        print("-" * 40)
        print(chunk["text"][:500])
        print("\n" + "=" * 60)


if __name__ == "__main__":
    test_chunking("PROCEDURE_Operationnelle_01.docx")