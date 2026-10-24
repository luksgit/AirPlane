# Roteiro de teste para os colegas

Olá! Obrigado por testar o **AirPlan**, um gerenciador de tarefas no estilo Kanban (quadros → colunas → cartões).
O teste leva cerca de **20 minutos**. Siga as tarefas abaixo e, sempre que algo der errado, parecer estranho ou for difícil de entender, registre no [formulário de bugs](formulario-de-bugs.md) **com print da tela**.

## Antes de começar

- **Link do app:** `https://<link-do-app-no-render>`
- ⏳ O primeiro acesso pode levar **cerca de 1 minuto** (o servidor gratuito estava "dormindo"). Isso não é bug.
- Use **sua própria conta**: crie uma na tarefa 1. Não use a conta de demonstração.
- Anote o **dispositivo e o navegador** que você está usando (ex.: Windows 11 + Chrome, iPhone + Safari).
- Se puder, faça as tarefas no computador e depois repita algumas no celular.

## Tarefas

| # | Tarefa | O que observar |
|---|---|---|
| 1 | Crie uma conta. Antes, tente enviar o formulário com campos vazios, uma senha curta e senhas diferentes. | As mensagens de erro são claras? O botão mostra "Criando conta…"? |
| 2 | Saia (menu das iniciais → Sair) e entre de novo. Teste também uma senha errada. | A mensagem de senha errada aparece? |
| 3 | Crie um quadro chamado **"Viagem de férias"**. | O quadro abre já com as colunas Embarque, Em voo e Pousou? |
| 4 | Adicione pelo menos **5 cartões** em colunas diferentes (ex.: "Comprar passagem", "Reservar hotel"…). | Dá para adicionar vários seguidos com Enter? |
| 5 | Abra um cartão e preencha **descrição**, **prazo para amanhã** e uma **etiqueta**. Salve. | O cartão mostra a faixa colorida e o selo de prazo **amarelo**? |
| 6 | Coloque em outro cartão um **prazo que já passou**. | Aparece "Atrasado" em vermelho? |
| 7 | No computador, **arraste cartões** entre colunas e dentro da mesma coluna. Recarregue a página (F5). | A ordem continuou igual depois de recarregar? |
| 8 | No celular, mude um cartão de coluna pelo campo **"Mover para"**. | É fácil trocar de coluna deslizando o dedo? |
| 9 | Renomeie uma coluna, crie uma coluna nova e exclua uma coluna que tenha cartões. | O texto de confirmação faz sentido? |
| 10 | Edite um cartão e tente fechar **sem salvar**. | O app pergunta se você quer descartar as alterações? |
| 11 | Volte para "Meus planos de voo", renomeie o quadro e depois crie outro e **exclua**. | Os números de colunas/cartões de cada quadro estão certos? |
| 12 | Em "Meu perfil", troque seu nome e depois sua senha (teste também com a senha atual errada). | O nome muda no círculo das iniciais? |
| 13 | Digite um endereço que não existe, ex.: `/quadros/999999`. | Aparece a página "Turbulência!"? |
| 14 | (Opcional) Use o app **só com o teclado** (Tab, Enter, Esc). | Dá para fazer tudo sem o mouse? |

## Para terminar

1. Preencha o [formulário de bugs](formulario-de-bugs.md), um item por problema encontrado, com print.
2. Responda às perguntas finais do formulário (nota de 1 a 5 e comentário livre).
3. Envie o arquivo (ou os prints) para o Lucas.

> Sugestões de funcionalidades novas também são bem-vindas. Algumas (compartilhar quadros, anexos, modo escuro…) estão fora do escopo deste projeto e vão para o laudo como "não implementadas".
