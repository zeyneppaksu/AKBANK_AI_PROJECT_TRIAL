# backend/app/schema_context.py
from functools import lru_cache
from .db import query

@lru_cache(maxsize=1)
def get_schema_context() -> str:
    """
    Returns a compact schema description for prompting.
    Cached so we don't query information_schema every request.
    """
    sql = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name, ordinal_position;
    """
    res = query(sql)

    # res = {"columns": [...], "rows": [...]}
    rows = res.get("rows", [])

    tables = {}
    for table_name, column_name, data_type in rows:
        tables.setdefault(table_name, []).append((column_name, data_type))

    lines = ["DATABASE SCHEMA (PostgreSQL):"]
    for t, cols in tables.items():
        col_str = ", ".join([f"{c} ({dt})" for c, dt in cols])
        lines.append(f"- {t}: {col_str}")

    # Keep it short-ish
    return "\n".join(lines)

def refresh_schema_cache() -> None:
    get_schema_context.cache_clear()
