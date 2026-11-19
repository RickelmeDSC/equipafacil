# EquipaFácil — Sistema de Aluguel de Equipamentos

Aplicação web para a gestão de aluguel de equipamentos de uma locadora: cadastro de equipamentos e clientes, registro de aluguéis e devoluções e consulta ao histórico.

- **Sistema publicado:** https://equipafacil.onrender.com/ (acesso restrito a funcionários cadastrados)
- **Situação em 19/11/2026:** RF001–RF010 implementados e integrados à `main` (`01d038d`); 20 cenários de interface automatizados; quatro jobs de integração contínua aprovados na execução [44413841611](https://github.com/RickelmeDSC/equipafacil/actions/runs/44413841611).

## Apresentação

O EquipaFácil substitui o controle manual de uma locadora de equipamentos. O funcionário autenticado consulta o que está disponível, registra o aluguel com o valor calculado pelo sistema, registra a devolução e acompanha a situação de cada aluguel. As regras de disponibilidade, datas e valores são verificadas no servidor.

**Contexto acadêmico:** projeto em equipe da disciplina Qualidade de Software, turma ADS5NA 2026.2, do curso de Análise e Desenvolvimento de Sistemas da UNIBRA, ministrada pelo professor Lucas Edson. O trabalho foi dividido entre as equipes de Requisitos, Desenvolvimento e Testes de Software, com planejamento no Jira.

**Público-alvo:** funcionários de uma locadora. Não há cadastro público nem acesso de clientes; as contas são criadas pelo administrador.

## Funcionalidades

### Equipamentos (RF001–RF004)

- Cadastro com código único (sem diferenciar maiúsculas de minúsculas), nome, categoria fixa, diária e descrição.
- Lista com pesquisa por código ou nome, situação (Ativo ou Inativo) e disponibilidade.
- Edição; o código não pode ser alterado depois do primeiro aluguel.
- Inativação e reativação; equipamento com aluguel em aberto não pode ser inativado.
- Exclusão só de equipamento sem histórico de aluguéis; com histórico, a tela mostra o motivo do bloqueio.
- Disponibilidade calculada: disponível é o equipamento ativo e sem aluguel em aberto.

### Clientes (RF005, RF009)

- Cadastro com nome completo, CPF, telefone e e-mail.
- CPF validado (dígitos verificadores) e único.
- Lista com pesquisa por nome ou por CPF, completo ou parcial, com ou sem máscara.
- Edição; o CPF não pode ser alterado depois do primeiro aluguel.
- Não há exclusão de clientes nem página de detalhe.

### Aluguéis (RF006–RF008, RF010)

- Registro em formulário único: cliente, equipamento disponível, data de retirada (hoje ou futura) e devolução prevista.
- Diárias inclusivas: `(devolução prevista − retirada) + 1`.
- Prévia do valor calculada no servidor ("Calcular resumo") antes da confirmação; a prévia não grava nada.
- O valor da diária e o valor total ficam congelados no registro: editar o equipamento depois não altera aluguéis anteriores.
- No máximo um aluguel em aberto por equipamento, inclusive em registros simultâneos.
- Devolução única, com data entre a retirada e a data atual; libera o equipamento.
- Histórico com cliente, equipamento, datas, diárias, valores e situação.
- Situação calculada: Ativo, Atrasado, Encerrado ou Encerrado com atraso. Não há multa por atraso.
- Filtro do histórico por situação.

## Arquitetura

Monólito Django com páginas renderizadas no servidor. Não existe API REST nem aplicação de frontend separada.

```text
Navegador ──> Templates Django (Bootstrap) ──> Views ──> Serviços ──> Models (ORM) ──> PostgreSQL
```

- **Templates:** HTML renderizado pelo Django, com Bootstrap servido como arquivo estático do próprio projeto.
- **Views:** recebem a requisição, validam com formulários e chamam os serviços.
- **Serviços** (`*/services.py`): regras de negócio e transações, como o registro de aluguel e a devolução.
- **Models:** `Equipamento`, `Cliente` e `Aluguel`, com restrições também no banco de dados.
- **Autenticação:** Django Auth, com login obrigatório em todas as páginas; contas criadas no Django Admin.

Detalhes em [`docs/modelagem-implementada.md`](docs/modelagem-implementada.md), [`docs/frontend-implementado.md`](docs/frontend-implementado.md) e [`docs/contrato-tecnico-frontend-backend.md`](docs/contrato-tecnico-frontend-backend.md).

## Tecnologias

| Uso | Tecnologia |
|-----|-----------|
| Aplicação | Python 3.13 (`.python-version`: 3.13.15), Django 5.2.18 (série LTS), psycopg 3.3.6, Django Templates, Bootstrap 5.3.8, HTML, CSS e JavaScript |
| Banco de dados | PostgreSQL (validado com a versão 18); SQLite apenas como recurso de desenvolvimento e na suíte Robot |
| Implantação | Render (Web Service), Gunicorn 26.2.0 e WhiteNoise 6.12.0 |
| Desenvolvimento | Ruff 0.17.3 e Black 26.10.1, configurados em `pyproject.toml` |
| Testes | Runner de testes do Django; Robot Framework 7.5.1 com a biblioteca Browser 21.0.0 (Playwright e Chromium), que exige Node.js |
| Integração contínua | GitHub Actions |
| Gestão | Jira (quadro Kanban) e GitHub |

As versões estão fixadas em `requirements.txt`, `requirements-dev.txt` e `requirements-robot.txt`.

## Execução local

Os comandos abaixo são para Windows com PowerShell. Não há Docker nem configuração automática.

### Requisitos

- Git e Python **3.13** (`py -3.13 --version`).
- PostgreSQL 14 ou superior é o banco-alvo. Para começar, o SQLite temporário também funciona (veja [Banco de dados](#banco-de-dados)).

### Ambiente virtual e dependências

Na raiz do repositório:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

O projeto usa só o Python do `.venv`. Se o PowerShell não permitir executar o `Activate.ps1`, troque `python` por `.\.venv\Scripts\python.exe` nos comandos.

- `requirements.txt`: dependências de execução; é o único arquivo usado na hospedagem.
- `requirements-dev.txt`: inclui o anterior e as ferramentas de qualidade (Ruff e Black).
- `requirements-robot.txt`: inclui o `requirements.txt` e a automação de interface.

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
| `DATABASE_URL` | Conexão do ambiente hospedado. Quando definida, vale sobre as `DB_*`; não use localmente para testes |
| `DB_CONN_MAX_AGE` | Segundos de reuso da conexão; padrão `0` |
| `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_PROXY_SSL_HEADER` | Segurança fora do desenvolvimento (veja [`docs/deploy-render-neon.md`](docs/deploy-render-neon.md)) |
| `RENDER_EXTERNAL_HOSTNAME` | Definida pelo Render; entra em `ALLOWED_HOSTS` automaticamente |
| `DJANGO_ENV_FILE` | Caminho de outro arquivo `.env`; vazio desativa a leitura |

### Banco de dados

- **PostgreSQL é o banco do projeto.** Para usá-lo localmente, siga [`docs/postgresql-local.md`](docs/postgresql-local.md): um usuário sem privilégios elevados, um banco de desenvolvimento e um banco de testes.
- **SQLite (`DB_ENGINE=sqlite`) é um recurso temporário de desenvolvimento.** O projeto o recusa com `DJANGO_DEBUG=False`. Ele não substitui o PostgreSQL: as restrições do banco e os testes de concorrência exigem PostgreSQL.

### Iniciar o servidor

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse http://127.0.0.1:8000/, que redireciona para o login. O Django Admin (http://127.0.0.1:8000/admin/) é o único meio de criar contas de funcionários. Crie o superusuário só no seu ambiente local, com senha própria.

## Testes

### Verificações e testes Django

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
ruff check .
black --check .
python -m pip check
```

- São 424 testes de unidade e de integração nos apps `equipamentos`, `clientes`, `alugueis` e `config`.
- Rode com `DJANGO_DEBUG=True`: com DEBUG desativado o projeto redireciona HTTP para HTTPS.
- **Com PostgreSQL, use `python manage.py test --keepdb`**; o resultado esperado é `OK`, sem testes pulados. Sem `--keepdb`, o Django tentaria apagar e recriar o banco de testes.
- **Com SQLite**, o resultado esperado é `OK (skipped=25)`: os testes de concorrência, de introspecção do banco e um teste de pesquisa com maiúsculas acentuadas só rodam com PostgreSQL.
- `black --check` e `ruff check` apenas verificam. Para corrigir, rode `black <arquivo>` ou `ruff check --fix <arquivo>` só nos arquivos alterados.

### Robot Framework (testes de interface)

Os 20 casos de teste (CT01–CT20) estão automatizados com Robot Framework e a biblioteca Browser, que controla um Chromium.

```powershell
python -m pip install --requirement requirements-robot.txt
rfbrowser init chromium
python scripts/robot/executar.py                         # a suíte inteira
python scripts/robot/executar.py tests/Cenario16.robot   # um cenário
```

O primeiro e o segundo comando preparam o ambiente uma única vez; o `rfbrowser` exige Node.js 20 ou mais recente.

| Pasta | Conteúdo |
|-------|----------|
| `tests/CenarioNN.robot` | Um arquivo por caso de teste, sem seletores |
| `tests/Keywords/*_Steps.robot` | Passos reutilizáveis de cada página |
| `tests/Pages/*_Page.robot` | Somente variáveis com os seletores XPath de cada página |
| `scripts/robot/massas/ctNN.py` | Dados fictícios que cada cenário cria antes de rodar |

**Isolamento:** `scripts/robot/executar.py` sobe um servidor Django temporário em `127.0.0.1`, com um banco SQLite descartável em `resultados-robot/` e usuário e senha fictícios gerados na hora. A suíte ignora o `.env` e a `DATABASE_URL`, e recusa rodar em um banco que não seja o isolado. Cada cenário recria a própria massa; a execução é sequencial.

Os relatórios (`report.html`, `log.html`, `output.xml`) ficam em `resultados-robot/`, fora do Git. Instruções completas em [`docs/testes-robot.md`](docs/testes-robot.md).

Os casos CT01–CT20 também tiveram execução manual em novembro de 2026, com evidências anexadas às atividades do Jira. Esses registros são históricos e independentes da automação.

## Integração contínua (GitHub Actions)

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) roda em Pull Requests para a `main` e em pushes na `main`, em `ubuntu-24.04`, com o Python do `.python-version`. São quatro jobs independentes:

| Job | O que faz |
|-----|-----------|
| Qualidade e testes (PostgreSQL 18) | `pip check`, Ruff, Black, `check`, `makemigrations --check --dry-run` e os testes Django em um PostgreSQL do próprio runner |
| Testes (SQLite, desenvolvimento) | Testes Django com SQLite; os exclusivos de PostgreSQL são pulados |
| Gunicorn em Linux (produção simulada) | `scripts/validar-gunicorn-linux.sh` |
| Robot Framework (CT01 a CT20) | Os 20 cenários de interface, em sequência; guarda os relatórios no artefato `relatorios-robot` por 14 dias |

O CI não usa segredos, não acessa o ambiente publicado e não faz deploy. O job do Robot **ainda não é obrigatório** nas regras de proteção da `main`.

Última execução auditada: [44413841611](https://github.com/RickelmeDSC/equipafacil/actions/runs/44413841611), de 18/11/2026, no commit `01d038d` — quatro jobs aprovados; 424 testes Django (`OK` no PostgreSQL, `OK (skipped=25)` no SQLite); Robot com 20 aprovados e nenhuma falha.

## Implantação

O sistema está publicado em https://equipafacil.onrender.com/, em um único Web Service do Render que serve as páginas e os arquivos estáticos.

- **Build:** `bash scripts/render-build.sh` — instala `requirements.txt`, roda `check --deploy` e `collectstatic`. Não acessa o banco e não executa migrations.
- **Servidor:** Gunicorn; arquivos estáticos servidos pelo WhiteNoise.
- **Banco:** a configuração de produção exige PostgreSQL, informado ao serviço pela variável `DATABASE_URL`, com TLS. O projeto foi preparado para um banco no Neon ([`docs/deploy-render-neon.md`](docs/deploy-render-neon.md)), mas o provedor em uso não foi confirmado nesta atualização, nem o commit publicado.
- **Verificação de saúde:** `/healthz/`, que responde sem consultar o banco.
- **Deploy** somente com autorização explícita do responsável técnico.

Em 18/11/2026 o site publicado foi conferido no navegador com dados fictícios: login, equipamentos, clientes, registro de aluguel, devolução e filtro do histórico funcionaram.

`docs/deploy-render-neon.md` foi escrito antes da publicação e ainda descreve a etapa de preparação; vale como referência de variáveis e comandos, não como retrato do ambiente atual.

## Estrutura de pastas

```text
equipafacil/
├── config/              projeto Django: settings, rotas, autenticação, mensagens
├── equipamentos/        app de equipamentos (models, services, views, forms, testes)
├── clientes/            app de clientes
├── alugueis/            app de aluguéis, devoluções e histórico
├── templates/           páginas HTML (Django Templates)
├── static/              CSS, JavaScript, fontes e Bootstrap
├── tests/               automação Robot Framework
│   ├── Cenario01.robot … Cenario20.robot
│   ├── Keywords/        passos (*_Steps.robot)
│   └── Pages/           seletores (*_Page.robot)
├── scripts/
│   ├── render-build.sh              build no Render
│   ├── validar-gunicorn-linux.sh    validação usada no CI
│   └── robot/                       execução isolada e massas da suíte Robot
├── docs/                documentação técnica
├── .github/workflows/ci.yml
├── requirements.txt, requirements-dev.txt, requirements-robot.txt
├── pyproject.toml       configuração do Ruff e do Black
└── manage.py
```

## Requisitos e rastreabilidade

| ID | Requisito funcional |
|----|---------------------|
| RF001 | Cadastrar equipamentos |
| RF002 | Consultar e pesquisar equipamentos |
| RF003 | Editar informações de equipamentos |
| RF004 | Excluir, inativar ou reativar equipamentos |
| RF005 | Cadastrar, listar, consultar e editar clientes |
| RF006 | Registrar aluguel |
| RF007 | Registrar devolução |
| RF008 | Consultar histórico de aluguéis |
| RF009 | Pesquisar clientes cadastrados |
| RF010 | Filtrar histórico de aluguéis por situação |

RF009 e RF010 foram acrescentados em 10/11/2026, a pedido do professor.

Regras de negócio: RN001 (aluguéis simultâneos e disponibilidade), RN002 (validação de dados), RN003 (integridade e exclusão ou inativação) e RN004 (datas, duração e valores).

Casos de teste: CT01–CT20, dois por requisito funcional (um positivo e um negativo), cada um com um arquivo em `tests/`.

- Resumo dos requisitos, das decisões técnicas e da relação entre RF, RN e CT: [`docs/rastreabilidade.md`](docs/rastreabilidade.md).
- Comportamento de cada módulo: [`docs/equipamentos-operacional.md`](docs/equipamentos-operacional.md), [`docs/clientes-operacional.md`](docs/clientes-operacional.md) e [`docs/alugueis-operacional.md`](docs/alugueis-operacional.md).
- O Documento de Requisitos e o Documento de Casos de Teste são documentos acadêmicos e não são publicados neste repositório.
- Planejamento e critérios de aceite: [quadro EQF no Jira](https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2) (projeto `EQF`, acesso restrito aos membros). O projeto ainda tem atividades abertas no Jira, principalmente pendências documentais.

## Equipe e contribuições

### Responsabilidades planejadas

| Equipe | Integrantes | Responsabilidade |
|--------|-------------|------------------|
| Requisitos | Rafael Ferreira, Ivisson | Documento de requisitos (RF e RN) e sua revisão |
| Desenvolvimento | Rickelme David | Backend, banco de dados, regras de negócio, integração, infraestrutura e coordenação técnica |
| Desenvolvimento | Raphael Eloi | Frontend: templates, Bootstrap e apresentação |
| Testes de Software | Alexandre Abreu, Vinícius Soares | Casos de teste em Gherkin, execução e registro de resultados |

### Automação Robot Framework: divisão e autoria

"Responsável designado" é a divisão originalmente planejada pela equipe. "Implementação registrada" segue a autoria dos commits no histórico do Git.

| Cenários | Responsável designado | Implementação registrada | Correções posteriores |
|----------|------------------------|-------------------|-----------------------|
| CT01, CT03, CT05, CT07 | Rafael Ferreira | Rickelme David, com apoio do Claude Code (PR #23) | — |
| CT02, CT04, CT06, CT08 | Vinícius Soares | Vinícius Soares (PR #21): cenários e massas | Rickelme David: keywords e validações (PR #25) e formatação (PR #24) |
| CT09, CT10, CT17, CT18 | Alexandre Abreu | Alexandre Abreu (PR #22) | Rickelme David: formatação (PR #24) |
| CT11, CT12, CT13 | Rickelme David | Rickelme David (PR #19) | — |
| CT14, CT15 | Raphael Eloi | Raphael Eloi (PR #20) | — |
| CT16 e infraestrutura | Rickelme David | Rickelme David (PR #18) | — |
| CT19, CT20 | Ivisson | Ivisson (PR #26) | Rickelme David: validações e lint (PR #27) |

- CT01, CT03, CT05 e CT07 foram implementados por Rickelme David, com apoio do Claude Code.
- A integração do Robot ao GitHub Actions (PR #28) é de Rickelme David.
- Os commits de Rickelme David e os de Raphael Eloi na automação registram o Claude Code como coautor.

### Revisões

A regra de colaboração do projeto pede revisão por outro integrante antes do merge (veja [Fluxo de qualidade](#fluxo-de-qualidade)). No histórico consultado em 19/11/2026, os Pull Requests #1, #2 e #17 têm aprovação registrada no GitHub, feita por Raphael Eloi; os demais não têm revisão registrada.

## Limitações conhecidas

### Produto

- Aluguel registrado não pode ser cancelado nem editado; a devolução não pode ser corrigida.
- Não há multa por atraso, reserva, pagamento nem exclusão de clientes.
- Não há cadastro público, recuperação de senha por e-mail, limite de tentativas de login nem política de segurança de conteúdo (CSP).
- Os campos de data usam o controle nativo do navegador, que exibe o formato conforme o idioma do próprio navegador (dia/mês/ano com o navegador em português).
- O histórico não tem paginação.

### Testes

- Os cenários Robot usam a data atual de America/Recife; uma execução na virada do dia pode falhar sem que haja defeito.
- CT07 e CT08 comprovam a exclusão e o bloqueio pela interface, não por consulta ao banco.
- O controle negativo do CT16 (`scripts/robot/controles/`) é executado manualmente e não roda no CI.
- A suíte Robot roda em SQLite; as restrições e a concorrência no PostgreSQL são cobertas pelos testes Django.

### Infraestrutura

- O job do Robot não é obrigatório para o merge.
- A preparação do Chromium no CI depende das bibliotecas de sistema da imagem `ubuntu-24.04`.
- As dependências indiretas da biblioteca Browser não têm versão fixada.
- O primeiro acesso ao site publicado pode demorar se o serviço estiver ocioso.
- Pendência: parte da documentação em `docs/` descreve etapas anteriores do projeto e ainda não foi atualizada (`deploy-render-neon.md`, `GUIA_EQUIPE_AUTOMACAO_ROBOT.md` e `publicacao-e-colaboracao.md`).

## Como colaborar

### Branches

| Branch | Uso |
|--------|-----|
| `main` | Versão integrada. Protegida: só recebe alterações por Pull Request |
| `docs/<descricao>` | Documentação |
| `feat/backend-eqf-NN-<descricao>` | Backend, banco e regras de negócio |
| `feat/frontend-eqf-NN-<descricao>` | Templates, estilos e interface |
| `fix/eqf-NN-<descricao>` | Correções |
| `test/<descricao>` | Automação de testes (opcional) |
| `chore/<descricao>` | Manutenção |

`NN` é o número da atividade no Jira. Crie a branch a partir da `main` atualizada e nunca faça commits diretamente na `main`.

Antes de alterar telas ou regras, leia o [guia de integração frontend ↔ backend](docs/guia-integracao-frontend-backend.md); antes de alterar a automação, leia [`docs/testes-robot.md`](docs/testes-robot.md).

### Fluxo de qualidade

1. **Planejamento antes da implementação:** confirme a atividade do Jira e os RF, RN e CT envolvidos.
2. **Testes automatizados** vinculados aos RF e aos cenários CT; nenhuma funcionalidade é concluída sem testes passando.
3. **Commits semânticos** em português ([Conventional Commits](https://www.conventionalcommits.org/pt-br/)), por exemplo `feat: adiciona cadastro de equipamentos`.
4. **Verificação de segurança** antes de cada commit e PR: revise o diff e confirme que não há segredos, `.env` ou dados reais.
5. **Pull Request** com o template, citando a atividade do Jira e os RF, RN e CT relacionados.
6. **Code review** humano, por integrante diferente do autor, antes do merge. Esta é a regra para mudanças futuras; o histórico dos Pull Requests anteriores está na seção [Revisões](#revisões).
7. **Alterações de requisitos** passam por revisão humana das equipes responsáveis e são registradas no Jira.
8. **Deploy** somente após autorização explícita do responsável técnico (Rickelme David).

**Nunca** publique senhas, tokens, arquivos `.env` ou dados reais de pessoas. Use `.env.example` com valores fictícios.

## Licença

Projeto acadêmico, sem licença de uso definida até o momento.
