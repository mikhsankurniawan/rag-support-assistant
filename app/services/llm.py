import httpx
from openai import OpenAI

from app.config import settings


SYSTEM_PROMPT = """You are a careful customer support knowledge assistant.
Answer only from the provided context.
If the context does not contain the answer, say you do not know from the available documents.
Keep the answer concise and practical.
Mention source numbers when useful, like [1] or [2].
"""


def build_prompt(question: str, context_blocks: list[str]) -> str:
    formatted_context = "\n\n".join(
        f"[Source {index + 1}]\n{block}" for index, block in enumerate(context_blocks)
    )
    return f"""{SYSTEM_PROMPT}

Context:
{formatted_context}

Question:
{question}

Answer:
"""


def generate_answer(question: str, context_blocks: list[str]) -> str:
    prompt = build_prompt(question, context_blocks)

    if settings.llm_provider.lower() == "openai":
        return _generate_with_openai(prompt)

    if settings.llm_provider.lower() == "ollama":
        return _generate_with_ollama(prompt)

    raise ValueError("Unsupported LLM_PROVIDER. Use 'ollama' or 'openai'.")


def _generate_with_ollama(prompt: str) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    try:
        response = httpx.post(url, json=payload, timeout=120)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "Failed to call Ollama. Make sure Ollama is running and the model is pulled."
        ) from exc

    data = response.json()
    return data.get("response", "").strip()


def _generate_with_openai(prompt: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=prompt,
        temperature=0.1,
    )
    return response.output_text.strip()
