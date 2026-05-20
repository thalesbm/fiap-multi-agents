"""Ponto de entrada do Consultor Financeiro Multi-Agente Quantum Finance.

Modo conversacional:
1. Coleta o perfil do cliente uma vez (com defaults — basta apertar Enter).
2. Entra em loop perguntando quais acoes o cliente quer analisar.
3. A cada rodada, executa o pipeline Pesquisador -> Dados B3 -> Estrategista
   com os tickers informados e exibe a recomendacao consolidada.

Defina as chaves antes de rodar:

    export OPENAI_API_KEY="sua-chave-openai"
    export BRAPI_TOKEN="seu-token-brapi"
    python main.py
"""

from __future__ import annotations

from typing import Any, Dict, List

from agents.dados_b3.agent import AgenteDadosB3
from agents.estrategista.agent import AgenteEstrategista
from agents.pesquisador.agent import AgentePesquisador
from config import status

PERFIL_DEFAULT: Dict[str, Any] = {
    "nome": "Joao da Silva",
    "idade": 34,
    "renda_mensal": 12_000,
    "patrimonio_investido": 80_000,
    "perfil_risco": "moderado",
    "horizonte": "10 anos",
    "objetivos": ["aposentadoria", "renda passiva"],
}

PRODUTOS_PADRAO: List[str] = ["CDB", "Tesouro Direto", "FII", "Acoes"]

COMANDOS_SAIDA = {"sair", "exit", "quit", "q"}


def consultar(
    perfil_cliente: Dict[str, Any],
    produtos_interesse: List[str],
    tickers_b3: List[str],
    pesquisador: AgentePesquisador,
    dados_b3: AgenteDadosB3,
    estrategista: AgenteEstrategista,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Pipeline completo do consultor financeiro multi-agente.

    Coordena o fluxo: Pesquisador -> Dados B3 -> Estrategista, passando o
    contexto acumulado para o agente lider produzir a recomendacao final.
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    log("\n[1/3] Agente Pesquisador analisando produtos...")
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


def perguntar(label: str, default: Any) -> str:
    """Le um input do usuario; se vazio, retorna o default."""
    raw = input(f"{label} [{default}]: ").strip()
    return raw if raw else str(default)


def coletar_perfil() -> Dict[str, Any]:
    """Coleta o perfil do cliente interativamente, com defaults."""
    print("\n" + "=" * 70)
    print(" Cadastro do cliente (Enter para usar o valor padrao)")
    print("=" * 70)

    nome = perguntar("Nome", PERFIL_DEFAULT["nome"])
    idade = int(perguntar("Idade", PERFIL_DEFAULT["idade"]))
    renda = float(perguntar("Renda mensal (R$)", PERFIL_DEFAULT["renda_mensal"]))
    patrimonio = float(
        perguntar("Patrimonio ja investido (R$)", PERFIL_DEFAULT["patrimonio_investido"])
    )
    risco = perguntar(
        "Perfil de risco (conservador / moderado / arrojado)",
        PERFIL_DEFAULT["perfil_risco"],
    )
    horizonte = perguntar("Horizonte de investimento", PERFIL_DEFAULT["horizonte"])
    objetivos_raw = perguntar(
        "Objetivos (separados por virgula)",
        ", ".join(PERFIL_DEFAULT["objetivos"]),
    )
    objetivos = [o.strip() for o in objetivos_raw.split(",") if o.strip()]

    return {
        "nome": nome,
        "idade": idade,
        "renda_mensal": renda,
        "patrimonio_investido": patrimonio,
        "perfil_risco": risco,
        "horizonte": horizonte,
        "objetivos": objetivos,
    }


def imprimir_dados_b3(dados: List[Dict[str, Any]]) -> None:
    print("\n" + "-" * 70)
    print(" DADOS REAIS DA B3")
    print("-" * 70)
    for d in dados:
        if d.get("erro"):
            print(f"- {d.get('ticker'):10s} ERRO: {d['erro']}")
        else:
            v52 = d.get("variacao_52s", {})
            print(
                f"- {d.get('ticker'):10s} preco=R$ {d.get('preco_atual')}  "
                f"var_dia={d.get('variacao_dia_pct')}%  "
                f"52s={v52.get('min')}-{v52.get('max')}  "
                f"({d.get('nome')})"
            )


def parse_tickers(linha: str) -> List[str]:
    """Converte 'PETR4, VALE3 ITUB4' em ['PETR4','VALE3','ITUB4']."""
    return [t.strip().upper() for t in linha.replace(",", " ").split() if t.strip()]


def main() -> None:
    print("=" * 70)
    print(" Quantum Finance — Consultor Financeiro Multi-Agente")
    print("=" * 70)
    print(f"Configuracao: {status()}")

    perfil = coletar_perfil()

    pesquisador = AgentePesquisador()
    dados_b3 = AgenteDadosB3()
    estrategista = AgenteEstrategista()

    print("\n" + "=" * 70)
    print(f" Ola, {perfil['nome']}! Sou o seu consultor da Quantum Finance.")
    print(" Diga quais acoes da B3 voce quer analisar (ex.: PETR4 VALE3 ITUB4).")
    print(f" Digite '{next(iter(COMANDOS_SAIDA))}' para encerrar.")
    print("=" * 70)

    while True:
        try:
            entrada = input("\n> Quais acoes quer analisar? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAte logo!")
            return

        if not entrada:
            print("Nenhum ticker informado. Tente novamente ou digite 'sair'.")
            continue

        if entrada.lower() in COMANDOS_SAIDA:
            print("\nAte logo!")
            return

        tickers = parse_tickers(entrada)
        if not tickers:
            print("Nao consegui interpretar os tickers. Exemplo: PETR4 VALE3.")
            continue

        try:
            resultado = consultar(
                perfil_cliente=perfil,
                produtos_interesse=PRODUTOS_PADRAO,
                tickers_b3=tickers,
                pesquisador=pesquisador,
                dados_b3=dados_b3,
                estrategista=estrategista,
            )
        except Exception as exc:
            print(f"\nFalha na consulta: {type(exc).__name__}: {exc}")
            continue

        imprimir_dados_b3(resultado["dados_b3"]["dados"])

        print("\n" + "-" * 70)
        print(" RECOMENDACAO PERSONALIZADA")
        print("-" * 70)
        print(resultado["recomendacao_final"])


if __name__ == "__main__":
    main()
