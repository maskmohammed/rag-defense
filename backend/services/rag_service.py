from services.vector_index_service import search_similar_chunks
from services.llm_service import LLMService


MIN_SCORE = 0.08
TOP_K = 5
MAX_EXCERPTS = 5
MAX_CONTEXT_ITEMS = 4


def normalize_text(text: str) -> str:
    if not text:
        return ""
    return " ".join(text.split()).strip()


def is_relevant_result(result: dict, min_score: float = MIN_SCORE) -> bool:
    return result.get("score", 0.0) >= min_score


def deduplicate_documents(results: list) -> list:
    seen = set()
    documents = []

    for item in results:
        meta = item["metadata"]
        filename = meta.get("filename", "Inconnu")

        if filename not in seen:
            seen.add(filename)
            documents.append(filename)

    return documents


def build_excerpts(results: list, max_excerpts: int = MAX_EXCERPTS) -> list:
    excerpts = []

    for item in results[:max_excerpts]:
        meta = item["metadata"]
        excerpt_text = normalize_text(meta.get("text", ""))

        excerpts.append({
            "document": meta.get("filename", "Inconnu"),
            "title": meta.get("title", "Inconnu"),
            "chunk_index": meta.get("chunk_index", -1),
            "score": round(item.get("score", 0.0), 4),
            "text": excerpt_text[:500]
        })

    return excerpts


def select_best_context_items(results: list, max_items: int = MAX_CONTEXT_ITEMS) -> list:
    cleaned = []

    for item in results:
        text = normalize_text(item["metadata"].get("text", ""))
        if not text:
            continue

        cleaned.append({
            "score": item.get("score", 0.0),
            "metadata": item["metadata"]
        })

    cleaned.sort(key=lambda x: x["score"], reverse=True)
    return cleaned[:max_items]


def build_context(results: list) -> str:
    selected = select_best_context_items(results)

    context_parts = []

    for item in selected:
        text = normalize_text(item["metadata"].get("text", ""))

        if text:
            context_parts.append(text)

    return "\n\n".join(context_parts)


def build_fallback_answer(results: list) -> str:
    if not results:
        return "Je ne peux pas répondre à partir des documents disponibles."

    best = results[0]
    best_text = normalize_text(best["metadata"].get("text", ""))

    if not best_text:
        return "Je ne peux pas répondre à partir des documents disponibles."

    answer = f"Selon les documents disponibles, {best_text}"

    if len(answer) > 900:
        answer = answer[:900].rsplit(" ", 1)[0] + "..."

    return answer

def detect_question_type(question: str) -> str:
    q = question.lower()

    if any(word in q for word in ["procédure", "étapes", "comment", "activation"]):
        return "procedure"

    if any(word in q for word in ["règles", "consignes", "sécurité", "communication"]):
        return "rules"

    if any(word in q for word in ["résume", "résumé", "synthèse"]):
        return "summary"

    return "generic"


def query_rag(question: str, top_k: int = TOP_K) -> dict:
    question = normalize_text(question)

    if not question:
        return {
            "status": "error",
            "message": "Question vide"
        }

    raw_results = search_similar_chunks(question, top_k=top_k)

    if raw_results and raw_results[0].get("score", 0.0) < MIN_SCORE:
        raw_results = []

    relevant_results = [item for item in raw_results if is_relevant_result(item)]

    question_type = detect_question_type(question)

    if not relevant_results:
        return {
            "status": "success",
            "question": question,
            "answer": "Je ne peux pas répondre à partir des documents disponibles.",
            "sources": [],
            "excerpts": [],
            "context": "",
            "top_k": top_k,
            "answer_mode": "none"
        }

    context = build_context(relevant_results)
    sources = deduplicate_documents(relevant_results)
    excerpts = build_excerpts(relevant_results, max_excerpts=MAX_EXCERPTS)

    llm_service = LLMService()

    try:
        typed_question = f"[TYPE={question_type}] {question}"

        answer = llm_service.generate_answer(
            question=typed_question,
            context=context
        )
        # khass tqad
        answer_mode = "llm_hybrid"

        if not answer or not answer.strip():
            raise ValueError("Réponse vide")

    except Exception as e:
        print("ERREUR LLM :", e)
        answer = build_fallback_answer(relevant_results)
        answer_mode = "extractive_fallback"

    return {
        "status": "success",
        "question": question,
        "answer": answer,
        "sources": sources,
        "excerpts": excerpts,
        "context": context,
        "top_k": top_k,
        "answer_mode": answer_mode,
        "question_type": question_type
    }