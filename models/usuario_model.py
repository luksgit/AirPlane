"""Model de usuário: cadastro, autenticação e alteração dos dados da conta."""
from psycopg import errors
from werkzeug.security import check_password_hash, generate_password_hash

from db import transacao
from models import validacoes
from models.erros import ErroConflito, ErroValidacao

EMAIL_DUPLICADO = "Este e-mail já está cadastrado"


def criar_usuario(nome, email, senha):
    """Cadastra um usuário e devolve {id, nome, email}."""
    nome = validacoes.limpar_texto(nome)
    email = validacoes.normalizar_email(email)
    erros = validacoes.juntar_erros(
        nome=validacoes.validar_nome(nome),
        email=validacoes.validar_email(email),
        senha=validacoes.validar_senha(senha),
    )
    if erros:
        raise ErroValidacao(erros)

    try:
        with transacao() as cur:
            cur.execute(
                "INSERT INTO usuario (nome, email, senha_hash) VALUES (%s, %s, %s)"
                " RETURNING id, nome, email",
                (nome, email, generate_password_hash(senha)),
            )
            return cur.fetchone()
    except errors.UniqueViolation:
        # A restrição UNIQUE do banco é quem garante que o e-mail não se repete.
        raise ErroConflito(EMAIL_DUPLICADO, {"email": EMAIL_DUPLICADO}) from None


def autenticar(email, senha):
    """Devolve {id, nome, email} se e-mail e senha conferem; senão, None."""
    if not isinstance(senha, str):
        return None
    with transacao() as cur:
        cur.execute(
            "SELECT id, nome, email, senha_hash FROM usuario WHERE email = %s",
            (validacoes.normalizar_email(email),),
        )
        usuario = cur.fetchone()
    if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
        return None
    del usuario["senha_hash"]
    return usuario


def buscar_por_id(usuario_id):
    """Devolve {id, nome, email} ou None se o usuário não existir."""
    with transacao() as cur:
        cur.execute("SELECT id, nome, email FROM usuario WHERE id = %s", (usuario_id,))
        return cur.fetchone()


def atualizar_nome(usuario_id, nome):
    """Troca o nome do usuário e devolve {id, nome, email}."""
    nome = validacoes.limpar_texto(nome)
    erro = validacoes.validar_nome(nome)
    if erro:
        raise ErroValidacao({"nome": erro})

    with transacao() as cur:
        cur.execute(
            "UPDATE usuario SET nome = %s WHERE id = %s RETURNING id, nome, email",
            (nome, usuario_id),
        )
        return cur.fetchone()


def alterar_senha(usuario_id, senha_atual, nova_senha):
    """Troca a senha, exigindo a senha atual correta e uma nova senha diferente."""
    erros = validacoes.juntar_erros(
        senha_atual=None if senha_atual else "Informe sua senha atual",
        nova_senha=validacoes.validar_senha(nova_senha),
    )
    if erros:
        raise ErroValidacao(erros)

    with transacao() as cur:
        cur.execute("SELECT senha_hash FROM usuario WHERE id = %s", (usuario_id,))
        usuario = cur.fetchone()
        if usuario is None or not check_password_hash(usuario["senha_hash"], senha_atual):
            raise ErroValidacao({"senha_atual": "Senha atual incorreta"}, "Senha atual incorreta")
        if senha_atual == nova_senha:
            mensagem = "A nova senha deve ser diferente da atual"
            raise ErroValidacao({"nova_senha": mensagem}, mensagem)

        cur.execute(
            "UPDATE usuario SET senha_hash = %s WHERE id = %s",
            (generate_password_hash(nova_senha), usuario_id),
        )
