import os
import httpx

def generate_sql(question: str, schema_context: str | None = None) -> str:
    base = os.getenv("VLLM_BASE_URL", "http://localhost:8001").rstrip("/")
    model = os.getenv("VLLM_MODEL")
    api_key = os.getenv("VLLM_API_KEY", "EMPTY")

    if not model:
        raise RuntimeError("VLLM_MODEL is not set")

    system = (
        "You are an NL-to-SQL assistant for PostgreSQL.\n"
        "Return ONLY one SQL query.\n"
        "Rules:\n"
        "- READ-ONLY ONLY (SELECT/WITH)\n"
        "- Use ONLY tables/columns from the schema below\n"
        "- Prefer explicit joins using keys\n"
        "- Always include a LIMIT (<= 50) unless the user asks for an aggregate count\n"
        "- No markdown, no explanations\n"
    )

    schema_block = f"\n\n{schema_context}\n" if schema_context else ""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system + schema_block},
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

    sql = data["choices"][0]["message"]["content"].strip()
    if not sql:
        raise RuntimeError("vLLM returned empty response")
    return sql
