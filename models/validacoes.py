"""Regras de validação dos campos (as mesmas do front-end).

Cada função `validar_*` devolve a mensagem de erro ou `None` se o valor for válido.
São funções puras: não acessam o banco nem a requisição.
"""
import re
from datetime import date

EMAIL_FORMATO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PRAZO_FORMATO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CORES_ETIQUETA = ("verde", "amarelo", "laranja", "vermelho", "roxo", "azul")


def limpar_texto(valor):
    """Devolve o texto sem espaços nas pontas ('' se não for texto)."""
    return valor.strip() if isinstance(valor, str) else ""


def texto_opcional(valor):
    """Texto sem espaços nas pontas, ou None se vier vazio ou ausente (vira NULL no banco)."""
    return limpar_texto(valor) or None


def normalizar_email(valor):
    """E-mail sem espaços e em minúsculas, como é salvo no banco."""
    return limpar_texto(valor).lower()


def validar_nome(nome):
    if not nome:
        return "Informe seu nome"
    if len(nome) < 2:
        return "O nome deve ter pelo menos 2 caracteres"
    if len(nome) > 100:
        return "O nome deve ter no máximo 100 caracteres"
    return None


def validar_email(email):
    if not email:
        return "Informe seu e-mail"
    if len(email) > 150:
        return "O e-mail deve ter no máximo 150 caracteres"
    if not EMAIL_FORMATO.match(email):
        return "Digite um e-mail válido"
    return None


def validar_senha(senha):
    """Mínimo de 8 caracteres, com pelo menos 1 letra e 1 número."""
    if not isinstance(senha, str) or not senha:
        return "Informe sua senha"
    tem_letra = any(c.isalpha() for c in senha)
    tem_numero = any(c.isdigit() for c in senha)
    if len(senha) < 8 or not tem_letra or not tem_numero:
        return "A senha deve ter no mínimo 8 caracteres, com letras e números"
    return None


def validar_titulo_quadro(titulo):
    if not titulo:
        return "O título do quadro não pode ficar vazio"
    if len(titulo) > 100:
        return "O título do quadro deve ter no máximo 100 caracteres"
    return None


def validar_titulo_coluna(titulo):
    if not titulo:
        return "O título da coluna não pode ficar vazio"
    if len(titulo) > 50:
        return "O título da coluna deve ter no máximo 50 caracteres"
    return None


def validar_titulo_cartao(titulo):
    if not titulo:
        return "Dê um título ao cartão"
    if len(titulo) > 100:
        return "O título do cartão deve ter no máximo 100 caracteres"
    return None


def validar_descricao(descricao):
    """Opcional; até 2000 caracteres."""
    if descricao is not None and len(descricao) > 2000:
        return "A descrição deve ter no máximo 2000 caracteres"
    return None


def validar_prazo(prazo):
    """Opcional; precisa ser uma data que existe, no formato AAAA-MM-DD."""
    if prazo is None:
        return None
    try:
        if PRAZO_FORMATO.match(prazo):
            date.fromisoformat(prazo)
            return None
    except ValueError:
        pass  # Ex.: 2026-02-30 tem o formato certo, mas não existe.
    return "Informe uma data válida"


def validar_cor_etiqueta(cor):
    """Opcional; uma das 6 cores de etiqueta."""
    if cor is not None and cor not in CORES_ETIQUETA:
        return "Escolha uma das cores disponíveis"
    return None


def eh_inteiro(valor, minimo):
    """Diz se o valor é um número inteiro >= minimo (True/False do JSON não contam)."""
    return isinstance(valor, int) and not isinstance(valor, bool) and valor >= minimo


def juntar_erros(**erros_por_campo):
    """Junta os resultados num dicionário só com os campos que têm erro."""
    return {campo: erro for campo, erro in erros_por_campo.items() if erro}
