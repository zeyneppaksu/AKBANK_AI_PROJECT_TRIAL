# backend/app/llm/gemini.py
import os
import re
from google import genai
from google.genai import types
from .rules import BASE_RULES, build_domain_rules

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _client

def _extract_sql(text: str) -> str:
    text = (text or "").strip()

    m = re.search(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        text = m.group(1).strip()

    m = re.search(r"\b(SELECT|WITH)\b.*", text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    sql = m.group(0).strip()

    # first statement only
    if ";" in sql:
        sql = sql.split(";", 1)[0].strip() + ";"
    elif not sql.endswith(";"):
        sql += ";"
    return sql

def _apply_limit(sql: str, question: str, default_limit: int = 50) -> str:
    s = sql.strip().rstrip(";")

    # top N => LIMIT N
    m = re.search(r"\btop\s+(\d+)\b", question, flags=re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if re.search(r"\bLIMIT\s+\d+\b", s, flags=re.IGNORECASE):
            s = re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {n}", s, flags=re.IGNORECASE)
        else:
            s = f"{s} LIMIT {n}"
        return s + ";"

    # default LIMIT
    if not re.search(r"\bLIMIT\b", s, flags=re.IGNORECASE):
        s = f"{s} LIMIT {default_limit}"
    return s + ";"

def generate_sql(question: str, schema_text: str) -> str:
    client = _get_client()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Build dynamic system prompt
    domain = build_domain_rules(question)
    system = BASE_RULES + ("\n\n" + domain if domain else "")

    user_prompt = (
        f"SCHEMA:\n{schema_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"Return ONLY SQL."
    )

    resp = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
        ),
    )

    text = getattr(resp, "text", "") or ""
    sql = _extract_sql(text)
    if not sql:
        raise ValueError(f"Gemini did not return SQL. Raw: {text[:300]}")
    return _apply_limit(sql, question)
