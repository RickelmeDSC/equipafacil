# Interface definitiva — DEV-07 (EQF-19)

> **Situação:** implementado na branch `feat/frontend-eqf-19-interface`, a partir da `main` em `5995c8d`. **Aguarda revisão cruzada (Rickelme) e homologação visual (equipe de Testes).** Substitui os 10 templates provisórios do backend. Nenhum arquivo `.py` foi alterado e nenhum teste do backend foi ajustado: a suíte passa como estava.
>
> O contrato técnico (PR #2) continua **proposta**; esta implementação consome as rotas, variáveis e campos que já estão na `main` e segue [`integracao-frontend-dev07.md`](integracao-frontend-dev07.md).

Escopo: P01–P10, com RF001–RF008 e as decisões D10–D15, I1–I5. Fora do escopo: views, forms, services, urls, models, migrations, dependências Python, banco e deploy.

## Arquivos

| Arquivo | Conteúdo |
|---------|----------|
| `templates/base.html` | Blocos `title` e `content` (contrato), mais `navegacao`, `rodape`, `classe_do_corpo`, `classe_do_main` e `scripts`. Link de salto para o conteúdo |
| `templates/includes/navbar.html` | Equipamentos, Clientes, Novo aluguel, Histórico; nome do funcionário; Sair por POST com `csrf_token` |
| `templates/includes/messages.html` | `messages` em `alert-{{ message.tags }}` |
| `templates/includes/form_errors.html` | `form.non_field_errors` em um alerta |
| `templates/includes/campo.html` | Um campo: rótulo, `{{ campo }}`, erros em `invalid-feedback` e ajuda opcional |
| `templates/registration/login.html`, `templates/inicio.html` | P10 e P01 |
| `templates/equipamentos/{lista,formulario,acoes}.html` | P02, P03, P04 |
| `templates/clientes/{lista,formulario}.html` | P05, P06 |
| `templates/alugueis/{formulario,historico,devolver}.html` | P07, P08, P09 |
| `static/vendor/bootstrap/bootstrap.min.css` | Bootstrap 5.3.8 local, sem CDN (ver o `README.md` da pasta) |
| `static/css/app.css` | Camada de estilo do projeto sobre o Bootstrap |
| `static/js/previa-aluguel.js` | Estimativa informativa de P07 |

## Decisões de interface tomadas aqui

Resolvem a seção 6 (“Decisões de interface pendentes”) do guia do DEV-07. **Todas dependem de aceite de Rickelme**; nenhuma altera requisito, regra ou mensagem do EQF-5.

1. **Bootstrap 5.3.8, só o CSS, versionado em `static/vendor/bootstrap/`.** Sem CDN. O `bundle.min.js` não entrou porque nenhuma tela usa componente com JavaScript. A última linha do arquivo (`sourceMappingURL`) foi removida: o `collectstatic` com `CompressedManifestStaticFilesStorage` resolveria a referência e falharia sem o `.map`. Procedência e SHA-256 em `static/vendor/bootstrap/README.md`.
2. **Nenhuma tela depende de JavaScript.** A navegação não usa menu colapsável (os itens quebram em linha em tela estreita), e a confirmação de exclusão de P04 é um bloco `<details>` com `confirmacao=sim`, não um modal — um modal do Bootstrap ficaria inacessível sem o bundle.
3. **P07 mantém o botão de registro só depois da prévia**, como o backend já fazia (há teste nos dois sentidos). A estimativa ao vivo em JavaScript é um extra informativo: aparece abaixo das datas, é rotulada como estimativa e remete ao botão “Calcular resumo”. Diárias, diária e total exibidos como resultado vêm sempre do servidor.
4. **Selo de situação do histórico por CSS, sem elemento novo.** O texto da situação continua filho direto do `<td>`; a cor e o ponto vêm de `td[data-situacao]`. Cores: ativo verde, atrasado vermelho, encerrado cinza, encerrado com atraso âmbar. Foi essa escolha que evitou mexer nos testes do backend.
5. **`novalidate` em todos os formulários.** Sem isso, o navegador bloqueia o envio e mostra bolhas próprias; com isso, toda recusa vem do servidor com os textos do EQF-5 — o que a equipe de Testes espera ver nos cenários CT. `required`, `min`, `max` e `disabled` continuam no HTML, vindos do Django, como orientação.
6. **Sem máscara de CPF e telefone.** Máscara exigiria JavaScript e o backend já aceita as duas formas de digitação e devolve o valor formatado. O formato esperado aparece como texto de ajuda.
7. **P04 mostra Inativar ou Reativar conforme a situação** (e o motivo de bloqueio quando houver), em vez das três seções sempre visíveis.
8. **Sem máscaras, ícones, fontes externas ou qualquer requisição a terceiros.** Só os dois arquivos locais de CSS e um de JavaScript.

## Marcação que o backend verifica por teste

Estes pontos são contrato verificado pela suíte: mudá-los quebra teste e exige revisão do backend no mesmo PR (seção 5 do guia do DEV-07).

| Onde | O que não pode mudar |
|------|----------------------|
| P07 | `name="acao" value="previa"` e `name="acao" value="registrar"` nessa ordem de atributos e com a prévia antes no HTML; o botão de registro só com `resumo`; o rótulo `Total previsto: R$ …`; a frase “não pode ser cancelado”; `json_script` com id `diarias-equipamentos` |
| P08 | Situação como texto direto do `<td>` (`>Ativo</td>`); célula do equipamento como `código — nome` com `(inativo)` no mesmo texto; histórico vazio sem nenhum “R$” na página (inclusive nos cabeçalhos) e sem “Registrar devolução” |
| P05 | Nenhum `name="q"` na página (D14) |
| P02 | As palavras Ativo, Inativo, Disponível e Indisponível |
| P03, P06 | A explicação do código e do CPF bloqueados, com os textos do EQF-5 |
| P09 | “Este aluguel já foi encerrado.” na página de aluguel encerrado; `min` e `max` do campo de data |
| P01, P10 | Nome do usuário escapado; Sair por POST com `csrf_token`; `method="post"` e `csrf_token` no login, sem credencial de exemplo |
| Listas | Nenhum acesso novo a relação nos templates: P02, P05 e P08 fazem uma consulta só |

## Textos novos do frontend

Fora dos rótulos de navegação, cabeçalhos de tabela e botões, estas frases foram escritas aqui e **não vêm do EQF-5**. Ficam registradas para a equipe de Requisitos avaliar se querem redação própria; nenhuma substitui mensagem de validação.

| Tela | Texto |
|------|-------|
| P10 | “Acesso do funcionário”; “As contas são criadas pelo administrador do sistema.” (D15) |
| P01 | “Sessão iniciada como …”; a descrição de cada uma das quatro áreas |
| P02 | “Equipamentos ativos e inativos da locadora.” |
| P03 | “O equipamento é cadastrado ativo e fica disponível para aluguel.”; “Use vírgula para os centavos. Exemplo: 35,50.” |
| P04 | “O equipamento inativo deixa de ficar disponível para novos aluguéis e continua no histórico.”; “O equipamento reativado volta a ficar disponível para aluguel. O histórico não é alterado.”; “A exclusão apaga o equipamento do sistema e só é possível enquanto ele não tiver histórico de locação.”; “Confirmar a exclusão de … ?”; “Esta ação é definitiva e não pode ser desfeita.” |
| P05 | “Clientes cadastrados, em ordem alfabética.” |
| P06 | “Com ou sem pontos e hífen.”; “Com DDD, 10 ou 11 dígitos. Exemplo: (81) 99999-8888.” |
| P07 | “Hoje ou uma data futura.”; “Resumo do aluguel”; “Estimativa: … Use ‘Calcular resumo’ para o valor do servidor.” |
| P08 | “Todos os aluguéis registrados, do mais recente para o mais antigo.” |
| P09 | “A devolução é registrada uma única vez e não pode ser corrigida depois. Não há multa por atraso.” |
| Todas | “(opcional)” nos campos não obrigatórios; “—” em célula sem valor; rodapé “EquipaFácil — gestão de aluguel de equipamentos.” |

Os textos provisórios que já estavam nos templates do backend e continuam iguais: o aviso de não cancelamento, “Nenhum cliente cadastrado.”, “Nenhum equipamento disponível para aluguel.” e a explicação da devolução antes da retirada.

## Verificação feita

| Verificação | Resultado |
|-------------|-----------|
| `python manage.py test` (SQLite) | 377 testes, OK, 24 pulados — igual à baseline da `main` antes da mudança |
| `ruff check .` e `black --check .` | Sem alteração a relatar (nenhum `.py` foi tocado) |
| `collectstatic` com `CompressedManifestStaticFilesStorage` | 131 arquivos, 393 pós-processados, sem erro — é o que o job Gunicorn da CI faz |

Não verificado nesta etapa: PostgreSQL local (os 24 testes pulados), navegação manual no navegador, responsividade medida em dispositivo real e leitor de tela.

## Pendências

1. **Homologação visual** pela equipe de Testes e **revisão cruzada** de Rickelme antes do merge.
2. **Aceite das oito decisões** da seção “Decisões de interface tomadas aqui”, principalmente a versão do Bootstrap sem o bundle, o `novalidate` e o `<details>` de P04.
3. **Redação dos textos novos** com a equipe de Requisitos, se ela quiser padronizar.
4. Capturas de tela para o PR: dependem de rodar o servidor local com dados fictícios.
5. Nada de deploy: não existe banco Neon nem serviço no Render, e o deploy depende de autorização de Rickelme.
