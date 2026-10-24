# UML: Diagrama de classes

## 1. Classes do domínio

As entidades do negócio e seus relacionamentos. No código não há ORM: cada entidade é uma tabela do banco, e as operações ficam nas funções do *model* correspondente (próxima seção).

```mermaid
classDiagram
    direction LR
    class Usuario {
        +int id
        +str nome
        +str email
        -str senha_hash
        +datetime criado_em
        +criar(nome, email, senha)
        +autenticar(email, senha)
        +atualizarNome(nome)
        +alterarSenha(senhaAtual, novaSenha)
    }
    class Quadro {
        +int id
        +str titulo
        +datetime criado_em
        +criar(titulo)
        +renomear(titulo)
        +excluir()
        +totalColunas() int
        +totalCartoes() int
    }
    class Coluna {
        +int id
        +str titulo
        +int posicao
        +datetime criado_em
        +criar(titulo)
        +renomear(titulo)
        +excluir()
    }
    class Cartao {
        +int id
        +str titulo
        +str descricao
        +date prazo
        +CorEtiqueta cor_etiqueta
        +int posicao
        +datetime criado_em
        +criar(titulo)
        +atualizar(dados)
        +mover(coluna, posicao)
        +excluir()
    }
    class CorEtiqueta {
        <<enumeration>>
        verde
        amarelo
        laranja
        vermelho
        roxo
        azul
    }

    Usuario "1" *-- "0..*" Quadro : possui
    Quadro "1" *-- "0..*" Coluna : contém
    Coluna "1" *-- "0..*" Cartao : contém
    Cartao ..> CorEtiqueta
```

A **composição** (losango cheio) indica que a parte não existe sem o todo: excluir um quadro exclui suas colunas e cartões.

---

## 2. Classes da arquitetura (MVC)

Como o back-end é escrito em Python com funções (sem classes de entidade), cada **módulo** aparece abaixo como uma classe com estereótipo. A separação mostra o padrão MVC exigido:

- **Model:** SQL e regras de negócio. Não conhece HTTP.
- **Controller:** recebe a requisição, chama o model e devolve JSON ou HTML. Não escreve SQL.
- **View:** templates HTML, CSS e JavaScript.

```mermaid
classDiagram
    direction TB

    class auth_controller {
        <<controller>>
        +cadastro() POST /api/auth/cadastro
        +login() POST /api/auth/login
        +logout() POST /api/auth/logout
    }
    class usuario_controller {
        <<controller>>
        +ver_perfil() GET /api/usuarios/me
        +atualizar_perfil() PUT /api/usuarios/me
        +alterar_senha() PUT /api/usuarios/me/senha
    }
    class quadro_controller {
        <<controller>>
        +listar() GET /api/quadros
        +criar() POST /api/quadros
        +ver(id) GET /api/quadros/id
        +renomear(id) PUT
        +excluir(id) DELETE
    }
    class coluna_controller {
        <<controller>>
        +criar(quadro_id) POST /api/quadros/id/colunas
        +renomear(id) PUT /api/colunas/id
        +excluir(id) DELETE
    }
    class cartao_controller {
        <<controller>>
        +criar(coluna_id) POST /api/colunas/id/cartoes
        +atualizar(id) PUT /api/cartoes/id
        +excluir(id) DELETE
        +mover(id) PUT /api/cartoes/id/mover
    }
    class pagina_controller {
        <<controller>>
        +login() +cadastro() +quadros()
        +quadro(id) +perfil()
        +pagina_nao_encontrada()
    }
    class sessao {
        <<controller helper>>
        +login_obrigatorio(rota)
        +iniciar_sessao(usuario)
        +usuario_logado_id()
    }
    class tratador_erros {
        <<controller helper>>
        +registrar_tratadores_de_erro(app)
    }

    class usuario_model {
        <<model>>
        +criar_usuario()
        +autenticar()
        +buscar_por_id()
        +atualizar_nome()
        +alterar_senha()
    }
    class quadro_model {
        <<model>>
        +listar_quadros()
        +criar_quadro()
        +buscar_quadro_completo()
        +renomear_quadro()
        +excluir_quadro()
    }
    class coluna_model {
        <<model>>
        +criar_coluna()
        +renomear_coluna()
        +excluir_coluna()
    }
    class cartao_model {
        <<model>>
        +criar_cartao()
        +atualizar_cartao()
        +excluir_cartao()
        +mover_cartao()
    }
    class validacoes {
        <<model helper>>
        +validar_nome() +validar_email()
        +validar_senha() +validar_titulo_quadro()
        +validar_titulo_coluna() +validar_titulo_cartao()
    }
    class erros {
        <<model helper>>
        ErroValidacao
        ErroConflito
        NaoEncontrado
    }
    class db {
        <<infra>>
        +transacao()
        +conectar(url)
    }
    class Views {
        <<view>>
        views/templates (HTML com Jinja)
        public/static/css (estilos)
        public/static/js (telas e utils)
    }

    auth_controller --> usuario_model
    usuario_controller --> usuario_model
    quadro_controller --> quadro_model
    coluna_controller --> coluna_model
    cartao_controller --> cartao_model
    pagina_controller --> quadro_model
    pagina_controller --> Views : render_template
    auth_controller ..> sessao
    quadro_controller ..> sessao
    usuario_model ..> validacoes
    quadro_model ..> validacoes
    coluna_model ..> validacoes
    cartao_model ..> validacoes
    usuario_model ..> erros
    cartao_model ..> erros
    tratador_erros ..> erros : traduz para 400/404/409
    usuario_model --> db
    quadro_model --> db
    coluna_model --> db
    cartao_model --> db
    Views ..> auth_controller : fetch (JSON)
    Views ..> quadro_controller : fetch (JSON)
    Views ..> cartao_controller : fetch (JSON)
```
