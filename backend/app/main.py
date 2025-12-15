# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .sql_safety import assert_read_only, ensure_limit

from .llm import generate_sql
from .sql_guard import assert_read_only
from .db import query

app = FastAPI(title="Mock NL→SQL System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskReq(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask")
def ask(req: AskReq):
    try:
        sql = generate_sql(req.question)
        assert_read_only(sql)
        sql = ensure_limit(sql, default_limit=50, max_limit=200)
        result = query(sql, timeout_ms=5000)
        return {"question": req.question, "sql": sql.strip(), "result": result}
    except Exception as e:
        # clean error text for UI
        msg = str(e)
        # shorten noisy psycopg messages
        msg = msg.split("\n")[0]
        raise HTTPException(status_code=400, detail=msg)
import os

@app.get("/config")
def config():
    return {"llm_mode": os.getenv("LLM_MODE", "mock")}
from .schema_context import get_schema_context

@app.get("/schema")
def schema():
    return {"schema": get_schema_context()}
