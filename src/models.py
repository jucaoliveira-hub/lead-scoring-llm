"""
Modelos Pydantic: definem e validam o "shape" (formato) do JSON
que entra (dados do lead) e do JSON que sai (score da LLM).

Ter isso explícito em código é o que garante que, mesmo antes de
chegar na LLM, um payload malformado já é rejeitado com um erro claro.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RespostasPesquisa(BaseModel):
    principal_desafio: Optional[str] = None
    prazo_para_decisao: Optional[str] = None
    ja_usa_ferramenta_similar: Optional[bool] = None


class LeadInput(BaseModel):
    lead_id: str
    nome: str
    email: EmailStr
    empresa: str
    cargo: str
    numero_funcionarios: int = Field(ge=0)
    setor: str
    orcamento_estimado_usd: float = Field(ge=0)
    origem: str
    respostas_pesquisa: Optional[RespostasPesquisa] = None


class ICPMatch(BaseModel):
    industria_alvo: bool
    tamanho_empresa_ok: bool
    orcamento_ok: bool
    cargo_decisor: bool


class ScoreOutput(BaseModel):
    lead_id: str
    score: int = Field(ge=0, le=100)
    classification: str = Field(pattern="^(hot|warm|cold)$")
    icp_match: ICPMatch
    reasoning: str
    recommended_action: str
