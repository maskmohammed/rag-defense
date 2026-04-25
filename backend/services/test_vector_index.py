from services.vector_index_service import build_vector_index, search_similar_chunks


def main():
    result = build_vector_index()

    print("Index construit avec succès")
    print(result)

    print("\nRecherche test :")
    results = search_similar_chunks("gestion des ressources logistiques", top_k=5)

    for i, item in enumerate(results, start=1):
        meta = item["metadata"]
        print(f"\nRésultat {i}")
        print(f"Score      : {item['score']:.4f}")
        print(f"Document   : {meta['filename']}")
        print(f"Chunk index: {meta['chunk_index']}")
        print(f"Texte      : {meta['text'][:200]}...")


if __name__ == "__main__":
    main()