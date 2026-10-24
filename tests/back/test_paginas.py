"""Testes das páginas HTML: redirecionamentos, proteção e página 404."""
import pytest


def test_raiz_leva_visitante_para_o_login(cliente):
    resposta = cliente.get("/")

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"


def test_raiz_leva_usuario_logado_para_os_quadros(cadastrar):
    resposta = cadastrar().get("/")

    assert resposta.headers["Location"] == "/quadros"


@pytest.mark.parametrize("rota", ["/login", "/cadastro"])
def test_paginas_de_visitante_abrem_sem_sessao(cliente, rota):
    resposta = cliente.get(rota)

    assert resposta.status_code == 200
    assert "text/html" in resposta.content_type


@pytest.mark.parametrize("rota", ["/login", "/cadastro"])
def test_usuario_logado_em_login_ou_cadastro_vai_para_os_quadros(cadastrar, rota):
    resposta = cadastrar().get(rota)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/quadros"


@pytest.mark.parametrize("rota", ["/quadros", "/quadros/1", "/perfil"])
def test_paginas_internas_sem_sessao_vao_para_o_login(cliente, rota):
    resposta = cliente.get(rota)

    assert resposta.status_code == 302
    assert resposta.headers["Location"] == "/login"


@pytest.mark.parametrize("rota", ["/quadros", "/perfil"])
def test_paginas_internas_abrem_com_sessao(cadastrar, rota):
    assert cadastrar().get(rota).status_code == 200


def test_pagina_do_proprio_quadro_abre(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)

    resposta = cliente.get(f"/quadros/{quadro['id']}")

    assert resposta.status_code == 200
    assert f'data-quadro-id="{quadro["id"]}"' in resposta.get_data(as_text=True)


def test_pagina_do_quadro_de_outro_usuario_mostra_404(quadro_da_ana):
    _, bruno, quadro = quadro_da_ana

    resposta = bruno.get(f"/quadros/{quadro['id']}")

    assert resposta.status_code == 404
    assert "Turbulência" in resposta.get_data(as_text=True)


def test_rota_desconhecida_mostra_404_com_volta_para_o_login(cliente):
    resposta = cliente.get("/rota-que-nao-existe")
    html = resposta.get_data(as_text=True)

    assert resposta.status_code == 404
    assert "Voltar para o Login" in html
    assert 'href="/login"' in html


def test_rota_desconhecida_logado_mostra_404_com_volta_para_o_hangar(cadastrar):
    resposta = cadastrar().get("/rota-que-nao-existe")
    html = resposta.get_data(as_text=True)

    assert resposta.status_code == 404
    assert "Voltar para o Hangar" in html
    assert 'href="/quadros"' in html
