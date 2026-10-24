"""Testes das colunas: criar no final, renomear, excluir reordenando e isolamento."""
import pytest


def titulos_e_posicoes(cliente, quadro_id):
    """Colunas do quadro como [(titulo, posicao), ...], na ordem em que aparecem."""
    quadro = cliente.get(f"/api/quadros/{quadro_id}").get_json()
    return [(c["titulo"], c["posicao"]) for c in quadro["colunas"]]


# --- Criar ------------------------------------------------------------------

def test_criar_coluna_vai_para_o_final(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)

    resposta = cliente.post(f"/api/quadros/{quadro['id']}/colunas", json={"titulo": "  Revisão  "})

    assert resposta.status_code == 201
    assert resposta.get_json() == {"id": 4, "titulo": "Revisão", "posicao": 3}
    assert titulos_e_posicoes(cliente, quadro["id"]) == [
        ("Embarque", 0), ("Em voo", 1), ("Pousou", 2), ("Revisão", 3),
    ]


@pytest.mark.parametrize(
    "titulo, mensagem",
    [
        ("", "O título da coluna não pode ficar vazio"),
        ("   ", "O título da coluna não pode ficar vazio"),
        ("A" * 51, "O título da coluna deve ter no máximo 50 caracteres"),
    ],
)
def test_criar_coluna_valida_titulo(cadastrar, criar_quadro, contar, titulo, mensagem):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)

    resposta = cliente.post(f"/api/quadros/{quadro['id']}/colunas", json={"titulo": titulo})

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": mensagem, "campos": {"titulo": mensagem}}
    assert contar("coluna") == 3


def test_criar_coluna_em_quadro_inexistente_retorna_404(cadastrar):
    resposta = cadastrar().post("/api/quadros/999/colunas", json={"titulo": "Nova"})

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Quadro não encontrado"}


# --- Renomear ---------------------------------------------------------------

def test_renomear_coluna(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    em_voo = quadro["colunas"][1]

    resposta = cliente.put(f"/api/colunas/{em_voo['id']}", json={"titulo": " Decolando "})

    assert resposta.status_code == 200
    assert resposta.get_json() == {"id": em_voo["id"], "titulo": "Decolando", "posicao": 1}


def test_renomear_coluna_com_titulo_vazio_retorna_400(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)

    resposta = cliente.put(f"/api/colunas/{quadro['colunas'][0]['id']}", json={"titulo": ""})

    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "O título da coluna não pode ficar vazio"
    assert titulos_e_posicoes(cliente, quadro["id"])[0] == ("Embarque", 0)


def test_renomear_coluna_inexistente_retorna_404(cadastrar):
    resposta = cadastrar().put("/api/colunas/999", json={"titulo": "Nova"})

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Coluna não encontrada"}


# --- Excluir ----------------------------------------------------------------

def test_excluir_coluna_do_meio_reordena_as_seguintes(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    cliente.post(f"/api/quadros/{quadro['id']}/colunas", json={"titulo": "Revisão"})

    resposta = cliente.delete(f"/api/colunas/{quadro['colunas'][1]['id']}")

    assert resposta.status_code == 204
    assert titulos_e_posicoes(cliente, quadro["id"]) == [("Embarque", 0), ("Pousou", 1), ("Revisão", 2)]


def test_criar_depois_de_excluir_mantem_posicoes_continuas(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    cliente.delete(f"/api/colunas/{quadro['colunas'][0]['id']}")

    resposta = cliente.post(f"/api/quadros/{quadro['id']}/colunas", json={"titulo": "Nova"})

    assert resposta.get_json()["posicao"] == 2
    assert titulos_e_posicoes(cliente, quadro["id"]) == [("Em voo", 0), ("Pousou", 1), ("Nova", 2)]


def test_excluir_coluna_apaga_somente_os_cartoes_dela(cadastrar, criar_quadro, inserir_cartao, contar):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    embarque, em_voo, _ = quadro["colunas"]
    inserir_cartao(embarque["id"], "Some junto", 0)
    inserir_cartao(embarque["id"], "Some junto 2", 1)
    inserir_cartao(em_voo["id"], "Continua", 0)

    cliente.delete(f"/api/colunas/{embarque['id']}")

    assert contar("cartao") == 1


def test_pode_excluir_todas_as_colunas(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)

    for coluna in quadro["colunas"]:
        assert cliente.delete(f"/api/colunas/{coluna['id']}").status_code == 204

    assert titulos_e_posicoes(cliente, quadro["id"]) == []


def test_excluir_coluna_inexistente_retorna_404(cadastrar):
    assert cadastrar().delete("/api/colunas/999").status_code == 404


# --- Isolamento entre usuários ----------------------------------------------

def test_usuario_nao_cria_coluna_no_quadro_de_outro(quadro_da_ana, contar):
    _, bruno, quadro = quadro_da_ana

    resposta = bruno.post(f"/api/quadros/{quadro['id']}/colunas", json={"titulo": "Invasora"})

    assert resposta.status_code == 404
    assert contar("coluna") == 3


@pytest.mark.parametrize("metodo, corpo", [("put", {"titulo": "Invadida"}), ("delete", None)])
def test_usuario_nao_altera_coluna_de_outro(quadro_da_ana, metodo, corpo):
    ana, bruno, quadro = quadro_da_ana

    resposta = getattr(bruno, metodo)(f"/api/colunas/{quadro['colunas'][0]['id']}", json=corpo)

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Coluna não encontrada"}
    assert titulos_e_posicoes(ana, quadro["id"]) == [("Embarque", 0), ("Em voo", 1), ("Pousou", 2)]
