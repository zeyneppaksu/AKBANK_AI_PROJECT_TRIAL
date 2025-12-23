import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

_TOKENIZER = None
_MODEL = None
_DEVICE = None

SYSTEM_PROMPT = (
    "You are an expert NL-to-SQL assistant for PostgreSQL.\n"
    "Your task is to translate natural language questions into ONE valid SQL query.\n\n"

    "OUTPUT RULES (STRICT):\n"
    "- Output ONLY a single SQL query.\n"
    "- Do NOT include explanations, comments, markdown, or code fences.\n"
    "- The SQL MUST start with SELECT or WITH.\n"
    "- Read-only queries ONLY (SELECT/WITH).\n"
    "- NEVER use INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TRUNCATE.\n"
    "- Use ONLY table and column names that appear in the provided schema.\n"
    "- Do NOT invent column or table names.\n"
    "- If multiple statements are generated, keep ONLY the first.\n"
    "- End the query with a semicolon.\n"
    "- If the user does not specify a limit, add LIMIT 50.\n\n"

    "DATABASE SCHEMA RULES:\n"
    "- The customers table primary key is customers.customer_no.\n"
    "- The accounts table references customers via accounts.customer_no.\n"
    "- Customer name fields: customers.first_name, customers.last_name.\n"
    "- Account balance fields:\n"
    "  * accounts.balance (generic)\n"
    "  * accounts.balance_try (TRY)\n"
    "  * accounts.balance_usd (USD)\n"
    "  * accounts.balance_eur (EUR)\n"
    "- To compute a customer's total balance, SUM the relevant balance column over accounts.\n\n"

    "JOIN RULES:\n"
    "- When combining customers and accounts, JOIN ON accounts.customer_no = customers.customer_no.\n"
    "- Use explicit JOIN syntax (no implicit joins).\n\n"

    "ORDERING RULES:\n"
    "- When the question asks for top/highest/largest, ORDER BY the relevant value DESC.\n"
    "- When it asks for lowest/smallest, ORDER BY ASC.\n\n"

    "ERROR AVOIDANCE:\n"
    "- NEVER use customer_id (it does not exist).\n"
    "- NEVER guess column names.\n"
    "- If a concept is ambiguous, choose the most reasonable column from the schema.\n\n"

    "Your response MUST be executable PostgreSQL SQL and NOTHING ELSE."
)

def _load():
    global _TOKENIZER, _MODEL, _DEVICE
    if _MODEL is not None and _TOKENIZER is not None:
        return

    model_id = os.getenv("HF_MODEL", "Qwen/Qwen2.5-3B-Instruct")

    _TOKENIZER = AutoTokenizer.from_pretrained(model_id)

    _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if _DEVICE == "cuda" else torch.float32

    # NOTE: use dtype= (torch_dtype is deprecated in some stacks)
    _MODEL = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="auto" if _DEVICE == "cuda" else None,
    )

    if _DEVICE == "cpu":
        _MODEL.to(_DEVICE)

def _extract_sql(text: str) -> str:
    text = (text or "").strip()

    # strip ```sql fences if present
    m = re.search(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        text = m.group(1).strip()

    # take from first SELECT/WITH onward
    m = re.search(r"\b(SELECT|WITH)\b.*", text, flags=re.DOTALL | re.IGNORECASE)
    if not m:
        return ""  # signal failure
    text = m.group(0).strip()

    # first statement only
    if ";" in text:
        text = text.split(";", 1)[0].strip() + ";"

    return text

def _apply_limit(sql: str, question: str, default_limit: int = 50) -> str:
    s = sql.strip().rstrip(";")

    # If user says "top N" (top 5, top 10, etc.), force LIMIT N
    m = re.search(r"\btop\s+(\d+)\b", question, flags=re.IGNORECASE)
    if m:
        n = int(m.group(1))
        if re.search(r"\bLIMIT\s+\d+\b", s, flags=re.IGNORECASE):
            s = re.sub(r"\bLIMIT\s+\d+\b", f"LIMIT {n}", s, flags=re.IGNORECASE)
        else:
            s = f"{s} LIMIT {n}"
        return s + ";"

    # Otherwise ensure there's SOME limit
    if not re.search(r"\bLIMIT\b", s, flags=re.IGNORECASE):
        s = f"{s} LIMIT {default_limit}"
    return s + ";"

def _build_prompt(schema_text: str, question: str) -> str:
    user_content = (
        f"{SYSTEM_PROMPT}\n"
        f"SCHEMA:\n{schema_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"SQL:"
    )

    # Prefer chat template for Qwen instruct models (much cleaner generations)
    if hasattr(_TOKENIZER, "apply_chat_template"):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"SCHEMA:\n{schema_text}\n\nQUESTION:\n{question}\n\nReturn ONLY SQL."},
        ]
        return _TOKENIZER.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    return user_content

def generate_sql(question: str, schema_text: str) -> str:
    _load()
    print("Torch CUDA available:", torch.cuda.is_available())
    print("Model device:", next(_MODEL.parameters()).device)

    prompt = _build_prompt(schema_text, question)
    inputs = _TOKENIZER(prompt, return_tensors="pt")
    inputs = {k: v.to(_MODEL.device) for k, v in inputs.items()}

    with torch.inference_mode():
        out = _MODEL.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,      # deterministic
            # NOTE: don't pass temperature/top_p/top_k when do_sample=False
            eos_token_id=_TOKENIZER.eos_token_id,
        )

    # Decode ONLY the newly generated tokens (avoid prompt-echo issues)
    gen_tokens = out[0][inputs["input_ids"].shape[-1]:]
    decoded = _TOKENIZER.decode(gen_tokens, skip_special_tokens=True).strip()

    sql = _extract_sql(decoded)
    if not sql:
        # Helpful for debugging: you can temporarily log `decoded` in router/main
        raise ValueError(f"HF model did not return SELECT/WITH SQL. Raw output: {decoded[:300]}")
    sql = _apply_limit(sql, question)
    return sql
