# EquipaFácil — Sistema de Aluguel de Equipamentos

> **Situação:** fundação técnica do Django em preparação (DEV-02). **Nenhuma funcionalidade de negócio (RF001–RF008) foi implementada:** existem apenas o projeto, a autenticação de funcionários e duas páginas provisórias para testá-la. Veja [Ambiente local de desenvolvimento](#ambiente-local-de-desenvolvimento).

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

Regras de negócio planejadas: RN001 (aluguéis simultâneos e disponibilidade), RN002 (validação de dados), RN003 (integridade e exclusão/inativação) e RN004 (datas, duração e valores). Detalhes e rastreabilidade em [`docs/rastreabilidade.md`](docs/rastreabilidade.md).

Requisito técnico transversal: acesso restrito a funcionários autenticados (Django Auth), sem cadastro público.

## Tecnologias previstas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.13, Django 5.2 LTS (5.2.18, fixado em `requirements.txt`) |
| Frontend | Django Templates, Bootstrap, HTML, CSS, JavaScript |
| Banco de dados | PostgreSQL (hospedagem prevista no Neon) |
| Hospedagem | Render (previsto) |
| Gestão | Jira (Kanban), GitHub |

Até agora estão configurados apenas o Python, o Django e o ambiente local. PostgreSQL definitivo, Neon e Render ainda não. Veja [`docs/arquitetura-planejada.md`](docs/arquitetura-planejada.md).

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
- [ ] Configuração do projeto Django (fundação de DEV-02 em preparação, aguardando revisão)
- [ ] Implementação de RF001–RF008
- [ ] Testes e demonstração
- [ ] Deploy

## Ambiente local de desenvolvimento

> Fundação de DEV-02 (EQF-14), **em preparação**. Ainda não há modelos de domínio, telas definitivas nem deploy. As páginas de login e de início são **provisórias**, só para validar a autenticação.

### Requisitos

- Windows com PowerShell (comandos abaixo) e Git.
- Python **3.13** (`py -3.13 --version`).
- PostgreSQL 14 ou superior é o banco-alvo; opcional nesta etapa (veja [Banco de dados](#banco-de-dados)).

### Ambiente virtual e dependências

Na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

O projeto usa só o Python do `.venv`, nunca o Python global. Se o PowerShell não permitir executar o `Activate.ps1`, troque `python` por `.\.venv\Scripts\python.exe` nos comandos, sem ativar o ambiente.

- `requirements.txt`: dependências de execução (Django 5.2.18, série LTS, e psycopg 3.3.6, driver do PostgreSQL). É o único arquivo usado fora do desenvolvimento.
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
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE` | Conexão com o PostgreSQL |
| `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_PROXY_SSL_HEADER` | Segurança fora do desenvolvimento, a definir no deploy (DEV-08) |
| `DJANGO_ENV_FILE` | Caminho de outro arquivo `.env`; vazio desativa a leitura |

### Banco de dados

- **PostgreSQL é o banco do projeto.** Para usá-lo localmente, crie um banco e um usuário próprios e preencha `DB_ENGINE=postgresql` e as variáveis `DB_*` no `.env`, seguindo o procedimento seguro em [`docs/postgresql-local.md`](docs/postgresql-local.md). **A validação em PostgreSQL ainda está pendente.** Neon e o banco de produção ainda não existem.
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

Os testes criam usuários e senhas temporários durante a execução. Rode-os com `DJANGO_DEBUG=True`: com DEBUG desativado o projeto redireciona HTTP para HTTPS. Com SQLite, o resultado esperado é `OK (skipped=3)`: os três testes de `config/tests/test_postgresql.py` só rodam com PostgreSQL.

`black --check` e `ruff check` apenas verificam. Para corrigir, rode `black <arquivo>` ou `ruff check --fix <arquivo>` só nos arquivos que você alterou.

Verificação de produção simulada, em um terminal separado (não conecta ao banco; os valores são fictícios):

```powershell
$env:DJANGO_ENV_FILE = ""
$env:DJANGO_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(50))")
$env:DJANGO_DEBUG = "False"
$env:DJANGO_ALLOWED_HOSTS = "equipafacil.exemplo.test"
$env:DB_ENGINE = "postgresql"; $env:DB_NAME = "equipafacil"; $env:DB_USER = "equipafacil"
python manage.py check --deploy
```

Nesta etapa, o único aviso esperado é `security.W004` (HSTS), que será configurado no deploy (DEV-08).

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

### Advertências para produção (DEV-08)

- `security.W004` (HSTS) continua em aberto: defina `DJANGO_SECURE_HSTS_SECONDS` só quando todo o site estiver em HTTPS.
- Atrás do proxy do Render, ative `DJANGO_SECURE_PROXY_SSL_HEADER=True`; sem isso, o redirecionamento para HTTPS entra em laço.
- Arquivos estáticos ainda não são servidos com `DJANGO_DEBUG=False` (falta definir `collectstatic` e o servidor de estáticos).
- Não há limite de tentativas de login nem política de segurança de conteúdo (CSP); a sessão dura o padrão do Django (duas semanas). São decisões pendentes, não configuradas.

### Limitações desta etapa

- Sem modelos, migrations ou regras de domínio; nenhum RF001–RF008 implementado.
- As rotas `login`, `logout` e `inicio` e as páginas `registration/login.html` e `inicio.html` são provisórias até o aceite do contrato DEV-01; o layout definitivo é do frontend.
- Testes executados só com SQLite; **nada foi testado em PostgreSQL ainda** (procedimento em [`docs/postgresql-local.md`](docs/postgresql-local.md)).
- Sem Bootstrap, arquivos estáticos próprios, Neon, Render ou deploy.

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
