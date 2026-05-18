"""Ponto de entrada do Consultor Financeiro Multi-Agente Quantum Finance.

Defina a chave da OpenAI antes de rodar:

    export OPENAI_API_KEY="sua-chave"
    python main.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from agents.dados_b3.agent import AgenteDadosB3
from agents.estrategista.agent import AgenteEstrategista
from agents.pesquisador.agent import AgentePesquisador
from config import status


def consultar(
    perfil_cliente: Dict[str, Any],
    produtos_interesse: List[str],
    tickers_b3: List[str],
    verbose: bool = True,
) -> Dict[str, Any]:
    """Pipeline completo do consultor financeiro multi-agente.

    Coordena o fluxo: Pesquisador -> Dados B3 -> Estrategista, passando o
    contexto acumulado para o agente lider produzir a recomendacao final.
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    pesquisador = AgentePesquisador()
    dados_b3 = AgenteDadosB3()
    estrategista = AgenteEstrategista()

    log("[1/3] Agente Pesquisador analisando produtos...")
    out_pesq = pesquisador.pesquisar(produtos_interesse)

    log("[2/3] Agente de Dados B3 buscando cotacoes reais...")
    out_b3 = dados_b3.analisar_carteira(tickers_b3)

    log("[3/3] Agente Estrategista consolidando recomendacao...")
    recomendacao = estrategista.recomendar(
        perfil_cliente=perfil_cliente,
        saida_pesquisador=out_pesq,
        saida_b3=out_b3,
    )

    return {
        "perfil": perfil_cliente,
        "pesquisador": out_pesq,
        "dados_b3": out_b3,
        "recomendacao_final": recomendacao,
    }


def main() -> None:
    print("=" * 70)
    print(" Quantum Finance — Consultor Financeiro Multi-Agente")
    print("=" * 70)
    print(f"Configuracao: {status()}\n")

    perfil_cliente = {
        "nome": "Joao da Silva",
        "idade": 34,
        "renda_mensal": 12_000,
        "patrimonio_investido": 80_000,
        "perfil_risco": "moderado",
        "horizonte": "10 anos",
        "objetivos": ["aposentadoria", "renda passiva"],
    }
    produtos_interesse = ["CDB", "Tesouro Direto", "FII", "Acoes"]
    tickers_b3 = ["PETR4", "VALE3", "ITUB4", "BBAS3"]

    resultado = consultar(
        perfil_cliente=perfil_cliente,
        produtos_interesse=produtos_interesse,
        tickers_b3=tickers_b3,
    )

    print("\n" + "=" * 70)
    print(" DADOS REAIS DA B3")
    print("=" * 70)
    for d in resultado["dados_b3"]["dados"]:
        print(f"- {d.get('ticker'):10s} preco={d.get('preco_atual')}  setor={d.get('setor')}")

    print("\n" + "=" * 70)
    print(" RECOMENDACAO FINAL")
    print("=" * 70)
    print(resultado["recomendacao_final"])


if __name__ == "__main__":
    main()
