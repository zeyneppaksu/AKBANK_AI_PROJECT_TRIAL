import os
import httpx

def generate_sql(question: str, schema_context: str | None = None) -> str:
    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")

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
        "stream": False,
    }

    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}/api/chat", json=payload)
        r.raise_for_status()
        data = r.json()

    sql = (data.get("message") or {}).get("content", "")
    sql = (sql or "").strip()
    if not sql:
        raise RuntimeError("Ollama returned empty response")
    return sql
