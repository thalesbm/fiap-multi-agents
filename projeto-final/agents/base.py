"""Classe base para todos os agentes.

Cada agente possui:
- `name`: identificador do agente.
- `instruction`: system prompt (persona / regras).
- `tools`: dicionario de ferramentas disponiveis (callables).

O metodo `run` monta um prompt unificado com a tarefa + contexto e delega
para o `llm()` central definido em `config.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from config import llm


@dataclass
class Agent:
    name: str
    instruction: str
    tools: Dict[str, Callable[..., Any]] = field(default_factory=dict)

    def use_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        if tool_name not in self.tools:
            raise ValueError(
                f"Tool '{tool_name}' nao disponivel para o agente {self.name}"
            )
        return self.tools[tool_name](*args, **kwargs)

    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        ctx = json.dumps(context or {}, ensure_ascii=False, indent=2, default=str)
        prompt = (
            f"# Tarefa\n{task}\n\n"
            f"# Contexto / Dados disponiveis\n{ctx}\n\n"
            "Responda em portugues, de forma clara e objetiva."
        )
        return llm(prompt, system=self.instruction)
