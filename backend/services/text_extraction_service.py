from pathlib import Path
from docx import Document
from pypdf import PdfReader


def extract_text_from_txt(file_path: str) -> str:
    path = Path(file_path)

    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        raise ValueError("Erreur lors de l'extraction du texte du fichier TXT")


def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        raise ValueError("Erreur lors de l'extraction du texte du fichier DOCX")


def extract_text_from_pdf(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        pages_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text.strip())

        return "\n".join(pages_text)
    except Exception:
        raise ValueError("Erreur lors de l'extraction du texte du fichier PDF")


def extract_text(file_path: str) -> str:
    """
    Détecte automatiquement le type de fichier et extrait le texte.
    """
    suffix = Path(file_path).suffix.lower()

    if suffix == ".txt":
        text = extract_text_from_txt(file_path)
    elif suffix == ".docx":
        text = extract_text_from_docx(file_path)
    elif suffix == ".pdf":
        text = extract_text_from_pdf(file_path)
    else:
        raise ValueError("Format de fichier non supporté pour l'extraction")

    if not text or not text.strip():
        raise ValueError("Le document est vide ou illisible après extraction")

    return text