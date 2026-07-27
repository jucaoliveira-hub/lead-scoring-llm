# Lead Scoring com LLM (Qualificação e Enriquecimento de Leads)

Projeto de referência para qualificação automática de leads usando LLM (Claude) com
saída **estritamente estruturada em JSON**, pronta para roteamento em CRM.

## Como funciona (visão geral)

```
Formulário / Pesquisa
        │  (dados brutos)
        ▼
  Webhook (POST /webhook/lead)
        │
        ▼
  Validação do payload (Pydantic)
        │
        ▼
  Prompt + ICP (Ideal Customer Profile)
        │
        ▼
     LLM (Claude) ──► saída JSON validada por schema
        │
        ▼
  Classificação (hot / warm / cold) + score
        │
        ▼
  Roteamento automático no CRM (mock/adaptável)
```

O ponto central é: a LLM **nunca** responde texto livre. Ela é forçada, via *tool use*
(function calling) da API da Anthropic, a devolver um JSON que respeita um schema fixo.
Isso elimina o problema clássico de "a IA respondeu bonito mas o sistema não consegue
parsear".

## Estrutura do projeto

```
lead-scoring-llm/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── icp.json              # Definição do Perfil de Cliente Ideal (regras de negócio)
├── src/
│   ├── main.py                # API FastAPI (recebe o webhook)
│   ├── models.py              # Modelos Pydantic (validação de entrada/saída)
│   ├── llm_client.py          # Chamada à LLM com JSON forçado (tool use)
│   ├── icp_config.py          # Carrega e aplica as regras do ICP
│   └── crm_client.py          # Simula o envio/roteamento para o CRM
├── examples/
│   ├── sample_lead_input.json  # Exemplo de payload recebido do formulário
│   └── sample_llm_output.json  # Exemplo de saída da LLM já validada
├── docs/
│   └── GUIA-JSON.md            # Guia rápido de JSON aplicado a este projeto
└── tests/
    └── test_scoring.py
```

## Setup rápido

```bash
# 1. Clonar / entrar na pasta
cd lead-scoring-llm

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# edite .env e coloque sua ANTHROPIC_API_KEY

# 5. Rodar a API
uvicorn src.main:app --reload --port 8000
```

## Testando o webhook

```bash
curl -X POST http://localhost:8000/webhook/lead \
  -H "Content-Type: application/json" \
  -d @examples/sample_lead_input.json
```

Resposta esperada: um JSON com `score`, `classification` (hot/warm/cold),
`icp_match` detalhado e `recommended_action` — pronto para o CRM decidir o roteamento
(ex: hot → SDR liga em 5 min; cold → fluxo de nutrição por e-mail).

## Customizando o ICP (Perfil de Cliente Ideal)

Toda a lógica de negócio de "o que é um bom lead" fica isolada em `config/icp.json`,
sem precisar mexer em código ou no prompt. Exemplo:

```json
{
  "industries_target": ["SaaS", "Fintech", "E-commerce"],
  "company_size_min": 11,
  "company_size_max": 500,
  "budget_min_usd": 2000,
  "decision_maker_roles": ["CEO", "CTO", "Head", "Diretor", "Gerente"]
}
```

## Próximos passos sugeridos

- [ ] Trocar `crm_client.py` (mock) pela integração real (HubSpot, RD Station, Pipedrive, etc.)
- [ ] Adicionar autenticação no webhook (assinatura HMAC, header secreto)
- [ ] Persistir histórico de leads pontuados (banco de dados)
- [ ] Adicionar fila (SQS/RabbitMQ) se o volume de leads for alto
- [ ] Criar dashboard de acompanhamento de qualidade dos scores

## Aprendendo JSON rápido

Se você está começando com JSON agora, veja **`docs/GUIA-JSON.md`** — um guia curto e
prático, usando exatamente os JSONs deste projeto como exemplo.
