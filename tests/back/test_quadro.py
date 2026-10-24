"""Testes dos quadros: CRUD, colunas padrão, totais, cascata e isolamento entre usuários."""
from datetime import date

import pytest


# --- Criar ------------------------------------------------------------------

def test_criar_quadro_retorna_201(cadastrar):
    cliente = cadastrar()

    resposta = cliente.post("/api/quadros", json={"titulo": "  Viagem de férias  "})

    assert resposta.status_code == 201
    assert resposta.get_json() == {"id": 1, "titulo": "Viagem de férias"}


def test_criar_quadro_ja_vem_com_as_tres_colunas_padrao(cadastrar, criar_quadro):
    quadro = criar_quadro(cadastrar())

    colunas = [(c["titulo"], c["posicao"], c["cartoes"]) for c in quadro["colunas"]]
    assert colunas == [("Embarque", 0, []), ("Em voo", 1, []), ("Pousou", 2, [])]


@pytest.mark.parametrize(
    "titulo, mensagem",
    [
        ("", "O título do quadro não pode ficar vazio"),
        ("    ", "O título do quadro não pode ficar vazio"),
        (None, "O título do quadro não pode ficar vazio"),
        ("A" * 101, "O título do quadro deve ter no máximo 100 caracteres"),
    ],
)
def test_criar_quadro_valida_titulo(cadastrar, contar, titulo, mensagem):
    cliente = cadastrar()

    resposta = cliente.post("/api/quadros", json={"titulo": titulo})

    assert resposta.status_code == 400
    assert resposta.get_json() == {"erro": mensagem, "campos": {"titulo": mensagem}}
    assert contar("quadro") == 0


# --- Listar -----------------------------------------------------------------

def test_listar_sem_quadros_retorna_lista_vazia(cadastrar):
    assert cadastrar().get("/api/quadros").get_json() == []


def test_listar_quadros_em_ordem_de_criacao_com_totais(cadastrar, criar_quadro, inserir_cartao):
    cliente = cadastrar()
    primeiro = criar_quadro(cliente, "Primeiro")
    criar_quadro(cliente, "Segundo")
    embarque, em_voo, _ = primeiro["colunas"]
    inserir_cartao(embarque["id"], "Tarefa 1", 0)
    inserir_cartao(embarque["id"], "Tarefa 2", 1)
    inserir_cartao(em_voo["id"], "Tarefa 3", 0)

    resposta = cliente.get("/api/quadros")

    assert resposta.status_code == 200
    assert resposta.get_json() == [
        {"id": 1, "titulo": "Primeiro", "total_colunas": 3, "total_cartoes": 3},
        {"id": 2, "titulo": "Segundo", "total_colunas": 3, "total_cartoes": 0},
    ]


# --- Ver completo -----------------------------------------------------------

def test_ver_quadro_traz_cartoes_em_ordem_dentro_de_cada_coluna(cadastrar, criar_quadro, inserir_cartao):
    cliente = cadastrar()
    quadro = criar_quadro(cliente, "Estudos")
    embarque, _, pousou = quadro["colunas"]
    inserir_cartao(embarque["id"], "Segundo", 1)
    inserir_cartao(embarque["id"], "Primeiro", 0, prazo=date(2026, 11, 17), cor_etiqueta="roxo")
    inserir_cartao(pousou["id"], "Feito", 0)

    resposta = cliente.get(f"/api/quadros/{quadro['id']}")

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["titulo"] == "Estudos"
    cartoes_embarque = corpo["colunas"][0]["cartoes"]
    assert [c["titulo"] for c in cartoes_embarque] == ["Primeiro", "Segundo"]
    assert cartoes_embarque[0] == {
        "id": 2,
        "titulo": "Primeiro",
        "descricao": None,
        "prazo": "2026-11-17",
        "cor_etiqueta": "roxo",
        "posicao": 0,
    }
    assert corpo["colunas"][1]["cartoes"] == []
    assert [c["titulo"] for c in corpo["colunas"][2]["cartoes"]] == ["Feito"]


def test_ver_quadro_inexistente_retorna_404(cadastrar):
    resposta = cadastrar().get("/api/quadros/999")

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Quadro não encontrado"}


# --- Renomear ---------------------------------------------------------------

def test_renomear_quadro(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente, "Antigo")

    resposta = cliente.put(f"/api/quadros/{quadro['id']}", json={"titulo": " Novo nome "})

    assert resposta.status_code == 200
    assert resposta.get_json() == {"id": quadro["id"], "titulo": "Novo nome"}
    assert cliente.get("/api/quadros").get_json()[0]["titulo"] == "Novo nome"


def test_renomear_quadro_com_titulo_vazio_retorna_400(cadastrar, criar_quadro):
    cliente = cadastrar()
    quadro = criar_quadro(cliente, "Antigo")

    resposta = cliente.put(f"/api/quadros/{quadro['id']}", json={"titulo": "  "})

    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "O título do quadro não pode ficar vazio"
    assert cliente.get("/api/quadros").get_json()[0]["titulo"] == "Antigo"


def test_renomear_quadro_inexistente_retorna_404(cadastrar):
    resposta = cadastrar().put("/api/quadros/999", json={"titulo": "Qualquer"})

    assert resposta.status_code == 404


# --- Excluir ----------------------------------------------------------------

def test_excluir_quadro_apaga_colunas_e_cartoes_em_cascata(cadastrar, criar_quadro, inserir_cartao, contar):
    cliente = cadastrar()
    quadro = criar_quadro(cliente)
    outro = criar_quadro(cliente, "Fica")
    inserir_cartao(quadro["colunas"][0]["id"], "Some junto", 0)
    inserir_cartao(outro["colunas"][0]["id"], "Continua", 0)

    resposta = cliente.delete(f"/api/quadros/{quadro['id']}")

    assert resposta.status_code == 204
    assert cliente.get(f"/api/quadros/{quadro['id']}").status_code == 404
    assert contar("coluna") == 3
    assert contar("cartao") == 1


def test_excluir_quadro_inexistente_retorna_404(cadastrar):
    assert cadastrar().delete("/api/quadros/999").status_code == 404


def test_excluir_usuario_apaga_quadros_em_cascata(cadastrar, criar_quadro, conexao_teste, inserir_cartao, contar):
    quadro = criar_quadro(cadastrar())
    inserir_cartao(quadro["colunas"][0]["id"], "Tarefa", 0)

    conexao_teste.execute("DELETE FROM usuario")

    assert [contar(t) for t in ("quadro", "coluna", "cartao")] == [0, 0, 0]


# --- Isolamento entre usuários ----------------------------------------------

def test_usuario_nao_ve_quadros_de_outro_na_lista(quadro_da_ana):
    _, bruno, _ = quadro_da_ana

    assert bruno.get("/api/quadros").get_json() == []


@pytest.mark.parametrize(
    "metodo, corpo",
    [("get", None), ("put", {"titulo": "Invadido"}), ("delete", None)],
)
def test_usuario_nao_acessa_quadro_de_outro(quadro_da_ana, metodo, corpo):
    ana, bruno, quadro = quadro_da_ana

    resposta = getattr(bruno, metodo)(f"/api/quadros/{quadro['id']}", json=corpo)

    assert resposta.status_code == 404
    assert resposta.get_json() == {"erro": "Quadro não encontrado"}
    assert ana.get(f"/api/quadros/{quadro['id']}").get_json()["titulo"] == "Quadro da Ana"
