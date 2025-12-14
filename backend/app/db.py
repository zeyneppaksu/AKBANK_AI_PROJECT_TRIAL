import os
import psycopg

DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:5432/mockbank")

def query(sql: str):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = cur.fetchall() if cur.description else []
            return {"columns": cols, "rows": rows}
