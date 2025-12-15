# backend/app/db.py
import os
import psycopg

DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:5432/mockbank")

def query(sql: str, timeout_ms: int = 5000):
    """
    Executes read-only queries with a statement timeout.
    Returns dict: {"columns": [...], "rows": [[...], ...]}
    """
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # hard stop long queries
            cur.execute(f"SET LOCAL statement_timeout = {int(timeout_ms)};")
            cur.execute(sql)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = cur.fetchall() if cols else []
            return {"columns": cols, "rows": rows}
