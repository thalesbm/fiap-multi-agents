"""Configuracao central do projeto Quantum Finance.

Carrega a chave da OpenAI e expoe uma funcao `llm()` usada por todos os agentes.
A `OPENAI_API_KEY` e obrigatoria — exporte-a antes de rodar o projeto:

    export OPENAI_API_KEY="sua-chave"
"""

from __future__ import annotations

import os

from openai import OpenAI

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY nao definida. Exporte a variavel antes de rodar: "
        "`export OPENAI_API_KEY=\"sua-chave\"`."
    )

_client = OpenAI(api_key=OPENAI_API_KEY)


def llm(prompt: str, system: str = "Voce e um assistente financeiro.") -> str:
    """Chama o LLM com a mensagem e o system prompt fornecidos."""
    response = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return (response.choices[0].message.content or "").strip()


def status() -> dict:
    """Resumo do estado da configuracao (util para logging)."""
    return {"model": MODEL_NAME}
