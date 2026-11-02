# Plano backend — DEV-01 a DEV-03

> **RASCUNHO PROVISÓRIO — PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.1 — 01/11/2026. Planejamento apenas: **nenhuma atividade foi iniciada** e não existe código Django no repositório.
>
> **Limitação:** a auditoria do Jira (Tarefa 08A-WEB) não foi concluída. O escopo oficial, os critérios de aceite, os responsáveis e os prazos de DEV-01 (EQF-13), DEV-02 (EQF-14) e DEV-03 (EQF-15) **não foram conferidos**. O que está marcado como proposta deve ser ajustado ao Jira antes de virar compromisso.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [modelagem proposta](modelagem-proposta.md).

## 1. Escopo conhecido das atividades

| Atividade | Jira | Escopo conhecido | Fonte | Situação |
|-----------|------|------------------|-------|----------|
| DEV-01 | EQF-13 | Arquitetura e contrato técnico frontend × backend; organização do projeto | Tarefa 08A-LOCAL; [`arquitetura-planejada.md`](arquitetura-planejada.md) | Critérios oficiais **[verificar]** |
| DEV-02 | EQF-14 | Organização do projeto: versão do Python, ferramentas de teste e de lint | [`arquitetura-planejada.md`](arquitetura-planejada.md) | Critérios oficiais **[verificar]** |
| DEV-03 | EQF-15 | **Não documentado no repositório** | — | **[verificar]** |
| DEV-04 | EQF-16 | Equipamentos: RF001–RF004, CT01–CT08 | [`rastreabilidade.md`](rastreabilidade.md) | Planejado |
| DEV-05 | EQF-17 | Clientes: RF005, CT09–CT10 | [`rastreabilidade.md`](rastreabilidade.md) | Planejado |
| DEV-06 | EQF-18 | Aluguel e devolução: RF006–RF007, CT11–CT14 | [`rastreabilidade.md`](rastreabilidade.md) | Planejado |
| DEV-07 | EQF-19 | Histórico: RF008, CT15–CT16 | [`rastreabilidade.md`](rastreabilidade.md) | Planejado |
| DEV-08 | EQF-20 | Deploy no Render (banco no Neon) | [`arquitetura-planejada.md`](arquitetura-planejada.md) | Planejado |

**Lacuna:** a autenticação (D1, coberta pela cobertura complementar FC12) não aparece associada a nenhuma atividade DEV nos documentos do repositório. Proposta: incluí-la em DEV-03, se o escopo oficial permitir — **[verificar]**.

## 2. Proposta para DEV-01, DEV-02 e DEV-03

### DEV-01 — Arquitetura e contrato técnico

- **Entregáveis:** [contrato técnico](contrato-tecnico-frontend-backend.md), [modelagem](modelagem-proposta.md) e este plano.
- **Pronto quando (proposta):** Rickelme e Raphael registram o aceite do contrato; os pontos **[verificar]** são conferidos com o Jira e o Documento de Requisitos v1.1.
- **Depende de:** nada. Destrava DEV-02 e o trabalho de telas de Raphael.

### DEV-02 — Fundação do projeto

- **Entregáveis (proposta):** projeto Django (`config/`, apps `core`, `equipamentos`, `clientes` e `alugueis` vazias); `settings.py` lendo variáveis de ambiente; `.env.example` com valores fictícios; lista de dependências fixada; banco PostgreSQL de desenvolvimento e de testes; configuração de `black` e `ruff`; diretórios `templates/` e `static/` criados vazios para Raphael.
- **Pronto quando (proposta):** `python manage.py check` e `python manage.py test` rodam sem erro num ambiente limpo, e nenhum segredo está versionado.
- **Depende de:** DEV-01 (nomes das apps e da estrutura).

### DEV-03 — Modelos, regras base e autenticação (proposta, escopo oficial não conferido)

- **Entregáveis (proposta):** models `Equipamento`, `Cliente` e `Aluguel` com restrições e migrations; serviços base (disponibilidade, situação do aluguel, bloqueios de concorrência); login e logout com `LoginRequiredMiddleware`; criação de contas pelo administrador; testes de modelo e de concorrência.
- **Pronto quando (proposta):** restrições verificadas em PostgreSQL; teste de dois aluguéis simultâneos do mesmo equipamento passando; rotas protegidas por login (FC12).
- **Depende de:** DEV-02.

## 3. Dependências entre atividades

1. **DEV-01** → **DEV-02** → **DEV-03**.
2. **DEV-04** (equipamentos) e **DEV-05** (clientes) dependem de DEV-03 e podem andar em paralelo.
3. **DEV-06** (aluguel e devolução) depende de DEV-04 e DEV-05.
4. **DEV-07** (histórico) depende de DEV-06.
5. **DEV-08** (deploy): a preparação de Neon e Render pode começar depois de DEV-02; o deploy final depende de DEV-07 e de autorização explícita.
6. **Frontend (Raphael):** design estático pode começar já; a integração de cada tela depende do contrato aceito e da atividade DEV correspondente.

## 4. Cronograma sugerido

Sugestão para discussão; não altera prazos nem prioridades do Jira, que permanecem como estão (I4).

| Período | Backend (Rickelme) | Frontend (Raphael) |
|---------|--------------------|--------------------|
| 02/11 a 03/11 | DEV-01: validar contrato e modelagem; primeira entrega acadêmica em 03/11 | Ler repositório e guia; design estático |
| 03/11 a 04/11 | DEV-02: fundação do projeto | Layout base e login em HTML estático |
| 04/11 a 05/11 | DEV-03: models, serviços base e autenticação | Telas de equipamentos e clientes em HTML estático |
| 05/11 a 07/11 | DEV-04 e DEV-05 | Integrar telas de equipamentos e clientes |
| 07/11 a 10/11 | DEV-06 | Integrar aluguel e devolução |
| 10/11 a 11/11 | DEV-07 | Integrar histórico |
| 11/11 a 13/11 | DEV-08 e apoio à execução dos testes (QA-06, EQF-26) | Revisão responsiva e de acessibilidade |
| 13/11 a 15/11 | Correções e entrega final | Correções e entrega final |

## 5. Estratégia de testes (proposta)

- **Runner:** `python manage.py test` com `TestCase` do Django, para não adicionar dependência — decisão final em DEV-02.
- **Banco de testes:** PostgreSQL, obrigatório para os testes de concorrência (o SQLite ignora `select_for_update()`).
- **Datas:** relativas à data atual em `America/Recife`; os serviços recebem `hoje` como parâmetro.
- **Nomes:** cada teste cita o cenário, por exemplo `test_ct11_registra_aluguel_de_tres_diarias`.

| Cenários | RF | Atividade | Camada principal |
|----------|----|-----------|------------------|
| CT01–CT02 | RF001 | DEV-04 | Serviço e view de cadastro |
| CT03–CT04 | RF002 | DEV-04 | View de lista e pesquisa |
| CT05–CT06 | RF003 | DEV-04 | Serviço de edição e valor congelado |
| CT07–CT08 | RF004 | DEV-04 | Serviços de exclusão e inativação |
| CT09–CT10 | RF005 | DEV-05 | Formulário e serviço de cliente |
| CT11–CT12 | RF006 | DEV-06 | Serviço de aluguel, incluindo concorrência |
| CT13–CT14 | RF007 | DEV-06 | Serviço de devolução |
| CT15–CT16 | RF008 | DEV-07 | View de histórico |
| FC12 | D1 | DEV-03 (proposta) | Proteção das rotas por login |
| Reativação inválida (I3) | RF004 | DEV-04 | Teste complementar com massa preparada; número FC **[verificar]** no EQF-6 |

## 6. Dependências Python candidatas

Nenhuma foi instalada. A decisão é de DEV-02 (desenvolvimento) e DEV-08 (deploy).

| Pacote | Uso | Quando |
|--------|-----|--------|
| Django | Framework (série 5.2 LTS, 6.0 ou 6.1, a decidir) | DEV-02 |
| psycopg (versão 3) | Driver do PostgreSQL | DEV-02 |
| black e ruff | Formatação e lint (desenvolvimento) | DEV-02 |
| gunicorn | Servidor WSGI no Render | DEV-08 |
| whitenoise | Servir arquivos estáticos no Render | DEV-08 |
| dj-database-url (opcional) | Ler a URL do banco do Neon; alternativa: variáveis separadas | DEV-02 ou DEV-08 |

## 7. Riscos

1. **Prazo:** cerca de 14 dias para 8 RFs, testes e deploy.
2. **Escopo oficial não conferido** para DEV-01 a DEV-03 (Tarefa 08A-WEB pendente).
3. **PR #1 aberto:** a `main`, e portanto esta branch, ainda trata I1–I5 como pendentes.
4. **Acesso de Raphael:** sem usuário do GitHub confirmado, ele ainda não pode criar branches no repositório.
5. **Concorrência:** os testes exigem PostgreSQL no ambiente local ou um banco de desenvolvimento.
6. **Mensagens:** a tabela oficial do EQF-5 não foi conferida.

## 8. Pendências

**Para DEV-02:**

1. Escolher a série e a versão exata do Django, com nova consulta às fontes oficiais.
2. Definir o runner de testes (`manage.py test` ou `pytest`).
3. Definir o PostgreSQL de desenvolvimento e de testes (local ou banco de desenvolvimento no Neon).
4. Fixar dependências e criar `.env.example`.
5. Configurar `black` e `ruff`.
6. Combinar com Raphael a versão exata do Bootstrap 5.3 e quem adiciona os arquivos.

**Para DEV-03:**

1. Conferir o escopo oficial de EQF-15 no Jira.
2. Confirmar onde fica a autenticação (D1) no planejamento e o mecanismo de criação de contas.
3. Resolver os pontos em aberto da [modelagem](modelagem-proposta.md): inativação sem histórico, reativação inválida (I3), normalização do código, CPF com dígitos repetidos e situação do aluguel futuro.
4. Conferir a tabela de mensagens do EQF-5 e substituir os textos provisórios do contrato.
