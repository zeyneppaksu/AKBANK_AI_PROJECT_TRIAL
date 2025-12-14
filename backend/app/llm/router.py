# backend/app/llm/router.py
import os

from . import mock, ollama, vllm


def generate_sql(question: str) -> str:
    mode = os.getenv("LLM_MODE", "mock").strip().lower()

    if mode == "mock":
        return mock.generate_sql(question)

    if mode == "ollama":
        return ollama.generate_sql(question)

    if mode == "vllm":
        return vllm.generate_sql(question)

    raise ValueError(f"Unknown LLM_MODE='{mode}'. Use: mock | ollama | vllm")
