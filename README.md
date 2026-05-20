# Quantum Finance — Consultor Financeiro Multi-Agente

MBA Data Science & Artificial Intelligence — Intelligent Multi Agents.

Sistema de IA Agêntica que atua como **Consultor Financeiro** para clientes
da Quantum Finance, com 3 agentes colaborando entre si em modo conversacional.

## Arquitetura

```
trabalho/
├── README.md                         # este arquivo
├── documento/
│   └── Avaliação Quantum Finance ... .pdf
└── projeto-final/
    ├── main.py                       # modo conversacional + função consultar()
    ├── config.py                     # config do LLM (OpenAI)
    ├── requirements.txt
    └── agents/
        ├── base.py                   # classe Agent base
        ├── pesquisador/              # Agente Pesquisador (Market Analyst)
        │   ├── agent.py              # AgentePesquisador + pesquisar_conceito()
        │   └── prompts.py
        ├── dados_b3/                 # Agente de Dados B3 (BrAPI)
        │   ├── agent.py              # AgenteDadosB3 + cotacao_b3() + resumo_mercado_b3()
        │   └── prompts.py
        └── estrategista/             # Agente Estrategista (Lead Advisor)
            ├── agent.py              # AgenteEstrategista
            └── prompts.py
```

### Orquestração

`main.py` define a função `consultar(perfil_cliente, produtos_interesse, tickers_b3, ...)`
que coordena os 3 agentes em sequência:

```
consultar()
  ├── [1/3] AgentePesquisador.pesquisar(produtos_interesse)
  ├── [2/3] AgenteDadosB3.analisar_carteira(tickers_b3)
  └── [3/3] AgenteEstrategista.recomendar(perfil, out_pesq, out_b3)
```

### Agentes

| Agente | Pasta | Classe | Método público | Responsabilidade |
|---|---|---|---|---|
| **Pesquisador** (Market Analyst) | `agents/pesquisador/` | `AgentePesquisador` | `pesquisar(produtos)` | Explica produtos do mercado (CDB, Tesouro Direto, FIIs, ações) |
| **Dados B3** | `agents/dados_b3/` | `AgenteDadosB3` | `analisar_carteira(tickers)` | Busca cotações e indicadores reais da B3 via API BrAPI |
| **Estrategista** (Lead Advisor) | `agents/estrategista/` | `AgenteEstrategista` | `recomendar(perfil, saida_pesquisador, saida_b3)` | Consolida perfil do cliente + saídas dos demais e gera a recomendação final |

#### Classe base

Todos os agentes herdam de `Agent` (`agents/base.py`):

| Método | Descrição |
|---|---|
| `run(task, context)` | Monta o prompt completo (tarefa + contexto em JSON) e chama o LLM |
| `use_tool(nome, *args)` | Dispara uma tool registrada no construtor do agente |

#### Tools registradas em cada agente

| Agente | Tool | Função (callable) | Onde está |
|---|---|---|---|
| `AgentePesquisador` | `pesquisar` | `pesquisar_conceito(conceito)` | `agents/pesquisador/agent.py` |
| `AgenteDadosB3` | `cotacao` | `cotacao_b3(ticker)` | `agents/dados_b3/agent.py` |
| `AgenteDadosB3` | `resumo_mercado` | `resumo_mercado_b3(tickers)` | `agents/dados_b3/agent.py` |
| `AgenteEstrategista` | _(nenhuma)_ | — | só consolida o contexto e chama o LLM |

#### Estrutura interna de cada pasta de agente

```
agents/<nome_do_agente>/
├── agent.py        # classe do agente + tools que ele consome
└── prompts.py      # INSTRUCTION (system prompt) + TASK / TASK_TEMPLATE
```

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r projeto-final/requirements.txt
```

## Variáveis de ambiente

Duas variáveis são **obrigatórias**:

| Variável | Como obter |
|---|---|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys (precisa ter crédito) |
| `BRAPI_TOKEN` | Cadastro gratuito em https://brapi.dev → Dashboard |

> **Nunca** cole essas chaves no código ou em arquivos versionados.
> Use sempre variáveis de ambiente.

## Execução

```bash
export OPENAI_API_KEY="sua-chave-openai"
export BRAPI_TOKEN="seu-token-brapi"
cd projeto-final
python main.py
```

## Modo conversacional

O `main.py` funciona em modo **chat**:

1. **Cadastro inicial** — coleta nome, idade, renda, patrimônio, perfil de
   risco, horizonte e objetivos (basta Enter para usar os valores padrão).
2. **Loop de perguntas** — você digita os tickers da B3 que quer analisar
   (ex.: `PETR4 VALE3 ITUB4`) e os 3 agentes geram uma recomendação
   personalizada para o seu perfil baseada nas cotações reais.
3. **Sair** — digite `sair` (ou `q`, `exit`, `quit`).

Exemplo de sessão:

```
> Quais acoes quer analisar? PETR4 VALE3

[1/3] Agente Pesquisador analisando produtos...
[2/3] Agente de Dados B3 buscando cotacoes reais...
[3/3] Agente Estrategista consolidando recomendacao...

---- DADOS REAIS DA B3 ----
- PETR4    preco=R$ 45.47  var_dia=1.04%  52s=28.86-50.69  (Petroleo Brasileiro SA)
- VALE3    preco=R$ 83.50  var_dia=0.76%  52s=49.72-91.62  (Vale S.A.)

---- RECOMENDACAO PERSONALIZADA ----
[recomendação consolidada pelo Estrategista usando o perfil e os preços reais]

> Quais acoes quer analisar? sair
Ate logo!
```

## Anti-alucinação

Conforme exigido no enunciado do projeto:

> *"Um consultor financeiro não pode 'alucinar' cotações."*

- O **Agente de Dados B3** é instruído a **nunca inventar cotações**.
- O **Agente Estrategista** só pode citar cotações **presentes no contexto**
  (o que foi produzido pelo Agente de Dados B3).
- A base de conceitos do Pesquisador é determinística (não depende de LLM).
