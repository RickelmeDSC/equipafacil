# EquipaFácil — Sistema de Aluguel de Equipamentos

> **Situação (marco de 02/11/2026, `main` em `85b4d1a`):** backend de RF001–RF008 implementado e integrado à `main` (DEV-02 a DEV-06, pelos PRs #1 e #3 a #8, com merge commit). Na validação da tarefa 13A, foram 360 testes aprovados no PostgreSQL e, no SQLite, 336 aprovados e 24 pulados. As páginas HTML são **provisórias**: o frontend definitivo (DEV-07) e a homologação visual estão pendentes, o contrato técnico (PR #2) ainda não foi aprovado e não há deploy (Neon e Render não foram criados). Publicação e colaboração com o frontend: [`docs/publicacao-e-colaboracao.md`](docs/publicacao-e-colaboracao.md). Veja [Ambiente local de desenvolvimento](#ambiente-local-de-desenvolvimento).

Sistema acadêmico de gestão de aluguel de equipamentos, desenvolvido com Python/Django e PostgreSQL.

## Objetivo

Oferecer a funcionários autenticados de uma locadora uma aplicação web para cadastrar equipamentos e clientes, registrar aluguéis e devoluções e consultar o histórico de locações, com regras de disponibilidade, datas e valores verificadas no backend.

## Contexto acadêmico

Projeto em equipe do curso de Análise e Desenvolvimento de Sistemas (ADS) da UNIBRA. O trabalho é dividido entre as equipes de Requisitos, Desenvolvimento e Testes de Software, e o planejamento funcional é acompanhado no Jira.

### Referências

| Referência | Papel | Situação |
|------------|-------|----------|
| Especificação técnica v3 (Jira, épicos EQF-4, EQF-5 e EQF-6) | Referência de planejamento | Vigente |
| Documento de Requisitos v1.1 | Documento acadêmico | Revisado tecnicamente; validação acadêmica final aguardando Rafael Ferreira e Ivisson. Não é publicado neste repositório |
| Decisões I1–I5 | Ajustes da especificação | Aprovadas por Rickelme David em 01/11/2026 |

A especificação v3 e o Documento de Requisitos v1.1 não são versões concorrentes do mesmo arquivo: a primeira organiza o planejamento no Jira; o segundo é o documento acadêmico de requisitos.

## Funcionalidades planejadas

| ID | Requisito funcional | Prioridade |
|----|---------------------|------------|
| RF001 | Cadastrar equipamentos | Alta |
| RF002 | Consultar e pesquisar equipamentos | Alta |
| RF003 | Editar informações de equipamentos | Alta |
| RF004 | Excluir, inativar ou reativar equipamentos | Alta |
| RF005 | Cadastrar, listar, consultar e editar clientes | Alta |
| RF006 | Registrar aluguel | Alta |
| RF007 | Registrar devolução | Alta |
| RF008 | Consultar histórico de aluguéis | Média |
| RF009 | Pesquisar clientes cadastrados | Média |
| RF010 | Filtrar histórico de aluguéis por situação | Média |

RF009 e RF010 foram acrescentados em 10/11/2026 (Documento de Requisitos v1.3 e Casos de Teste v1.4, CT17–CT20), com a decisão D16; aprovação técnica no EQF-5 e implementação no EQF-43. A validação documental da equipe de Requisitos está pendente.

Regras de negócio planejadas: RN001 (aluguéis simultâneos e disponibilidade), RN002 (validação de dados), RN003 (integridade e exclusão/inativação) e RN004 (datas, duração e valores). Detalhes e rastreabilidade em [`docs/rastreabilidade.md`](docs/rastreabilidade.md).

Requisito técnico transversal: acesso restrito a funcionários autenticados (Django Auth), sem cadastro público.

## Tecnologias previstas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.13, Django 5.2 LTS (5.2.18, fixado em `requirements.txt`) |
| Frontend | Django Templates, Bootstrap, HTML, CSS, JavaScript |
| Banco de dados | PostgreSQL (hospedagem prevista no Neon) |
| Hospedagem | Render, um único Web Service com Gunicorn e WhiteNoise (preparado, não implantado) |
| Gestão | Jira (Kanban), GitHub |

Até agora estão configurados o Python, o Django e o ambiente local, com PostgreSQL local validado para desenvolvimento e testes. O código está preparado para o Render e o Neon ([`docs/deploy-render-neon.md`](docs/deploy-render-neon.md)), mas nenhum serviço foi criado. Veja [`docs/arquitetura-planejada.md`](docs/arquitetura-planejada.md).

## Equipes

| Equipe | Integrantes | Responsabilidades |
|--------|-------------|-------------------|
| Requisitos | Rafael Ferreira, Ivisson | Documento de requisitos (RF, RN), revisão e validação acadêmica |
| Desenvolvimento | Rickelme David | Backend Django, banco de dados, regras de negócio, autenticação, integração, infraestrutura e deploy, coordenação técnica |
| Desenvolvimento | Raphael Eloi | Frontend (Django Templates, Bootstrap), responsividade e apresentação de dados e mensagens |
| Testes de Software | Alexandre Abreu, Vinícius Soares | 16 cenários Gherkin (CT01–CT16), execução de testes e registro de defeitos |

## Situação atual

- [x] Planejamento no Jira (especificação técnica v3)
- [x] Repositório e documentação inicial
- [x] Revisão técnica do Documento de Requisitos v1.1 e aprovação das decisões I1–I5
- [ ] Validação acadêmica final dos requisitos (Rafael Ferreira e Ivisson)
- [ ] Revisão dos cenários de teste (equipe de Testes)
- [x] Configuração do projeto Django (DEV-02, integrada à `main`)
- [x] Implementação de RF001–RF008 no backend (DEV-02 a DEV-06), com páginas provisórias
- [x] Implementação de RF009 e RF010 (EQF-43), com CT17–CT20 automatizados
- [ ] Frontend definitivo e homologação visual (DEV-07)
- [ ] Testes e demonstração
- [ ] Deploy

## Ambiente local de desenvolvimento

> Backend de RF001–RF008 integrado à `main`: fundação (DEV-02, EQF-14), modelos de domínio (DEV-03, EQF-15) e gestão de equipamentos (DEV-04, EQF-16), de clientes (DEV-05, EQF-17) e de aluguéis (DEV-06, EQF-18). Todas as páginas HTML são **provisórias**, só para validar o backend; as definitivas são do frontend.

### Requisitos

- Windows com PowerShell (comandos abaixo) e Git.
- Python **3.13** (`py -3.13 --version`).
- PostgreSQL 14 ou superior é o banco-alvo (validado com o 18.6 local); para começar, o SQLite temporário também funciona (veja [Banco de dados](#banco-de-dados)).

### Ambiente virtual e dependências

Na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

O projeto usa só o Python do `.venv`, nunca o Python global. Se o PowerShell não permitir executar o `Activate.ps1`, troque `python` por `.\.venv\Scripts\python.exe` nos comandos, sem ativar o ambiente.

- `requirements.txt`: dependências de execução (Django 5.2.18, série LTS; psycopg 3.3.6, driver do PostgreSQL; Gunicorn 26.2.0 e WhiteNoise 6.12.0, para a hospedagem). É o único arquivo usado fora do desenvolvimento.
- `requirements-dev.txt`: inclui o anterior e as ferramentas de qualidade (Ruff 0.17.3 e Black 26.10.1), configuradas em `pyproject.toml`.

### Configuração (`.env`)

```powershell
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Cole a chave gerada em `DJANGO_SECRET_KEY` no `.env`. O `.env` é ignorado pelo Git e **nunca** deve ser versionado; variáveis já definidas no ambiente têm prioridade sobre ele.

| Variável | Uso |
|----------|-----|
| `DJANGO_SECRET_KEY` | Obrigatória; uma chave própria por ambiente. Com `DJANGO_DEBUG=False`, o projeto não inicia com chave fraca (menos de 50 caracteres, como a do `.env.example`) |
| `DJANGO_DEBUG` | `True` só no desenvolvimento local; padrão `False` |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos, separados por vírgula |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origens HTTPS confiáveis, separadas por vírgula |
| `DB_ENGINE` | `postgresql` (padrão, banco-alvo) ou `sqlite` (temporário) |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE` | Conexão com o PostgreSQL local |
| `DATABASE_URL` | Conexão hospedada (Neon). Quando definida, vale sobre as `DB_*`; não use localmente para testes |
| `DB_CONN_MAX_AGE` | Segundos de reuso da conexão; padrão `0` |
| `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_PROXY_SSL_HEADER` | Segurança fora do desenvolvimento (veja [`docs/deploy-render-neon.md`](docs/deploy-render-neon.md)) |
| `RENDER_EXTERNAL_HOSTNAME` | Definida pelo Render; entra em `ALLOWED_HOSTS` automaticamente |
| `DJANGO_ENV_FILE` | Caminho de outro arquivo `.env`; vazio desativa a leitura |

### Banco de dados

- **PostgreSQL é o banco do projeto.** Para usá-lo localmente, siga [`docs/postgresql-local.md`](docs/postgresql-local.md): um usuário sem privilégios elevados, um banco de desenvolvimento e um banco de testes, com a senha no `pgpass.conf`. **Validado localmente** (PostgreSQL 18.6, todos os testes aprovados, nenhum pulado). Neon e o banco de produção ainda não existem; a conexão hospedada usa `DATABASE_URL` com TLS obrigatório.
- **SQLite (`DB_ENGINE=sqlite`) é um recurso temporário de desenvolvimento.** O projeto o recusa com `DJANGO_DEBUG=False`. Ele não substitui o PostgreSQL: as restrições do banco e os testes de concorrência previstos a partir de DEV-03 exigem PostgreSQL.

### Verificações e testes

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
ruff check .
black --check .
python -m pip check
```

Os testes criam usuários e senhas temporários durante a execução. Rode-os com `DJANGO_DEBUG=True`: com DEBUG desativado o projeto redireciona HTTP para HTTPS. Com SQLite, o resultado esperado é `OK (skipped=25)` (o Django conta os pulados dentro do total executado): os testes de `config/tests/test_postgresql.py`, `alugueis/tests/test_banco.py` (introspecção), `alugueis/tests/test_concorrencia.py`, `alugueis/tests/test_concorrencia_devolucao.py`, `alugueis/tests/test_concorrencia_confirmacao.py`, `equipamentos/tests/test_concorrencia.py` e `clientes/tests/test_concorrencia.py`, e o teste de maiúsculas acentuadas de `clientes/tests/test_pesquisa.py`, só rodam com PostgreSQL. **Com PostgreSQL, use sempre `python manage.py test --keepdb`**; o resultado esperado é `OK`, sem testes pulados. Na validação da tarefa 13A (`main` em `85b4d1a`), foram 360 testes no total: todos aprovados no PostgreSQL; no SQLite, 336 aprovados e 24 pulados. Com RF009 e RF010 (EQF-43, 10/11/2026), são 424 testes: todos aprovados no PostgreSQL local; no SQLite, 399 aprovados e 25 pulados. Sem `--keepdb`, o Django tentaria apagar e recriar o banco de testes (veja o documento do PostgreSQL).

`black --check` e `ruff check` apenas verificam. Para corrigir, rode `black <arquivo>` ou `ruff check --fix <arquivo>` só nos arquivos que você alterou.

**Integração contínua:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em Pull Requests para a `main` e em pushes na `main`, em Ubuntu com o Python do `.python-version`. São três jobs:

- **PostgreSQL 18** (serviço do runner, com credenciais fictícias): `pip check`, Ruff, Black, `check`, `makemigrations --check --dry-run` e a suíte completa.
- **SQLite**: a suíte, com os testes exclusivos de PostgreSQL pulados.
- **Gunicorn em Linux**: `scripts/validar-gunicorn-linux.sh`.

Não usa segredos, não acessa Neon nem Render e não faz deploy. O workflow só é considerado validado depois da primeira execução verde no GitHub.

Verificação de produção simulada, em um terminal separado (não conecta ao banco; os valores são fictícios):

```powershell
$env:DJANGO_ENV_FILE = ""
$env:DJANGO_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(50))")
$env:DJANGO_DEBUG = "False"
$env:DJANGO_ALLOWED_HOSTS = "equipafacil.exemplo.test"
$env:DATABASE_URL = "postgresql://app@127.0.0.1:1/equipafacil?sslmode=require"
python manage.py check --deploy
python manage.py collectstatic --noinput
```

A `DATABASE_URL` acima é fictícia e local. Nesta etapa, o único aviso esperado é `security.W004` (HSTS), que só será ligado depois de validar o ambiente real. O `collectstatic` grava em `staticfiles/`, fora do Git. O mesmo roteiro do build do Render está em `scripts/render-build.sh`.

### Execução local

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://127.0.0.1:8000/, que redireciona para o login. O Django Admin (http://127.0.0.1:8000/admin/) é o único meio de criar contas de funcionários; não há cadastro público nem recuperação de senha por e-mail. Crie o superusuário só no seu ambiente local, com senha própria.

### Templates provisórios

`templates/registration/login.html` e `templates/inicio.html` existem só para validar a autenticação e serão substituídos pelo frontend. Para a troca não quebrar o backend nem os testes, a nova versão deve manter:

- **Login:** o caminho `registration/login.html` (padrão do `LoginView`), formulário `method="post"` com `{% csrf_token %}`, os campos `username` e `password` e o campo oculto `next`.
- **Saída:** um formulário `method="post"` para `{% url 'logout' %}` com `{% csrf_token %}`; logout por link (GET) não funciona.
- Saída de dados sempre com o escape automático do Django (sem `|safe` em dados do usuário).

Os nomes `login`, `logout` e `inicio` ainda dependem do aceite do contrato DEV-01.

`templates/equipamentos/lista.html`, `formulario.html` e `acoes.html` (DEV-04) `templates/clientes/lista.html` e `formulario.html` (DEV-05) e `templates/alugueis/formulario.html`, `historico.html` e `devolver.html` (DEV-06) também são provisórios, sem Bootstrap. Rotas, variáveis e campos estão em [`docs/equipamentos-operacional.md`](docs/equipamentos-operacional.md), [`docs/clientes-operacional.md`](docs/clientes-operacional.md) e [`docs/alugueis-operacional.md`](docs/alugueis-operacional.md); a troca pelo frontend deve mantê-los, com `{% csrf_token %}` em todo POST.

### Hospedagem (preparação)

Um único Web Service no Render serve backend e frontend, com Gunicorn, arquivos estáticos pelo WhiteNoise e banco no Neon por `DATABASE_URL`. Comandos, variáveis, health check (`/healthz/`), estratégia de migrations, backup e restrições do plano Free estão em [`docs/deploy-render-neon.md`](docs/deploy-render-neon.md). **Nada foi implantado.**

Advertências ainda abertas:

- `security.W004` (HSTS): defina `DJANGO_SECURE_HSTS_SECONDS` só depois de confirmar todo o site em HTTPS no ambiente real.
- No Render, `DJANGO_SECURE_PROXY_SSL_HEADER=True` é obrigatório; sem isso, o redirecionamento para HTTPS entra em laço.
- O Gunicorn não roda no Windows. Em Linux, valide com `bash scripts/validar-gunicorn-linux.sh` antes do primeiro deploy; o job `gunicorn` do CI executa esse script, mas a validação só vale depois de uma execução verde no GitHub.
- Não há limite de tentativas de login nem política de segurança de conteúdo (CSP); a sessão dura o padrão do Django (duas semanas). São decisões pendentes, não configuradas.

### Limitações desta etapa

- Modelos `Equipamento`, `Cliente` e `Aluguel` com restrições e migrations iniciais (DEV-03; veja [`docs/modelagem-implementada.md`](docs/modelagem-implementada.md)).
- Gestão de equipamentos (RF001–RF004, DEV-04; veja [`docs/equipamentos-operacional.md`](docs/equipamentos-operacional.md)) com páginas provisórias.
- Gestão de clientes (RF005, DEV-05; veja [`docs/clientes-operacional.md`](docs/clientes-operacional.md)), sem detalhe nem exclusão (D14, RN003), com pesquisa por nome ou CPF (RF009, D16, EQF-43).
- Aluguéis, devoluções e histórico (RF006–RF008, DEV-06; veja [`docs/alugueis-operacional.md`](docs/alugueis-operacional.md)), com prévia calculada no servidor (D13), sem cancelamento nem edição de aluguel; histórico com filtro por situação (RF010, EQF-43).
- As rotas `login`, `logout` e `inicio` e as páginas `registration/login.html` e `inicio.html` são provisórias até o aceite do contrato DEV-01; o layout definitivo é do frontend.
- Suíte validada no SQLite e no PostgreSQL 18.6 local; restrições de banco e concorrência dependem dos modelos de DEV-03 (detalhes em [`docs/postgresql-local.md`](docs/postgresql-local.md)).
- Sem Bootstrap nem arquivos estáticos próprios: o frontend definitivo (DEV-07) e a homologação visual estão pendentes. O contrato técnico (PR #2) continua em rascunho, sem aprovação.
- Neon e Render preparados, mas sem serviço criado nem deploy.

## Prazos

| Entrega | Data |
|---------|------|
| Primeira entrega (requisitos, regras de negócio, cenários Gherkin e Jira) | 03/11/2026 |
| Entrega final do sistema | 15/11/2026 |

## Jira

Planejamento, atividades e especificação técnica v3: [Quadro EQF no Jira](https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2) (acesso restrito aos membros do projeto).

## Como colaborar

### Branches

| Branch | Uso |
|--------|-----|
| `main` | Versão integrada e revisada. Protegida: só recebe alterações por Pull Request |
| `docs/<descricao>` | Documentação |
| `feat/backend-eqf-NN-<descricao>` | Backend, banco e regras de negócio (ex.: `feat/backend-eqf-16-equipamentos`) |
| `feat/frontend-eqf-NN-<descricao>` | Templates, estilos e interface (ex.: `feat/frontend-eqf-16-equipamentos`) |
| `fix/eqf-NN-<descricao>` | Correções |

`NN` é o número da atividade no Jira. Crie a branch a partir da `main` atualizada e nunca faça commits diretamente na `main`.

Antes de desenvolver frontend ou backend, leia o [guia de integração frontend ↔ backend](docs/guia-integracao-frontend-backend.md).

### Fluxo de qualidade

1. **Planejamento antes da implementação:** confirme a atividade do Jira, os RF/RN/CT envolvidos e, se houver tela, o contrato frontend × backend.
2. **Testes automatizados** vinculados aos RF e aos cenários CT; nenhuma funcionalidade é concluída sem testes passando.
3. **Commits semânticos** em português ([Conventional Commits](https://www.conventionalcommits.org/pt-br/)), por exemplo `feat: adiciona cadastro de equipamentos`.
4. **Verificação de segurança** antes de cada commit e PR: revise o diff e confirme que não há segredos, `.env` ou dados reais.
5. **Pull Request** com o template, citando a atividade do Jira (ex.: `EQF-16`) e os RF/RN/CT relacionados.
6. **Code review** humano antes do merge.
7. **Alterações de requisitos** passam por revisão humana das equipes responsáveis e são registradas no Jira; implemente apenas requisitos aprovados.
8. **Deploy** somente após autorização explícita do responsável técnico (Rickelme David).

**Nunca** publique senhas, tokens, arquivos `.env` ou dados reais de pessoas. Use `.env.example` com valores fictícios.

## Licença

Projeto acadêmico, sem licença de uso definida até o momento.
