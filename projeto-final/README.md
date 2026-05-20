# Quantum Finance — Consultor Financeiro Multi-Agente

MBA Data Science & Artificial Intelligence — Intelligent Multi Agents.

Sistema de IA Agêntica que atua como **Consultor Financeiro** para clientes
da Quantum Finance, com 3 agentes colaborando entre si em modo conversacional.

## Arquitetura

```
projeto-final/
├── main.py                       # modo conversacional + função consultar()
├── config.py                     # config do LLM (OpenAI)
├── requirements.txt
└── agents/
    ├── base.py                   # classe Agent base
    ├── pesquisador/              # Agente Pesquisador (Market Analyst)
    ├── dados_b3/                 # Agente de Dados B3 (BrAPI)
    └── estrategista/             # Agente Estrategista (Lead Advisor)
```

### Agentes

| Agente | Pasta | Responsabilidade |
|---|---|---|
| **Pesquisador** (Market Analyst) | `agents/pesquisador/` | Explica produtos do mercado (CDB, Tesouro Direto, FIIs) |
| **Dados B3** | `agents/dados_b3/` | Busca cotações e indicadores reais via BrAPI |
| **Estrategista** (Lead Advisor) | `agents/estrategista/` | Recebe perfil do cliente + saídas dos demais e gera a recomendação final |

Cada pasta de agente tem:
- `agent.py` — classe do agente (e, quando aplicável, as tools que ele usa)
- `prompts.py` — system prompt e templates de tarefa

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
