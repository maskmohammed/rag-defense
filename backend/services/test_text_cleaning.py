from pathlib import Path
from services.text_extraction_service import extract_text
from services.text_cleaning_service import clean_text


BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = BASE_DIR / "data" / "docs" / "demo"


def test_cleaning(filename: str):
    file_path = DOCS_DIR / filename

    raw_text = extract_text(str(file_path))
    cleaned_text = clean_text(raw_text)

    print("Texte brut :")
    print("-" * 50)
    print(raw_text[:800])

    print("\n" + "=" * 50 + "\n")

    print("Texte nettoyé :")
    print("-" * 50)
    print(cleaned_text[:800])

    print("\n" + "=" * 50 + "\n")
    print("Longueur brute :", len(raw_text))
    print("Longueur nettoyée :", len(cleaned_text))


if __name__ == "__main__":
    test_cleaning("GUIDE_Securite_Informatique_01.pdf")