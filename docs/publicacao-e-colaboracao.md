# Publicação do backend e colaboração com o frontend

> **Situação:** plano executado em 02/11/2026. As cinco branches do backend foram publicadas e integradas à `main` com merge commit, junto com o PR #1 e o guia (PR #3); a `main` chegou a `85b4d1a` (marco). O PR #2 (contrato) continua em rascunho. A seção "Ordem de publicação" fica como registro histórico do plano.

**Raphael precisa receber a estrutura Django pelo GitHub para iniciar o frontend.** Enquanto o backend não for publicado, não há templates, rotas nem variáveis reais sobre os quais ele possa trabalhar.

## Divisão de arquivos

Conforme a seção 10 do contrato proposto (PR #2): cada arquivo tem um responsável, e ninguém edita arquivo do outro sem acordo registrado no PR.

| Responsável | Arquivos |
|-------------|----------|
| **Frontend (Raphael)** | `templates/**` (`base.html`, `includes/**` e os templates de cada página) e `static/**` (`static/css/**`, `static/js/**` — inclusive a prévia em JavaScript de P07 —, `static/img/**`, `static/vendor/bootstrap/**`) |
| **Backend (Rickelme)** | `manage.py`, `config/**`, `equipamentos/**`, `clientes/**`, `alugueis/**` (modelos, serviços, formulários, views, URLs, `admin.py`, `migrations/**`, `tests/**`), `requirements*.txt`, `pyproject.toml`, `scripts/**`, `.env.example`, `CLAUDE.md`, `.claude/**`, documentação técnica do backend |
| **Os dois, por PR revisado pelos dois** | Contrato técnico, guia de integração e este documento |

### Templates provisórios do backend

Criados só para validar o backend; **não são arquivos definitivos de Raphael** e serão substituídos por ele:

| Template | Etapa | Contrato que a troca deve manter |
|----------|-------|----------------------------------|
| `templates/registration/login.html` | DEV-02 | `form`, `next`, POST com CSRF |
| `templates/inicio.html` | DEV-02 a DEV-06 | Links para as áreas; Sair por POST |
| `templates/equipamentos/{lista,formulario,acoes}.html` | DEV-04 | [`equipamentos-operacional.md`](equipamentos-operacional.md) |
| `templates/clientes/{lista,formulario}.html` | DEV-05 | [`clientes-operacional.md`](clientes-operacional.md) |
| `templates/alugueis/{formulario,historico,devolver}.html` | DEV-06 | [`alugueis-operacional.md`](alugueis-operacional.md) |

Ainda não existem `base.html`, `includes/navbar.html`, `includes/messages.html`, `includes/form_errors.html`, Bootstrap local nem arquivos em `static/` (só `static/.gitkeep`). São todos do frontend.

### Arquivos compartilhados que exigem coordenação

| Arquivo | Por quê |
|---------|---------|
| `templates/inicio.html` | Hoje é do backend (provisório) e recebe um link a cada etapa; o definitivo é de Raphael. Combinar o momento da troca para os dois não editarem ao mesmo tempo |
| `templates/registration/login.html` | Provisório do backend; o definitivo (P10) é de Raphael e precisa manter `form`, `next` e o POST com CSRF |
| `config/urls.py` | Do backend. Nomes de rota são contrato: Raphael usa `{% url %}` e pede mudanças por PR |
| Templates de cada app | O backend define campos, variáveis e botões (`acao=previa` e `acao=registrar` em P07, `confirmacao=sim` em P04); Raphael define o HTML. Mudança de variável exige atualizar o contrato |
| `config/settings.py` (`TEMPLATES`, `STATICFILES_DIRS`, WhiteNoise) | Do backend; afeta onde o frontend coloca arquivos. Hoje: `templates/` e `static/` na raiz |
| `*/forms.py` | Do backend. As classes do Bootstrap já vêm dos widgets (`config/formularios.py`); mudanças de campo ou classe são pedidas ao backend |

## Resultado da integração (02/11/2026)

| PR | Ramo | Merge commit na `main` |
|----|------|------------------------|
| #1 | `docs/alinhamento-workspace` | `690ba37` |
| #3 | `docs/guia-integracao-raphael` | `5cc3d3e` |
| #4 | `feat/backend-dev02-foundation` (DEV-02) | `90f8e01` |
| #5 | `feat/backend-eqf-15-modelagem` (DEV-03) | `c1012b6` |
| #6 | `feat/backend-eqf-16-equipamentos` (DEV-04) | `0c24778` |
| #7 | `feat/backend-eqf-17-clientes` (DEV-05) | `3cd5092` |
| #8 | `feat/backend-eqf-18-alugueis` (DEV-06, com `f3ad6d8`) | `85b4d1a` |

- Os commits do backend entraram com os mesmos identificadores. O ramo do guia foi reaplicado sobre o merge do PR #1 antes da integração (`388bbca` → `21b9b39`), com conteúdo idêntico.
- Validação 13A na `main` em `85b4d1a`: 360 testes aprovados no PostgreSQL; no SQLite, 336 aprovados e 24 pulados; fluxo ponta a ponta com o cliente HTTP do Django (17 passos).
- **Raphael agora cria sua branch de frontend a partir da `main`**, não mais de `feat/backend-eqf-18-alugueis`.

## Ordem de publicação

### Situação dos ramos antes da publicação (02/11/2026, histórico)

| Ramo | Commit | Base | Situação |
|------|--------|------|----------|
| `docs/alinhamento-workspace` | `c0625ca` | `main` | PR #1 aberto, aguardando revisão de Raphael |
| `docs/guia-integracao-raphael` | `388bbca` | commit intermediário do PR #1 | Publicado; PR a abrir depois do PR #1 |
| `docs/contrato-tecnico-dev01` | `353b063` | `main` | PR #2 em rascunho, aguardando aceite |
| `feat/backend-dev02-foundation` | `87d23fb` | `c0625ca` (topo do PR #1) | Local, 22 commits próprios |
| `feat/backend-eqf-15-modelagem` | `ba0493a` | DEV-02 | Local, 5 commits |
| `feat/backend-eqf-16-equipamentos` | `657627a` | DEV-03 | Local, 4 commits |
| `feat/backend-eqf-17-clientes` | `fa1b32f` | DEV-04 | Local, 5 commits |
| `feat/backend-eqf-18-alugueis` | — | DEV-05 | Local (DEV-06) |

Simulação local com `git merge-tree` (sem alterar ramos nem arquivos), na ordem PR #1 → guia → PR #2 → DEV-02 → DEV-03 → DEV-04 → DEV-05 → DEV-06: **sem conflitos** em 02/11/2026.

### Sequência proposta

Regras do ruleset da `main`: PR obrigatório com 1 aprovação, sem exclusão e sem push não fast-forward. Integração por **merge commit** (nunca squash ou rebase), sem bypass de administrador. Cada PR usa o template do repositório e cita a atividade do Jira e os RF/RN/CT.

1. **PR #1** (`docs/alinhamento-workspace`): revisão e aprovação de Raphael; merge commit. Destrava o resto, porque o DEV-02 foi criado sobre ele.
2. **Guia de integração** (`docs/guia-integracao-raphael`): abrir o PR depois do PR #1, que então mostra só os 3 commits do guia.
3. **PR #2** (contrato): sair de rascunho quando Raphael aceitar; merge commit. Pode andar em paralelo às etapas seguintes, porque o backend não altera os arquivos do contrato.
4. **DEV-02** (`feat/backend-dev02-foundation` → `main`, EQF-14). Depois do PR #1, o diff mostra só os 22 commits da fundação.
5. **DEV-03** (`feat/backend-eqf-15-modelagem` → `main`, EQF-15), aberto ou atualizado depois do merge do DEV-02.
6. **DEV-04** (`feat/backend-eqf-16-equipamentos`, EQF-16).
7. **DEV-05** (`feat/backend-eqf-17-clientes`, EQF-17).
8. **DEV-06** (`feat/backend-eqf-18-alugueis`, EQF-18; inclui RF008, ver o aviso em `alugueis-operacional.md`).

Como os merges são merge commits, os commits de cada etapa entram na `main` com os mesmos identificadores: o PR seguinte mostra só os próprios commits, sem rebase. **Opção para revisar em paralelo:** abrir todos os PRs de uma vez, cada um com a base no ramo anterior (DEV-03 com base em DEV-02, e assim por diante), os posteriores em rascunho. Depois de cada merge, mudar a base do PR seguinte para `main` antes de aprovar.

### Acesso mais rápido e seguro para Raphael

> Histórico. Depois da integração, vale a orientação da seção "Resultado da integração": branch de frontend a partir da `main`.

**Recomendação:** quando autorizado, publicar os cinco ramos `feat/backend-*` (os nomes já seguem a tabela do `CLAUDE.md`), sem abrir PR de imediato. Raphael cria seus ramos `feat/frontend-eqf-NN-*` a partir de `feat/backend-eqf-18-alugueis`, que contém DEV-02 a DEV-06, e trabalha só em `templates/**` e `static/**`.

- Nada é mesclado à `main` sem PR aprovado. Os ramos publicados são de trabalho, não versão integrada.
- Quando os PRs do backend forem mesclados por merge commit, o ramo de Raphael continua compatível: os commits do backend já estarão na `main` com os mesmos identificadores.
- Se um PR do backend receber correções, Raphael traz as mudanças com `git merge` do ramo do backend, nunca com rebase.
- Squash ou rebase nos PRs do backend duplicariam commits no histórico de Raphael. Por isso, só merge commit.

**Alternativa:** um ramo único claramente provisório, por exemplo `chore/integracao-provisoria-backend`, no mesmo commit de `feat/backend-eqf-18-alugueis` e com aviso "não mesclar" na descrição. É mais explícito para Raphael, mas é um ramo a mais para manter atualizado e não está na tabela de ramos do `CLAUDE.md`; precisa da decisão de Rickelme.

### Checklist antes de publicar

- [ ] Autorização explícita de Rickelme para o push (e, separadamente, para cada PR).
- [ ] Árvore limpa; suítes PostgreSQL (`--keepdb`, banco de testes) e SQLite verdes; Ruff, Black, `pip check`, `check --deploy` (só `security.W004` esperado).
- [ ] Varredura de segredos no intervalo publicado (`git log -p main..<ramo>`): em 02/11/2026, só valores fictícios (`exemplo.test`, `<usuario>:<senha>`) e nenhum `.env`, banco, `.docx` ou chave versionados.
- [ ] Descrição do PR com dependências ("depende de DEV-02…"), Jira (EQF-14 a EQF-18), RF/RN/CT e divergências com o contrato.
- [ ] Nenhum dado pessoal da equipe ou documento do professor no diff.
