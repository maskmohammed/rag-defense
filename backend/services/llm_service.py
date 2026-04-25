import json
import urllib.request
import urllib.error

from app.config import (
    LLM_ENABLED,
    LLM_PROVIDER,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TIMEOUT_SECONDS
)


class LLMService:
    def __init__(self):
        self.enabled = LLM_ENABLED
        self.provider = LLM_PROVIDER
        self.base_url = LLM_BASE_URL.rstrip("/")
        self.model = LLM_MODEL
        self.timeout = LLM_TIMEOUT_SECONDS

    def is_enabled(self) -> bool:
        return self.enabled and self.provider == "ollama"

    def generate_answer(self, question: str, context: str) -> str:
        if not self.is_enabled():
            raise ValueError("LLM désactivé")

        prompt = self._build_prompt(question, context)
        return self._call_ollama_chat(prompt)

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""
        Tu es un assistant expert.

        Ta tâche est de transformer le texte en réponse claire.

        INTERDICTIONS STRICTES :
        - Ne copie PAS les phrases du contexte
        - Ne commence PAS par "Selon les documents"
        - Ne fais PAS de copier-coller

        OBLIGATIONS :
        - Reformule entièrement
        - Simplifie
        - Structure

        FORMAT IMPOSÉ :

        Si c'est des règles :
        Réponds EXACTEMENT comme ceci :

        Principales règles :
        - ...
        - ...
        - ...

        Si c'est une procédure :
        Réponds EXACTEMENT comme ceci :

        Étapes :
        1. ...
        2. ...
        3. ...

        Sinon :
        Réponds en 3 phrases maximum.

        IMPORTANT :
        Même si le contexte est long, ta réponse doit être courte.

        Contexte :
        {context}

        Question :
        {question}

        Réponse :
        """.strip()

    def _call_ollama_chat(self, prompt: str) -> str:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "stream": False,
            "options": {
                "temperature": 0.2
            },
            "messages": [
                {
                    "role": "system",
                    "content": "Tu réponds uniquement à partir du contexte fourni, sans invention."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_data = json.loads(response.read().decode("utf-8"))

                message = response_data.get("message", {})
                content = message.get("content", "").strip()

                if not content:
                    raise ValueError("Réponse vide du LLM")

                return content

        except urllib.error.URLError as e:
            raise ValueError(f"LLM local indisponible : {str(e)}")
        except Exception as e:
            raise ValueError(f"Erreur LLM : {str(e)}")