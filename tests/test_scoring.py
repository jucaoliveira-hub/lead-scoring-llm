"""
Testes que NÃO dependem de chamar a API real da Anthropic — validam apenas
que o contrato de dados (schema) está sendo respeitado.

Rodar: pytest
"""
import json
from pathlib import Path

from src.models import LeadInput, ScoreOutput

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def test_lead_input_schema_valido():
    with open(EXAMPLES_DIR / "sample_lead_input.json", encoding="utf-8") as f:
        data = json.load(f)

    lead = LeadInput(**data)
    assert lead.lead_id == "lead_00231"
    assert lead.numero_funcionarios == 85


def test_score_output_schema_valido():
    with open(EXAMPLES_DIR / "sample_llm_output.json", encoding="utf-8") as f:
        data = json.load(f)

    score = ScoreOutput(**data)
    assert 0 <= score.score <= 100
    assert score.classification in {"hot", "warm", "cold"}


def test_score_output_rejeita_classification_invalida():
    data = {
        "lead_id": "x",
        "score": 50,
        "classification": "morno",  # inválido de propósito
        "icp_match": {
            "industria_alvo": True,
            "tamanho_empresa_ok": True,
            "orcamento_ok": True,
            "cargo_decisor": True,
        },
        "reasoning": "teste",
        "recommended_action": "teste",
    }
    try:
        ScoreOutput(**data)
        assert False, "Deveria ter levantado erro de validação"
    except Exception:
        pass
