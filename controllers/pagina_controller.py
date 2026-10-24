"""Páginas HTML do AirPlan e proteção das rotas.

As páginas só entregam o HTML; os dados chegam depois pelo JavaScript, via API.
- Visitante em página interna → vai para /login.
- Usuário logado em /login ou /cadastro → vai para /quadros.
- Quadro inexistente ou de outro usuário → página 404 (sem revelar que existe).
"""
from functools import wraps

from flask import Blueprint, redirect, render_template, url_for

from controllers.sessao import usuario_logado_id
from models import quadro_model

bp = Blueprint("paginas", __name__)


def pagina_nao_encontrada():
    """Resposta da página 404; o botão leva ao Hangar ou ao Login, conforme a sessão."""
    logado = usuario_logado_id() is not None
    return render_template(
        "404.html",
        destino=url_for("paginas.quadros") if logado else url_for("paginas.login"),
        texto_botao="Voltar para o Hangar" if logado else "Voltar para o Login",
    ), 404


def somente_logado(pagina):
    """Página interna: sem sessão, redireciona para o login."""

    @wraps(pagina)
    def verificar(*args, **kwargs):
        if usuario_logado_id() is None:
            return redirect(url_for("paginas.login"))
        return pagina(*args, **kwargs)

    return verificar


def somente_visitante(pagina):
    """Login e cadastro: quem já está logado vai direto para os quadros."""

    @wraps(pagina)
    def verificar(*args, **kwargs):
        if usuario_logado_id() is not None:
            return redirect(url_for("paginas.quadros"))
        return pagina(*args, **kwargs)

    return verificar


@bp.get("/")
def inicio():
    """A raiz leva para os quadros (logado) ou para o login (visitante)."""
    destino = "paginas.quadros" if usuario_logado_id() is not None else "paginas.login"
    return redirect(url_for(destino))


@bp.get("/login")
@somente_visitante
def login():
    return render_template("login.html")


@bp.get("/cadastro")
@somente_visitante
def cadastro():
    return render_template("cadastro.html")


@bp.get("/quadros")
@somente_logado
def quadros():
    return render_template("quadros.html")


@bp.get("/quadros/<int:quadro_id>")
@somente_logado
def quadro(quadro_id):
    if not quadro_model.quadro_pertence_ao_usuario(usuario_logado_id(), quadro_id):
        return pagina_nao_encontrada()
    return render_template("quadro.html", quadro_id=quadro_id)


@bp.get("/perfil")
@somente_logado
def perfil():
    return render_template("perfil.html")
