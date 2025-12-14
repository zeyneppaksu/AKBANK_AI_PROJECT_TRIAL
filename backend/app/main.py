# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from .llm_mock import nl_to_sql
from .sql_guard import assert_read_only
from .db import query

app = FastAPI(title="Mock NL→SQL System")

# Allow local dev frontend (Vite)
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
        sql = nl_to_sql(req.question)
        assert_read_only(sql)
        result = query(sql)
        return {"question": req.question, "sql": sql.strip(), "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
