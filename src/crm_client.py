"""
Simula o envio do resultado de qualificação para um CRM.

Substitua o corpo de `route_lead_to_crm` pela chamada real da API do seu CRM
(HubSpot, RD Station, Pipedrive, Salesforce etc.), usando CRM_WEBHOOK_URL do .env.
"""
import os
import logging

logger = logging.getLogger("crm_client")

CRM_WEBHOOK_URL = os.getenv("CRM_WEBHOOK_URL", "")


def route_lead_to_crm(score_result: dict) -> dict:
    """
    Decide o roteamento com base na classificação e "envia" (aqui, apenas loga)
    para o CRM. Troque o `logger.info` por uma chamada HTTP real, ex:

        import requests
        requests.post(CRM_WEBHOOK_URL, json=score_result, timeout=10)
    """
    classification = score_result["classification"]

    routing_map = {
        "hot": "Fila prioritária de SDR — contato em até 1h",
        "warm": "Fila de nutrição ativa — contato em até 24h",
        "cold": "Fluxo de nutrição por e-mail (automação de marketing)",
    }

    destino = routing_map.get(classification, "Fila padrão")

    logger.info(
        "Roteando lead %s | score=%s | classification=%s | destino=%s",
        score_result["lead_id"],
        score_result["score"],
        classification,
        destino,
    )

    return {"status": "roteado", "destino": destino}
