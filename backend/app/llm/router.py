# backend/app/llm/router.py
import os
from . import mock, ollama, vllm
from ..schema_context import get_schema_context

def generate_sql(question: str) -> str:
    mode = os.getenv("LLM_MODE", "mock").strip().lower()

    # only real LLMs need schema injected; mock can ignore
    schema = None
    if mode in ("ollama", "vllm"):
        schema = get_schema_context()

    if mode == "mock":
        return mock.generate_sql(question)

    if mode == "ollama":
        return ollama.generate_sql(question, schema_context=schema)

    if mode == "vllm":
        return vllm.generate_sql(question, schema_context=schema)

    raise ValueError(f"Unknown LLM_MODE='{mode}'. Use: mock | ollama | vllm")
