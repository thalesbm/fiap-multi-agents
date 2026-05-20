"""Agente de Dados B3.

Especialista em buscar cotacoes e indicadores fundamentais diretamente da
bolsa brasileira (B3). Usa a API publica BrAPI (https://brapi.dev), que e
brasileira e especifica para a B3 — mais robusta para esses tickers do que
fontes internacionais.

Tickers brasileiros NAO usam sufixo na BrAPI (ex.: PETR4, VALE3, ITUB4).

Token obrigatorio: cadastre-se gratuitamente em https://brapi.dev e
exporte a variavel de ambiente:

    export BRAPI_TOKEN="seu-token"
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import requests

from agents.base import Agent
from agents.dados_b3.prompts import INSTRUCTION, TASK_TEMPLATE

BRAPI_BASE_URL = "https://brapi.dev/api/quote"
BRAPI_TOKEN = os.getenv("BRAPI_TOKEN", "")


def _normalizar_ticker(ticker: str) -> str:
    """BrAPI usa ticker sem sufixo `.SA`."""
    return ticker.upper().strip().removesuffix(".SA")


def _mapear_resultado(item: Dict[str, Any]) -> Dict[str, Any]:
    """Converte a resposta crua da BrAPI no formato esperado pelos agentes."""
    return {
        "ticker": item.get("symbol"),
        "nome": item.get("longName") or item.get("shortName"),
        "preco_atual": item.get("regularMarketPrice"),
        "moeda": item.get("currency", "BRL"),
        "variacao_dia_pct": item.get("regularMarketChangePercent"),
        "variacao_52s": {
            "min": item.get("fiftyTwoWeekLow"),
            "max": item.get("fiftyTwoWeekHigh"),
        },
        "volume": item.get("regularMarketVolume"),
        "pl": item.get("priceEarnings"),
        "lpa": item.get("earningsPerShare"),
        "market_cap": item.get("marketCap"),
        "atualizado_em": item.get("regularMarketTime"),
    }


def cotacao_b3(ticker: str) -> Dict[str, Any]:
    """Retorna cotacao atual e indicadores de um unico ativo da B3.

    O plano gratuito da BrAPI limita a 1 ativo por requisicao, portanto
    fazemos uma chamada HTTP separada para cada ticker.
    """
    symbol = _normalizar_ticker(ticker)

    if not BRAPI_TOKEN:
        return {
            "ticker": symbol,
            "erro": (
                "BRAPI_TOKEN nao definida. Cadastre-se gratuitamente em "
                "https://brapi.dev e exporte: `export BRAPI_TOKEN=\"seu-token\"`."
            ),
        }

    try:
        resp = requests.get(
            f"{BRAPI_BASE_URL}/{symbol}",
            params={"token": BRAPI_TOKEN},
            timeout=15,
            headers={"User-Agent": "QuantumFinance-MultiAgent/1.0"},
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        return {"ticker": symbol, "erro": str(exc)}

    resultados = payload.get("results") or []
    if not resultados:
        return {"ticker": symbol, "erro": "ativo nao encontrado na BrAPI"}
    return _mapear_resultado(resultados[0])


def resumo_mercado_b3(tickers: List[str]) -> List[Dict[str, Any]]:
    """Busca cotacoes de varios ativos.

    Faz uma requisicao por ticker (limite do plano gratuito da BrAPI).
    """
    return [cotacao_b3(t) for t in tickers]


class AgenteDadosB3(Agent):
    def __init__(self) -> None:
        super().__init__(
            name="Dados B3",
            instruction=INSTRUCTION,
            tools={
                "cotacao": cotacao_b3,
                "resumo_mercado": resumo_mercado_b3,
            },
        )

    def analisar_carteira(self, tickers: List[str]) -> Dict[str, Any]:
        """Busca dados reais dos tickers e gera uma analise descritiva.

        Returns:
            Dict com:
                - `dados`: cotacoes brutas vindas da BrAPI.
                - `analise`: texto descritivo gerado pelo agente via LLM.
        """
        dados = self.use_tool("resumo_mercado", tickers)
        analise = self.run(
            task=TASK_TEMPLATE.format(tickers=", ".join(tickers)),
            context={"cotacoes_b3": dados},
        )
        return {"dados": dados, "analise": analise}
