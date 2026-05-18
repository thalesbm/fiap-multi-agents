"""Agente Pesquisador (Market Analyst).

Responsavel por buscar informacoes publicas e explicar conceitos e produtos
financeiros brasileiros (CDB, Tesouro Direto, FIIs, acoes).

Inclui uma base de conhecimento local sobre produtos financeiros brasileiros
que funciona como "tool de pesquisa". Em uma versao mais completa, poderia
ser substituida por um RAG ou chamada a uma API externa (ANBIMA, Tesouro
Nacional, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, List

from agents.base import Agent
from agents.pesquisador.prompts import INSTRUCTION, TASK_TEMPLATE


BASE_CONHECIMENTO: dict[str, str] = {
    "cdb": (
        "CDB (Certificado de Deposito Bancario): titulo de renda fixa emitido "
        "por bancos. Possui garantia do FGC ate R$250 mil por CPF/instituicao. "
        "Rentabilidade pode ser prefixada, pos-fixada (% do CDI) ou hibrida (IPCA+)."
    ),
    "tesouro direto": (
        "Tesouro Direto: titulos publicos emitidos pelo Governo Federal. "
        "Considerado o investimento de menor risco do pais. Principais: "
        "Tesouro Selic (pos-fixado), Tesouro Prefixado e Tesouro IPCA+."
    ),
    "fii": (
        "FII (Fundo de Investimento Imobiliario): fundo negociado em bolsa que "
        "investe em imoveis (tijolo) ou em recebiveis imobiliarios (papel). "
        "Distribui rendimentos mensais isentos de IR para pessoa fisica."
    ),
    "acoes": (
        "Acoes: fracoes do capital de uma empresa listada em bolsa (B3). "
        "Renda variavel, com maior risco e maior potencial de retorno no longo prazo."
    ),
    "selic": (
        "Taxa Selic: taxa basica de juros da economia brasileira, definida pelo Copom. "
        "Serve como referencia para a maior parte da renda fixa."
    ),
    "cdi": (
        "CDI: taxa de referencia para renda fixa, normalmente muito proxima a Selic."
    ),
    "ipca": (
        "IPCA: indice oficial de inflacao do Brasil, medido pelo IBGE. "
        "Usado como referencia para titulos atrelados a inflacao."
    ),
}


def pesquisar_conceito(conceito: str) -> str:
    """Busca a explicacao de um conceito na base local.

    A busca e feita por correspondencia parcial (case-insensitive).
    """
    chave = conceito.lower().strip()
    for k, v in BASE_CONHECIMENTO.items():
        if k in chave:
            return v
    return f"Conceito '{conceito}' nao encontrado na base local."


class AgentePesquisador(Agent):
    def __init__(self) -> None:
        super().__init__(
            name="Pesquisador",
            instruction=INSTRUCTION,
            tools={"pesquisar": pesquisar_conceito},
        )

    def pesquisar(self, produtos: List[str]) -> Dict[str, Any]:
        """Coleta fichas tecnicas via tool e pede ao LLM um resumo consolidado.

        Returns:
            Dict com:
                - `fichas`: ficha tecnica bruta de cada produto.
                - `resumo`: explicacao consolidada gerada pelo agente.
        """
        fichas = {p: self.use_tool("pesquisar", p) for p in produtos}
        resumo = self.run(
            task=TASK_TEMPLATE.format(produtos=", ".join(produtos)),
            context={"fichas_tecnicas": fichas},
        )
        return {"fichas": fichas, "resumo": resumo}
