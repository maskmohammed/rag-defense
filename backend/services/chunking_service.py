def chunk_text(text: str, chunk_size: int = 120, overlap: int = 20):
    """
    Découpe un texte en chunks basés sur le nombre de mots.
    - chunk_size : nombre de mots par chunk
    - overlap : nombre de mots partagés entre deux chunks
    Retourne une liste de dictionnaires :
    [
        {"chunk_index": 0, "text": "..."},
        {"chunk_index": 1, "text": "..."}
    ]
    """
    if not text or not text.strip():
        return []

    words = text.split()

    if chunk_size <= 0:
        raise ValueError("chunk_size doit être > 0")

    if overlap < 0:
        raise ValueError("overlap doit être >= 0")

    if overlap >= chunk_size:
        raise ValueError("overlap doit être inférieur à chunk_size")

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text_value = " ".join(chunk_words).strip()

        if chunk_text_value:
            chunks.append({
                "chunk_index": chunk_index,
                "text": chunk_text_value
            })

        chunk_index += 1
        start += chunk_size - overlap

    return chunks