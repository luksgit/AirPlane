"""Leitura do corpo das requisições."""
from flask import request


def ler_json():
    """Devolve o corpo JSON como dicionário ({} se vier vazio ou inválido).

    Assim um corpo malformado cai na validação normal (400) em vez de quebrar a rota.
    """
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}
