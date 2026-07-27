"""
Carrega as regras do Perfil de Cliente Ideal (ICP) a partir de config/icp.json.

Manter essas regras em um JSON separado (em vez de "hardcoded" no código ou
espalhadas no prompt) permite que times de marketing/vendas ajustem critérios
sem precisar mexer em código Python.
"""
import json
from pathlib import Path
from functools import lru_cache

ICP_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "icp.json"


@lru_cache
def load_icp_config() -> dict:
    with open(ICP_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
