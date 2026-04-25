from pathlib import Path
from werkzeug.utils import secure_filename

from app.config import DOCS_DIR, ALLOWED_EXTENSIONS
from services.text_extraction_service import extract_text
from services.text_cleaning_service import clean_text
from services.chunking_service import chunk_text
from services.document_db_service import insert_document, insert_chunks, get_all_documents
from services.vector_index_service import build_vector_index


def is_allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def document_exists_in_db(filename: str) -> bool:
    documents = get_all_documents()
    for doc in documents:
        if doc["filename"] == filename:
            return True
    return False


def save_uploaded_file(file_storage):
    """
    Sauvegarde un fichier uploadé, l'ingère immédiatement dans la base
    et reconstruit l'index vectoriel.
    """
    if file_storage is None:
        raise ValueError("Aucun fichier fourni")

    filename = file_storage.filename

    if not filename or not filename.strip():
        raise ValueError("Nom de fichier invalide")

    if not is_allowed_file(filename):
        raise ValueError("Format non supporté")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    safe_filename = secure_filename(filename)

    if not safe_filename:
        raise ValueError("Nom de fichier invalide")

    file_path = DOCS_DIR / safe_filename

    if file_path.exists():
        raise ValueError("Un fichier avec ce nom existe déjà sur le disque")

    if document_exists_in_db(safe_filename):
        raise ValueError("Un document avec ce nom existe déjà dans la base")

    try:
        file_storage.save(file_path)

        raw_text = extract_text(str(file_path))

        cleaned_text = clean_text(raw_text)

        chunks = chunk_text(cleaned_text, chunk_size=120, overlap=20)

        if not chunks:
            raise ValueError("Aucun contenu exploitable dans le document")

        title = file_path.stem
        file_type = file_path.suffix.replace(".", "").upper()

        document_id = insert_document(
            title=title,
            filename=file_path.name,
            file_type=file_type
        )

        insert_chunks(document_id, chunks)

        build_vector_index()

        return {
            "filename": safe_filename,
            "file_path": str(file_path),
            "document_id": document_id,
            "chunks": len(chunks)
        }

    except Exception as e:
        # cas erreur
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass

        raise ValueError(f"Erreur lors du traitement du document: {str(e)}")