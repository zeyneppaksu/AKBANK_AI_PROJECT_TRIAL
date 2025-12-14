# backend/app/llm/ollama.py
import os
import httpx


def generate_sql(question: str) -> str:
    """
    Calls Ollama chat API and expects SQL back.
    Environment:
      OLLAMA_BASE_URL (default http://localhost:11434)
      OLLAMA_MODEL (default qwen2.5:7b-instruct)  <-- change later
    """
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

    system = (
        "You are an NL-to-SQL assistant. "
        "Return ONLY a single SQL query (read-only). "
        "No explanations, no markdown fences."
    )

    # keep this minimal; you'll improve prompt/schema injection later
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }

    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()

    # Ollama returns message content here:
    sql = (data.get("message") or {}).get("content", "")
    sql = (sql or "").strip()

    if not sql:
        raise RuntimeError("Ollama returned empty response")

    return sql
