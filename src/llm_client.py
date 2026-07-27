"""
Responsável por chamar a Claude API e GARANTIR que a resposta venha em JSON
estritamente parametrizado.

A técnica usada é "tool use forçado" (tool_choice): em vez de pedir
"responda em JSON" como texto livre (o que pode falhar), definimos uma
ferramenta (`registrar_qualificacao_lead`) cujo `input_schema` É o próprio
JSON Schema que queremos como saída. A API então garante que o `input`
retornado no bloco `tool_use` já respeita esse schema.
"""
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

from src.icp_config import load_icp_config
from src.models import ScoreOutput

load_dotenv()

MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# JSON Schema que define exatamente o formato de saída aceito.
SCORING_TOOL = {
    "name": "registrar_qualificacao_lead",
    "description": "Registra a qualificação (score) de um lead com base no ICP.",
    "input_schema": {
        "type": "object",
        "properties": {
            "lead_id": {"type": "string"},
            "score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Nota de 0 a 100 indicando aderência ao ICP.",
            },
            "classification": {
                "type": "string",
                "enum": ["hot", "warm", "cold"],
            },
            "icp_match": {
                "type": "object",
                "properties": {
                    "industria_alvo": {"type": "boolean"},
                    "tamanho_empresa_ok": {"type": "boolean"},
                    "orcamento_ok": {"type": "boolean"},
                    "cargo_decisor": {"type": "boolean"},
                },
                "required": [
                    "industria_alvo",
                    "tamanho_empresa_ok",
                    "orcamento_ok",
                    "cargo_decisor",
                ],
            },
            "reasoning": {
                "type": "string",
                "description": "Justificativa curta (1-2 frases) da nota atribuída.",
            },
            "recommended_action": {
                "type": "string",
                "description": "Ação recomendada para o time comercial/CRM.",
            },
        },
        "required": [
            "lead_id",
            "score",
            "classification",
            "icp_match",
            "reasoning",
            "recommended_action",
        ],
    },
}


def build_prompt(lead: dict, icp: dict) -> str:
    return f"""
Você é um analista de qualificação de leads (Lead Scoring).

Perfil de Cliente Ideal (ICP) da empresa:
{json.dumps(icp, ensure_ascii=False, indent=2)}

Dados brutos do lead recebido via formulário/pesquisa:
{json.dumps(lead, ensure_ascii=False, indent=2)}

Analise o lead cruzando com as premissas do ICP acima e use a ferramenta
`registrar_qualificacao_lead` para registrar sua qualificação.
Critérios:
- industria_alvo: o setor do lead está em icp.industries_target?
- tamanho_empresa_ok: numero_funcionarios está entre company_size_min e company_size_max?
- orcamento_ok: orcamento_estimado_usd >= budget_min_usd?
- cargo_decisor: o cargo do lead corresponde a um dos decision_maker_roles (mesmo que
  parcialmente, ex: "Head de Growth" casa com "Head")?
- score: combine os pesos em icp.score_weights de acordo com os critérios atendidos.
- classification: "hot" se score >= classification_thresholds.hot,
  "warm" se score >= classification_thresholds.warm, senão "cold".
""".strip()


def score_lead(lead: dict) -> ScoreOutput:
    icp = load_icp_config()
    prompt = build_prompt(lead, icp)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[SCORING_TOOL],
        tool_choice={"type": "tool", "name": "registrar_qualificacao_lead"},
        messages=[{"role": "user", "content": prompt}],
    )

    tool_use_block = next(
        block for block in response.content if block.type == "tool_use"
    )
    raw_output = tool_use_block.input  # já vem como dict Python (JSON parseado)

    # Validação extra com Pydantic, garantindo o contrato mesmo se o modelo
    # mudar de comportamento no futuro.
    return ScoreOutput(**raw_output)
