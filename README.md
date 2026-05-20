# Quantum Finance — Consultor Financeiro Multi-Agente

MBA Data Science & Artificial Intelligence — Intelligent Multi Agents.

Sistema de IA Agêntica que atua como **Consultor Financeiro** para clientes da
Quantum Finance, com 3 agentes colaborando entre si.

## Arquitetura

```
projeto-final/
├── main.py                       # ponto de entrada + função consultar() (orquestração)
├── config.py                     # config do LLM (OpenAI)
├── requirements.txt
└── agents/
    ├── base.py                   # classe Agent base
    ├── pesquisador/              # Agente Pesquisador (Market Analyst)
    ├── dados_b3/                 # Agente de Dados B3
    └── estrategista/             # Agente Estrategista (Lead Advisor)
```

### Agentes

| Agente | Pasta | Responsabilidade |
|---|---|---|
| **Pesquisador** (Market Analyst) | `agents/pesquisador/` | Explica produtos do mercado (CDB, Tesouro Direto, FIIs) |
| **Dados B3** | `agents/dados_b3/` | Busca cotações e indicadores reais via API BrAPI |
| **Estrategista** (Lead Advisor) | `agents/estrategista/` | Recebe perfil do cliente + saídas dos demais e gera a recomendação final |

Cada pasta de agente segue o mesmo padrão:
- `agent.py` — classe do agente
- `prompts.py` — system prompt e templates de tarefa

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r projeto-final/requirements.txt
```

## Execução

Duas variáveis de ambiente são **obrigatórias**:

| Variável | Como obter |
|---|---|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys (precisa ter crédito) |
| `BRAPI_TOKEN` | Cadastro gratuito em https://brapi.dev → seção "Dashboard" → token pessoal |

```bash
export OPENAI_API_KEY="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"
export BRAPI_TOKEN="auKzRE3FoQgZATThqd9tki"
cd projeto-final
python main.py
```

## Fluxo de execução

```
main.py
  └── consultar(perfil, produtos, tickers)
        ├── [1/3] AgentePesquisador.pesquisar(produtos)
        ├── [2/3] AgenteDadosB3.analisar_carteira(tickers)
        └── [3/3] AgenteEstrategista.recomendar(perfil, out_pesq, out_b3)
```

## Anti-alucinação

Conforme exigido no enunciado:

> "Um consultor financeiro não pode 'alucinar' cotações."

- O **Agente de Dados B3** é instruído a **nunca inventar cotações**.
- O **Agente Estrategista** só pode citar cotações **presentes no contexto**
  (o que foi produzido pelo Agente de Dados B3).
- A base de conceitos do Pesquisador é determinística (não-LLM).
