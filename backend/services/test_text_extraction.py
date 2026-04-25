from pathlib import Path
from services.text_extraction_service import extract_text


BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "data" / "docs" / "demo"


def test_extraction(filename: str):
    file_path = DOCS_DIR / filename

    print(f"Test extraction : {file_path}")
    print("-" * 50)

    text = extract_text(str(file_path))

    if text.strip():
        print("Extraction réussie")
        print("-" * 50)
        print(text[:1000])  #1000 char
    else:
        print("Aucun texte extrait")


if __name__ == "__main__":
    # Change ce nom pour tester plusieurs fichiers
    test_extraction("GUIDE_Securite_Informatique_01.pdf")