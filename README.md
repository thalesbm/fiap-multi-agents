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

## Fluxo das ferramentas (tools)

As tools são funções Python (não-LLM, determinísticas) registradas no
construtor de cada agente. Quando o agente precisa de dados externos ou de
informações de uma base local, ele chama a tool via `self.use_tool(nome, …)`
(método herdado de `Agent`), e o **retorno da tool é injetado no contexto
JSON** que vai junto com o prompt para o LLM.

### Diagrama do fluxo end-to-end

```
[ Cliente digita: "PETR4 VALE3" no main.py ]
                │
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ AgentePesquisador.pesquisar(produtos)                                 │
│   1. para cada produto em ["CDB","Tesouro Direto","FII","Acoes"]:     │
│        ficha = use_tool("pesquisar", produto)                         │
│        └─► pesquisar_conceito(produto)                                │
│            └─► consulta BASE_CONHECIMENTO (dict local)                │
│            └─► retorna string com a explicação do produto             │
│   2. run(TASK_TEMPLATE, context={"fichas_tecnicas": fichas})          │
│      └─► LLM gera um resumo didático consolidado                      │
│   retorna: {"fichas": {...}, "resumo": "<texto LLM>"}                 │
└──────────────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ AgenteDadosB3.analisar_carteira(tickers)                              │
│   1. dados = use_tool("resumo_mercado", ["PETR4","VALE3"])            │
│        └─► resumo_mercado_b3(tickers)                                 │
│            └─► para cada ticker: cotacao_b3(ticker)                   │
│                └─► HTTP GET https://brapi.dev/api/quote/PETR4         │
│                    com BRAPI_TOKEN no query string                    │
│                └─► _mapear_resultado(payload) padroniza o dict        │
│            └─► retorna lista de cotações reais                        │
│   2. run(TASK_TEMPLATE, context={"cotacoes_b3": dados})               │
│      └─► LLM gera análise descritiva ancorada nos preços reais        │
│   retorna: {"dados": [...], "analise": "<texto LLM>"}                 │
└──────────────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ AgenteEstrategista.recomendar(perfil, out_pesq, out_b3)               │
│   - NÃO usa tools — só consolida.                                     │
│   run(TASK, context={                                                 │
│       "perfil_cliente": perfil,                                       │
│       "conceitos": out_pesq,    # ← do Pesquisador                    │
│       "dados_b3":  out_b3,      # ← do Dados B3                       │
│   })                                                                  │
│   └─► LLM gera recomendação final personalizada (5 seções)            │
│   retorna: string com a recomendação consolidada                      │
└──────────────────────────────────────────────────────────────────────┘
                │
                ▼
[ Output formatado impresso para o cliente no terminal ]
```

### Tools — input / output

| Tool | Input | O que faz | Output |
|---|---|---|---|
| `pesquisar_conceito` | `conceito: str` | Busca por correspondência parcial (lowercase) no `BASE_CONHECIMENTO` (dict literal em `agents/pesquisador/agent.py` com fichas de CDB, Tesouro Direto, FII, ações, Selic, CDI, IPCA) | `str` com a explicação do produto, ou mensagem de "não encontrado" |
| `cotacao_b3` | `ticker: str` (ex.: `PETR4`) | `HTTP GET https://brapi.dev/api/quote/{ticker}?token=…` → mapeia o payload via `_mapear_resultado()` | `dict` com `ticker`, `nome`, `preco_atual`, `moeda`, `variacao_dia_pct`, `variacao_52s {min,max}`, `volume`, `pl`, `lpa`, `market_cap`, `atualizado_em`. Se falhar: `{"ticker": …, "erro": …}` |
| `resumo_mercado_b3` | `tickers: List[str]` | Itera chamando `cotacao_b3()` para cada ticker (o plano gratuito da BrAPI limita a 1 ativo por requisição) | `List[dict]` com o resultado de cada cotação |

### Fontes de dados

| Fonte | Acesso | Usada por |
|---|---|---|
| **Base de conhecimento local** | Dict Python em `agents/pesquisador/agent.py` | `pesquisar_conceito` |
| **BrAPI** (https://brapi.dev) | HTTP REST + token via `BRAPI_TOKEN` | `cotacao_b3`, `resumo_mercado_b3` |
| **OpenAI Chat Completions** | SDK `openai` + chave via `OPENAI_API_KEY`, modelo `gpt-4o-mini` (default, configurável via `OPENAI_MODEL`) | Função `llm()` em `config.py`, usada por todos os agentes via `Agent.run()` |

## Prompts utilizados

Cada agente tem 2 prompts: o **`INSTRUCTION`** (system prompt — persona e regras
do agente, definida no construtor) e o **`TASK` / `TASK_TEMPLATE`** (user prompt
— a tarefa específica que o `consultar()` envia em cada rodada). Ambos vivem em
`agents/<agente>/prompts.py` e estão transcritos literalmente abaixo.

### Agente Pesquisador — `agents/pesquisador/prompts.py`

**`INSTRUCTION`** (system prompt):

> Voce e um analista de mercado especializado em produtos financeiros
> brasileiros (CDB, Tesouro Direto, FIIs, acoes). Sua funcao e EXPLICAR
> conceitos de forma didatica, baseando-se nas fichas tecnicas fornecidas
> no contexto. Voce NUNCA recomenda investimento — apenas educa o cliente.

**`TASK_TEMPLATE`** (user prompt, com placeholder `{produtos}`):

> Explique de forma clara, em ate 3 paragrafos, os seguintes produtos:
> {produtos}. Use as fichas tecnicas fornecidas no contexto como base.

### Agente de Dados B3 — `agents/dados_b3/prompts.py`

**`INSTRUCTION`** (system prompt):

> Voce e um especialista em dados da B3 (Bolsa de Valores brasileira).
> Sua funcao e analisar ativos exclusivamente com base nas COTACOES
> REAIS fornecidas no contexto. Voce NUNCA inventa cotacoes. Se um dado
> nao estiver disponivel no contexto, declare isso explicitamente.

**`TASK_TEMPLATE`** (user prompt, com placeholder `{tickers}`):

> Analise brevemente os ativos {tickers} a partir dos dados reais abaixo.
> Para cada ativo, destaque: preco atual, variacao do dia, faixa de 52
> semanas, P/L (quando disponivel) e market cap. Nao recomende compra ou
> venda — apenas descreva.

### Agente Estrategista — `agents/estrategista/prompts.py`

**`INSTRUCTION`** (system prompt):

> Voce e o Consultor Financeiro LIDER da Quantum Finance. Sua tarefa e
> gerar uma recomendacao de alocacao de carteira PERSONALIZADA para o
> cliente, considerando: (1) perfil de risco, (2) horizonte de tempo,
> (3) objetivos, (4) dados reais da B3 fornecidos no contexto,
> (5) conceitos explicados pelo Agente Pesquisador.
> **REGRAS CRITICAS:** NUNCA invente cotacoes — use APENAS os dados do
> contexto. Sempre inclua um aviso final de que esta e uma sugestao
> educacional, NAO uma recomendacao formal de investimento.

**`TASK`** (user prompt fixo, sem placeholders):

> Com base no perfil do cliente e nas analises dos sub-agentes, gere:
> 1. Diagnostico do perfil do cliente.
> 2. Sugestao de alocacao em % (renda fixa, FIIs, acoes, reserva de emergencia).
> 3. Justificativa usando os dados reais da B3 presentes no contexto.
> 4. Riscos relevantes a considerar.
> 5. Aviso final de carater educacional.

### Como o prompt final é montado

`Agent.run(task, context)` em `agents/base.py` faz a composição:

```python
prompt = (
    f"# Tarefa\n{task}\n\n"
    f"# Contexto / Dados disponiveis\n{json.dumps(context, ...)}\n\n"
    "Responda em portugues, de forma clara e objetiva."
)
llm(prompt, system=self.instruction)
```

Ou seja, cada chamada ao LLM é uma `ChatCompletion` com duas mensagens:

| Role | Conteúdo |
|---|---|
| `system` | `INSTRUCTION` do agente |
| `user` | `# Tarefa\n<TASK ou TASK_TEMPLATE>\n\n# Contexto\n<JSON com o que as tools retornaram>\n\nResponda em portugues, de forma clara e objetiva.` |

## Anti-alucinação

Conforme exigido no enunciado do projeto:

> *"Um consultor financeiro não pode 'alucinar' cotações."*

- O **Agente de Dados B3** é instruído a **nunca inventar cotações**.
- O **Agente Estrategista** só pode citar cotações **presentes no contexto**
  (o que foi produzido pelo Agente de Dados B3).
- A base de conceitos do Pesquisador é determinística (não depende de LLM).
