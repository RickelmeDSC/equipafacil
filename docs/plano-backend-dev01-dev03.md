# Plano backend — DEV-01 a DEV-03

> **PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.2 — 01/11/2026, reconciliada com a auditoria do Jira de 01/11/2026 e com o Documento de Requisitos v1.1. Planejamento apenas: **nenhuma atividade foi iniciada nem concluída** e não existe código Django no repositório. Este documento não altera status, prazos nem prioridades do Jira.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [modelagem proposta](modelagem-proposta.md).

## 1. Escopo oficial (Jira)

| Atividade | Jira | Escopo oficial | Prazo | Dependência registrada |
|-----------|------|----------------|-------|------------------------|
| DEV-01 | EQF-13 | Definir apps Django; justificar a arquitetura; documentar estrutura e convenções; preparar decisões para registro no Jira | 06/11/2026 | — |
| DEV-02 | EQF-14 | Ambiente virtual; dependências; projeto Django funcional; configurações; instruções de execução | 07/11/2026 | — |
| DEV-03 | EQF-15 | Models de Equipamento, Cliente e Aluguel; RN001–RN004; migrations; diagrama de dados | 08/11/2026 | REQ-04 (EQF-10), em andamento na auditoria |
| DEV-04 | EQF-16 | Equipamentos: RF001–RF004, CT01–CT08 | Conferir no Jira | — |
| DEV-05 | EQF-17 | Clientes: RF005, CT09–CT10 | Conferir no Jira | — |
| DEV-06 | EQF-18 | Aluguel e devolução: RF006–RF007, CT11–CT14 | Conferir no Jira | — |
| DEV-07 | EQF-19 | Histórico: RF008, CT15–CT16 | Conferir no Jira | — |
| DEV-08 | EQF-20 | Deploy no Render, banco no Neon | Conferir no Jira | — |

Na auditoria, DEV-01 ainda não tinha evidência de execução registrada na atividade. O resumo da seção 9 serve para essa futura atualização, feita por Rickelme.

## 2. Autenticação no planejamento

O requisito transversal de autenticação (D1, coberto pela cobertura complementar FC12) não aparece no escopo oficial de DEV-01, DEV-02 ou DEV-03. **Proposta:** tratar a configuração de login, logout e proteção das rotas em DEV-02 ("configurações" e "projeto Django funcional"), com os testes de FC12 junto. Isso precisa ser registrado no Jira por Rickelme; até lá, é uma lacuna de planejamento.

## 3. Como DEV-01 atende o escopo oficial

| Item do escopo | Onde está |
|----------------|-----------|
| Definir apps Django | [Contrato, seção 2](contrato-tecnico-frontend-backend.md#2-arquitetura-proposta-dev-01): `equipamentos`, `clientes` e `alugueis` |
| Justificar a arquitetura | Contrato, seção 2 (justificativa) e seção 3 (autenticação) |
| Documentar estrutura e convenções | Contrato, seções 4 a 8; [modelagem](modelagem-proposta.md) |
| Preparar decisões para registro no Jira | Seção 9 deste plano |

**Pronto quando (proposta):** aceite registrado de Rickelme e Raphael no contrato e decisões da seção 9 registradas no EQF-13.

## 4. Propostas para DEV-02 e DEV-03

**DEV-02 — fundação do projeto (dentro do escopo oficial):**

- Ambiente virtual criado explicitamente com o Python 3.13 (`py -3.13 -m venv .venv`), por haver outras instalações de Python na máquina de Rickelme.
- Dependências fixadas (seção 7) e `.env.example` com valores fictícios.
- Projeto `config` e apps `equipamentos`, `clientes` e `alugueis`; `settings.py` lendo variáveis de ambiente; `TIME_ZONE`, `LANGUAGE_CODE` e autenticação conforme o contrato.
- Diretórios `templates/` e `static/` criados vazios para Raphael.
- Instruções de execução no README.
- **Pronto quando (proposta):** `python manage.py check` e `python manage.py test` rodam num ambiente limpo seguindo as instruções, sem segredo versionado.

**DEV-03 — modelos e regras (dentro do escopo oficial):**

- Models, restrições e migrations conforme a [modelagem](modelagem-proposta.md); serviços com RN001–RN004 e proteção contra concorrência; diagrama de dados.
- Depende de REQ-04 (EQF-10) concluído, pois é a atividade de regras de negócio.
- **Pronto quando (proposta):** restrições verificadas em PostgreSQL e teste de dois aluguéis simultâneos do mesmo equipamento passando.

## 5. Dependências entre atividades

1. **DEV-01** → **DEV-02** → **DEV-03** (DEV-03 também depende de REQ-04, EQF-10).
2. **DEV-04** e **DEV-05** dependem de DEV-03 e podem andar em paralelo.
3. **DEV-06** depende de DEV-04 e DEV-05.
4. **DEV-07** depende de DEV-06.
5. **DEV-08:** a preparação de Neon e Render pode começar depois de DEV-02; o deploy final depende de DEV-07 e de autorização explícita.
6. **Frontend (Raphael):** design estático pode começar já; a integração de cada tela depende do contrato aceito e da atividade DEV correspondente.

## 6. Cronograma sugerido

Os prazos oficiais de DEV-01 a DEV-03 vão até 08/11, o que deixa sete dias para DEV-04 a DEV-08. A sugestão é antecipar as três primeiras sem mudar os prazos do Jira; prioridades do Jira permanecem como estão (I4).

| Período sugerido | Backend (Rickelme) | Prazo oficial | Frontend (Raphael) |
|------------------|--------------------|---------------|--------------------|
| 02/11 a 03/11 | DEV-01: aceite do contrato; primeira entrega acadêmica em 03/11 | 06/11 | Ler repositório e guia; design estático |
| 03/11 a 04/11 | DEV-02 | 07/11 | Layout base e login em HTML estático |
| 04/11 a 06/11 | DEV-03 (se REQ-04 estiver concluída) | 08/11 | Telas de equipamentos e clientes em HTML estático |
| 06/11 a 09/11 | DEV-04 e DEV-05 | Conferir | Integrar equipamentos e clientes |
| 09/11 a 11/11 | DEV-06 | Conferir | Integrar aluguel e devolução |
| 11/11 a 12/11 | DEV-07 | Conferir | Integrar histórico |
| 12/11 a 14/11 | DEV-08 e apoio aos testes (QA-06, EQF-26) | Conferir | Revisão responsiva e de acessibilidade |
| 14/11 a 15/11 | Correções e entrega final | 15/11 | Correções e entrega final |

## 7. Testes e dependências (propostas para DEV-02)

**Testes:** `python manage.py test` com `TestCase` do Django, sem dependência extra; banco de testes PostgreSQL (necessário para concorrência); datas relativas à data atual em `America/Recife`; nomes citando o cenário (`test_ct11_...`).

| Cenários | RF | Atividade |
|----------|----|-----------|
| CT01–CT08 | RF001–RF004 | DEV-04 |
| CT09–CT10 | RF005 | DEV-05 |
| CT11–CT14 | RF006–RF007 | DEV-06 |
| CT15–CT16 | RF008 | DEV-07 |
| FC12 (login obrigatório) | D1 | DEV-02 (proposta, seção 2) |
| Reativação inválida com massa preparada (I3) | RF004 | DEV-04; complementar, fora dos 16 cenários; número FC a conferir no EQF-6 |

**Dependências candidatas (nenhuma instalada):**

| Pacote | Uso | Quando |
|--------|-----|--------|
| Django | Framework (série 5.2 LTS, 6.0 ou 6.1; todas com `LoginRequiredMiddleware` e `CheckConstraint(condition=...)`) | DEV-02 |
| psycopg (versão 3) | Driver do PostgreSQL | DEV-02 |
| black e ruff | Formatação e lint | DEV-02 |
| gunicorn e whitenoise | Servidor WSGI e arquivos estáticos no Render | DEV-08 |
| dj-database-url (opcional) | Ler a URL do banco do Neon | DEV-02 ou DEV-08 |

## 8. Riscos e ordem de integração

**Riscos:**

1. **Prazo:** sete dias entre o fim de DEV-03 (08/11) e a entrega final (15/11).
2. **REQ-04 (EQF-10) em andamento** pode atrasar DEV-03.
3. **PR #1 aberto:** a `main`, e portanto esta branch, ainda trata I1–I5 como pendentes.
4. **Acesso de Raphael:** ele consta como colaborador do repositório com permissão de escrita (verificado em 01/11/2026). Falta confirmar na prática o fluxo de branch própria e de revisão de PR.
5. **Concorrência:** os testes exigem PostgreSQL local ou banco de desenvolvimento.
6. **Mensagens:** a tabela oficial do EQF-5 ainda não foi conferida.

**Ordem de integração das branches documentais (pendência, sem alteração nesta tarefa):**

1. PR #1 (`docs/alinhamento-workspace`), de preferência com merge commit, para preservar os commits.
2. `docs/guia-integracao-raphael`, que herda os dois commits do PR #1; depois do item 1, o PR dela mostraria só os commits do guia.
3. `docs/contrato-tecnico-dev01`, baseada na `main` sem os commits anteriores; antes do PR, atualizar com a `main` integrada, de forma não destrutiva.

## 9. Resumo técnico para futura atualização do EQF-13

Texto preparado para Rickelme registrar no Jira; **não foi registrado**.

> **DEV-01 — decisões propostas (aguardando aceite de Rickelme e Raphael):**
>
> - Apps Django: `equipamentos` (RF001–RF004), `clientes` (RF005) e `alugueis` (RF006–RF008). Projeto `config` com página inicial e rotas `login`/`logout`.
> - Autenticação com views nativas do Django Auth, sem app própria; logout só por POST; `LoginRequiredMiddleware` (Django 5.1 ou superior); contas criadas administrativamente; sem cadastro público nem recuperação de senha.
> - Regras de negócio em `services.py`; templates globais em `templates/`; Bootstrap 5.3 local em `static/`.
> - Modelagem: aluguel aberto indicado por `data_devolucao_real` nula; restrição única parcial no PostgreSQL para um aluguel aberto por equipamento; `PROTECT` nas relações; valores em `DecimalField`; datas em `America/Recife`.
> - Contrato: 16 rotas e 14 templates, com variáveis de contexto e divisão de arquivos entre backend e frontend.
> - Documentos: `docs/contrato-tecnico-frontend-backend.md`, `docs/modelagem-proposta.md` e `docs/plano-backend-dev01-dev03.md` (branch `docs/contrato-tecnico-dev01`, ainda local).
> - Pendências: aceite do contrato, interpretações listadas no contrato (seção 11) e tabela de mensagens do EQF-5.

## 10. Pendências

**Para DEV-02:**

1. Escolher a série e a versão exata do Django, com nova consulta às fontes oficiais.
2. Confirmar o runner de testes (`manage.py test` ou `pytest`).
3. Definir o PostgreSQL de desenvolvimento e de testes.
4. Fixar dependências, criar `.env.example` e escrever as instruções de execução.
5. Verificar se `LoginView` aceita acesso anônimo com `LoginRequiredMiddleware` ou se precisa de `login_not_required`.
6. Registrar no Jira onde fica a autenticação (seção 2).
7. Combinar com Raphael a versão exata do Bootstrap 5.3 e quem adiciona os arquivos.

**Para DEV-03:**

1. Aguardar a conclusão de REQ-04 (EQF-10).
2. Resolver as interpretações pendentes da [modelagem](modelagem-proposta.md#11-pontos-em-aberto).
3. Produzir o diagrama de dados.
4. Conferir a tabela de mensagens do EQF-5.
