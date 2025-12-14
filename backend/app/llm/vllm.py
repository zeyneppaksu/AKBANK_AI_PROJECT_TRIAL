# backend/app/llm/vllm.py
import os
import httpx


def generate_sql(question: str) -> str:
    """
    Calls a vLLM OpenAI-compatible server.
    Environment:
      VLLM_BASE_URL (default http://localhost:8001)
      VLLM_MODEL (required) e.g. "Qwen/Qwen3-8B" or whatever you serve
      VLLM_API_KEY (optional; default "EMPTY")
    """
    base = os.getenv("VLLM_BASE_URL", "http://localhost:8001").rstrip("/")
    model = os.getenv("VLLM_MODEL")
    api_key = os.getenv("VLLM_API_KEY", "EMPTY")

    if not model:
        raise RuntimeError("VLLM_MODEL is not set")

    system = (
        "You are an NL-to-SQL assistant. "
        "Return ONLY a single SQL query (read-only). "
        "No explanations, no markdown fences."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        "temperature": 0.0,
        "max_tokens": 256,
    }

    headers = {"Authorization": f"Bearer {api_key}"}

    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}/v1/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

    try:
        sql = data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Unexpected vLLM response format: {e}")

    if not sql:
        raise RuntimeError("vLLM returned empty response")

    return sql
