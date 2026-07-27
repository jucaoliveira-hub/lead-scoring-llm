"""
API que recebe o webhook de leads, chama a LLM para qualificação e roteia
o resultado para o CRM.

Rodar:
    uvicorn src.main:app --reload --port 8000
"""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from src.models import LeadInput
from src.llm_client import score_lead
from src.crm_client import route_lead_to_crm

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Lead Scoring com LLM",
    description="Qualificação e enriquecimento automático de leads via LLM + JSON estruturado.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/webhook/lead")
def receive_lead(payload: dict):
    # 1. Validação estrutural do payload recebido do formulário/pesquisa.
    try:
        lead = LeadInput(**payload)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    # 2. Qualificação via LLM (saída já validada em ScoreOutput).
    try:
        score_result = score_lead(lead.model_dump())
    except Exception as e:
        logging.exception("Erro ao qualificar lead via LLM")
        raise HTTPException(status_code=502, detail=f"Erro na qualificação: {e}")

    # 3. Roteamento no CRM.
    routing = route_lead_to_crm(score_result.model_dump())

    return {
        "score": score_result.model_dump(),
        "routing": routing,
    }
