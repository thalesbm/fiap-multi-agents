"""Agente Estrategista (Lead Advisor).

Recebe o perfil do cliente, consolida as saidas do Agente Pesquisador e do
Agente de Dados B3, e produz a recomendacao final de carteira.
"""

from __future__ import annotations

from typing import Any, Dict

from agents.base import Agent
from agents.estrategista.prompts import INSTRUCTION, TASK


class AgenteEstrategista(Agent):
    def __init__(self) -> None:
        super().__init__(name="Estrategista", instruction=INSTRUCTION)

    def recomendar(
        self,
        perfil_cliente: Dict[str, Any],
        saida_pesquisador: Dict[str, Any],
        saida_b3: Dict[str, Any],
    ) -> str:
        return self.run(
            task=TASK,
            context={
                "perfil_cliente": perfil_cliente,
                "conceitos": saida_pesquisador,
                "dados_b3": saida_b3,
            },
        )
