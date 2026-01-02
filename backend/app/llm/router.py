# backend/app/llm/router.py
import os
from . import mock, ollama, vllm, hf, gemini
from ..schema_context import get_schema_context

def generate_sql(question: str) -> str:
    mode = os.getenv("LLM_MODE", "mock").strip().lower()

    schema = None
    if mode != "mock":
        schema = get_schema_context()

    if mode == "mock":
        return mock.generate_sql(question)

    if mode == "ollama":
        return ollama.generate_sql(question, schema_context=schema)

    if mode == "vllm":
        return vllm.generate_sql(question, schema_context=schema)

    if mode == "hf":
        return hf.generate_sql(question, schema_text=schema)

    if mode == "gemini":
        return gemini.generate_sql(question, schema_text=schema)

    raise ValueError(f"Unknown LLM_MODE='{mode}'. Use: mock | ollama | vllm | hf | gemini")
