# CLAUDE.md — EquipaFácil

Instruções para sessões do Claude Code neste repositório. Leia antes de qualquer alteração. A apresentação do projeto para visitantes está no `README.md`; este arquivo traz só o que orienta o trabalho.

## Visão do projeto

EquipaFácil é um sistema web acadêmico (UNIBRA, Qualidade de Software, ADS5NA 2026.2) de gestão de aluguel de equipamentos, usado por funcionários autenticados de uma locadora: equipamentos, clientes, aluguéis, devoluções e histórico.

- **Arquitetura:** monólito Django com páginas renderizadas no servidor. Fluxo: templates → views → serviços (`*/services.py`) → models (ORM) → PostgreSQL. Não há API REST nem SPA.
- **Stack:** Python 3.13 (`.python-version`) e **Django 5.2 LTS** (framework definido; não sugerir troca), versão exata em `requirements.txt` (5.2.18); mudanças de versão só com revisão. Django Templates + Bootstrap 5.3 servido como estático local. PostgreSQL. Django Auth, sem cadastro público e sem recuperação de senha por e-mail; contas de funcionários criadas no Django Admin (D15).
- **Organização:** projeto `config`; apps `equipamentos`, `clientes` e `alugueis`; `templates/`; `static/`; automação em `tests/` e `scripts/robot/`; documentação em `docs/`.
- **Publicação:** https://equipafacil.onrender.com/ — Web Service no Render, com Gunicorn e WhiteNoise; build em `scripts/render-build.sh`; banco informado por `DATABASE_URL`.
- **Planejamento:** Jira, projeto `EQF` — https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2

## Fontes e decisões

- **Especificação técnica v3** no Jira (épicos EQF-4 Requisitos, EQF-5 Desenvolvimento, EQF-6 Testes): referência de **planejamento**. Resumo em `docs/rastreabilidade.md`.
- **Documento de Requisitos** (v1.1; v1.3 com RF009 e RF010) e **Documento de Casos de Teste** (v1.4, com CT17–CT20): documentos **acadêmicos**, fora do Git — nunca adicione o DOCX ao repositório. A v3 e o documento de requisitos não são versões concorrentes do mesmo arquivo.
- **Decisões I1–I5**: aprovadas por Rickelme em 01/11/2026. O detalhamento está no Jira e no Documento v1.1; `docs/rastreabilidade.md` não o reproduz. Antes de implementar algo afetado por elas (retirada futura, correção de registros, reativação, prioridades, armazenamento do CPF), consulte a decisão registrada; se não estiver disponível na sessão, pergunte.
- **Decisões complementares D10–D15**: aprovadas por Rickelme e registradas na descrição do EQF-5 em 01/11/2026. Complementam a interpretação técnica dos RF e RN, sem alterar o texto normativo:
  - D10 — inativação de equipamento sem aluguel aberto, com ou sem histórico (RF004);
  - D11 — normalização do código e unicidade sem diferenciar maiúsculas e minúsculas (RF001, RF003, RN002);
  - D12 — validações adicionais de CPF e telefone (RF005, RN002);
  - D13 — aluguel em formulário único, com resumo antes da gravação (RF006);
  - D14 — clientes consultados pela listagem, sem página de detalhe (RF005); a parte "sem pesquisa" foi revisada pela D16;
  - D15 — contas de funcionários provisionadas pelo administrador via Django Admin.
- **D16, RF009 e RF010**: aprovados tecnicamente por Rickelme em 10/11/2026 no EQF-5 (comentário 10078), a pedido do professor. A lista de clientes oferece pesquisa por nome ou CPF (parcial ou completo, com ou sem máscara; sem pesquisa insensível a acentos). O histórico é filtrado por situação, na ordem `-data_retirada, -pk`; filtro desconhecido vale "Todas".
- O contrato técnico (`docs/contrato-tecnico-frontend-backend.md`), a modelagem proposta e o plano de backend entraram na `main` pelo PR #2, aprovado por Raphael em 15/11/2026. Mudanças no contrato frontend × backend são combinadas entre Rickelme e Raphael antes de implementar.
- A validação documental dos requisitos por Rafael Ferreira e Ivisson não está registrada: **não declare homologação por eles**. Divergência com o documento acadêmico é registrada para a equipe de Requisitos, não resolvida pelo Claude.

## Regras de domínio que não podem ser violadas

- Toda regra e todo cálculo ficam no **backend**; campo somente leitura na tela não substitui validação no servidor.
- Valores monetários com `DecimalField`/`Decimal`, duas casas — **nunca `float`**.
- "Data atual" sempre no fuso `America/Recife`, nunca o dia UTC.
- Código de equipamento único, sem diferenciar maiúsculas de minúsculas (D11); CPF único, validado e armazenado com 11 dígitos (D12, I5).
- Disponibilidade é **derivada** (ativo e sem aluguel em aberto); não criar campo manual. A situação do aluguel (Ativo, Atrasado, Encerrado, Encerrado com atraso) também é calculada, nunca armazenada.
- No máximo um aluguel em aberto por equipamento, com proteção contra concorrência (restrição no banco e transação no serviço).
- Retirada não anterior à data atual; devolução prevista igual ou posterior à retirada.
- Diárias inclusivas: `(prevista − retirada) + 1`; diária e valor contratado congelados no registro.
- Só `acao=registrar` grava o aluguel; a prévia (`acao=previa`) nunca grava (D13).
- Devolução única, com data entre a retirada e a data atual; sem multa.
- Aluguel registrado não é editado nem cancelado; devolução não é corrigida.
- Código do equipamento e CPF do cliente não mudam depois do primeiro aluguel.
- Equipamento com histórico não é excluído; equipamento com aluguel em aberto não é inativado (D10). Cliente não é excluído (RN003).
- Categorias fixas: Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil, Outros.

Detalhes em `docs/modelagem-implementada.md` e nos documentos operacionais de cada módulo.

## Escopo

- Implemente apenas requisitos aprovados (RF001–RF010, RN001–RN004 e decisões D1–D9, N2–N6, TZ, I1–I5 e D10–D16).
- Não invente requisitos, campos, telas ou integrações (ex.: multa, WhatsApp, reservas, pagamentos).
- Ambiguidade de requisito → pare e pergunte; registre a dúvida para o Jira em vez de decidir sozinho.
- Não crie funcionalidades, dependências, configuração no Render ou no banco hospedado, nem deploy, a menos que a tarefa da sessão autorize explicitamente.
- Mudanças em requisitos, regras de negócio ou cenários de teste exigem revisão humana das equipes responsáveis e registro no Jira — nunca são decididas pelo Claude.

## Convenções de código

- PEP 8, formatação com `black` e lint com `ruff`, configurados em `pyproject.toml` (versões em `requirements-dev.txt`). Formate só os arquivos alterados na atividade.
- Nomes de domínio em português, coerentes com a especificação (`Equipamento`, `Cliente`, `Aluguel`); código Python em `snake_case`, classes em `PascalCase`.
- Type hints em funções de serviço; regras de negócio em camada de serviço ou model, não em views ou templates.
- Mensagens ao usuário em português, centralizadas em `config/mensagens.py`, conforme a tabela de mensagens do EQF-5.
- Templates: saída sempre com o escape automático do Django (sem `|safe` em dados do usuário); todo POST com `{% csrf_token %}`; logout por POST. Rotas, variáveis e campos de cada tela seguem o contrato e os documentos operacionais.

## Qualidade e testes

Comandos, a partir da raiz, com o ambiente virtual ativo:

```powershell
ruff check .
black --check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test                    # SQLite: OK (skipped=25)
python manage.py test --keepdb           # PostgreSQL local: OK, sem pulados
python scripts/robot/executar.py         # suíte Robot, CT01–CT20
python scripts/robot/executar.py tests/Cenario16.robot
```

- Antes de cada commit: `ruff check .` e `black --check .`.
- Nenhuma funcionalidade é considerada concluída sem testes automatizados passando.
- Testes Django: rode com `DJANGO_DEBUG=True`; no SQLite, `DB_ENGINE=sqlite` e uma `DJANGO_SECRET_KEY` temporária. Relacione testes aos cenários `CTxx` e às coberturas complementares `FCxx`. Datas relativas à data atual em `America/Recife`.
- Migrations locais só rodam no banco de testes `test_equipafacil_dev` (com `--keepdb`); nunca no `equipafacil_dev` nem no banco hospedado sem autorização explícita.

### Robot Framework

- `tests/CenarioNN.robot`: um arquivo por CT, **sem seletores**.
- `tests/Keywords/*_Steps.robot`: `*** Settings ***` e `*** Keywords ***`.
- `tests/Pages/*_Page.robot`: somente `*** Variables ***`, com XPaths. **Nunca duplicar um XPath** entre Pages.
- Biblioteca Browser. Massas em `scripts/robot/massas/ctNN.py`, com dados fictícios.
- **Isolamento:** `scripts/robot/executar.py` sobe o Django em `127.0.0.1:8765` com `scripts/robot/settings_robot.py`, que força o SQLite `resultados-robot/robot.sqlite3`, descarta `DATABASE_URL` e ignora o `.env`. `massa.py` recusa banco não isolado. A senha entra por `Fill Secret`, e só o nome da variável aparece nos relatórios. Opções do script usam `=` (ex.: `--opcao=valor`).
- Execução sequencial; não rodar suítes em paralelo sobre a mesma massa.
- Não alterar código funcional do Django para forçar PASS; não enfraquecer asserções para obter PASS.
- Não alterar `Common_Steps.robot`, `executar.py`, `massa.py` nem `settings_robot.py` sem a tarefa pedir.
- Guia completo: `docs/testes-robot.md`.

### Integração contínua

`.github/workflows/ci.yml`, em PRs para a `main` e pushes na `main`, com quatro jobs: `postgresql` (pip check, Ruff, Black, check, migrations e testes no PostgreSQL 18), `sqlite`, `gunicorn` e `robot` (CT01–CT20, artefato `relatorios-robot`). Não usa segredos nem serviços externos e não substitui a execução local antes do commit. O job `robot` não é obrigatório para o merge.

## Git e GitHub

1. **Planejar antes de implementar**: confirmar a atividade do Jira e os RF, RN e CT envolvidos; apresentar um plano curto antes de escrever código.
2. **Uma branch por atividade**, criada a partir da `main` atualizada. Nunca commitar direto na `main`.
   **Uma única pasta de trabalho** (a raiz do repositório), com uma branch ativa por vez, trocada com `git switch`. **Não use `git worktree`** neste repositório (decisão de Rickelme em 02/11/2026). Antes de trocar de branch, a árvore precisa estar limpa; não use `git reset --hard`, `git clean` nem descarte alterações para trocar.

   | Branch | Uso |
   |--------|-----|
   | `main` | Versão integrada, sempre estável |
   | `docs/<descricao>` | Documentação |
   | `feat/backend-eqf-NN-<descricao>` | Backend, banco e regras de negócio |
   | `feat/frontend-eqf-NN-<descricao>` | Templates, estilos e interface |
   | `fix/eqf-NN-<descricao>` | Correções |
   | `test/<descricao>` | Automação de testes (opcional) |
   | `chore/<descricao>` | Manutenção (dependências, ferramentas, configuração) |

3. **Commits semânticos** em português, só com os prefixos `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`. O histórico tem dois commits com `style:` e `perf:`; não repita e não reescreva.
4. **Verificação de segurança** antes de cada commit: revisar o diff, confirmar que só entraram arquivos da atividade e que não há segredo, `.env` ou dado real.
5. **Pull Request** com o template do repositório, citando a atividade Jira e os RF, RN e CT; **code review humano obrigatório antes do merge**, por integrante diferente do autor. A regra vale para toda mudança futura.
6. **Merge:** `gh pr merge` é negado em `.claude/settings.json`; o merge é feito manualmente por um integrante. Sem force push, sem rebase de branch publicada, sem excluir branches.
7. **Deploy somente após autorização explícita** de Rickelme.

### Limites do Claude Code

- Não fazer push, abrir PR, merge, deploy nem alterar recursos externos (GitHub, Jira, Render, banco hospedado) sem autorização explícita na tarefa da sessão. Autorização dada em uma tarefa não vale para a seguinte.
- Este arquivo orienta, mas **não é controle técnico**. Os bloqueios efetivos são as permissões em `.claude/settings.json` e o ruleset da `main` no GitHub. Não os altere nem os contorne.
- Não alterar a identidade global do Git nem a conta ativa do `gh`.
- **Autoria:** nunca alterar autor de commit para simular participação de outro integrante; não reescrever histórico. Não atribuir a ninguém implementação, execução, revisão ou aprovação sem evidência (commit, PR, revisão registrada ou comentário da própria pessoa).
- **Jira:** não alterar atividades sem pedido explícito; antes de qualquer escrita, conferir a conta em `/myself`. Não concluir atividades de outros integrantes em nome deles.

## Segurança

- Nunca publicar credenciais (GitHub, Jira, Render, banco, `SECRET_KEY`, URLs de banco com senha). Não pedir, exibir nem guardar senhas.
- Configuração por variáveis de ambiente; apenas `.env.example` com valores fictícios entra no Git.
- Não versionar dados reais de clientes (CPF, telefone, e-mail). Usar dados fictícios em fixtures e massas.
- Não acessar dados de produção sem necessidade; não executar migrations, massas de teste nem testes automatizados em produção.
- Nunca usar a `DATABASE_URL` de produção em testes Django ou na suíte Robot.
- Não alterar o Render nem o banco hospedado sem autorização explícita; não executar operações destrutivas sem aprovação.
- Escritas no site publicado (ex.: registrar aluguel em demonstração) só com autorização específica, com dados fictícios, e sem repetir a operação se a resposta for ambígua.
- Não publicar documentos originais do professor nem dados pessoais da equipe sem avaliação prévia.
- Se encontrar um segredo commitado, pare e avise: ele deve ser revogado, não apenas removido.

## Responsabilidades

| Pessoa / equipe | Papel |
|-----------------|-------|
| Rickelme David | Backend, banco de dados, regras RN001–RN004, autenticação, fuso, integração, infraestrutura, deploy, revisão técnica |
| Raphael Eloi | Frontend: templates, Bootstrap, HTML/CSS/JS, responsividade, exibição de estados e mensagens vindas do backend |
| Requisitos (Rafael Ferreira, Ivisson) | Validação acadêmica dos RF e RN |
| Testes (Alexandre Abreu, Vinícius Soares) | Validação acadêmica dos cenários CT01–CT20 e execução dos testes |

A divisão e a autoria efetiva da automação Robot estão no `README.md` (seção "Equipe e contribuições"). CT01, CT03, CT05 e CT07 foram implementados por Rickelme, com apoio do Claude Code; não atribua essa implementação a outro integrante.

## Estado atual (19/11/2026)

- `main` em `01d038d`. RF001–RF010 implementados, com frontend definitivo e sistema publicado.
- Automação encerrada tecnicamente: 20 cenários Robot (CT01–CT20) na `main` e no CI.
- Última execução auditada: GitHub Actions 44413841611 (18/11/2026) — quatro jobs aprovados; 424 testes Django; Robot 20/20.
- Limitações conhecidas: job `robot` não obrigatório; Chromium do CI depende das bibliotecas da imagem `ubuntu-24.04`; dependências indiretas da Browser sem versão fixada; cenários sensíveis à virada do dia; controle negativo do CT16 fora do CI; CT07 e CT08 verificados só pela interface.
- **O projeto não está encerrado no Jira:** há atividades abertas no projeto `EQF`. Consulte o estado atual das atividades antes de qualquer operação no Jira e antes de citar números ou situações.
- Histórico de revisões (consultado em 19/11/2026): só os PRs #1, #2 e #17 têm aprovação registrada no GitHub (Raphael). Os PRs anteriores não cumpriram todos a regra de revisão; não declare revisões que não constam no histórico.
- O commit publicado no Render e o provedor do banco não foram reconferidos; não afirme sem verificar.
- Pendência — documentos desatualizados, que descrevem etapas anteriores: `docs/deploy-render-neon.md`, `docs/GUIA_EQUIPE_AUTOMACAO_ROBOT.md`, `docs/publicacao-e-colaboracao.md` e o comentário inicial de `config/urls.py`.

## Referências internas

| Assunto | Documento |
|---------|-----------|
| Requisitos, decisões e relação RF × RN × CT | `docs/rastreabilidade.md` |
| Modelos e restrições | `docs/modelagem-implementada.md` |
| Equipamentos, clientes e aluguéis (rotas, regras, mensagens) | `docs/equipamentos-operacional.md`, `docs/clientes-operacional.md`, `docs/alugueis-operacional.md` |
| Contrato e integração frontend × backend | `docs/contrato-tecnico-frontend-backend.md`, `docs/guia-integracao-frontend-backend.md` |
| Frontend e design system | `docs/frontend-implementado.md`, `equipafacil-design-system.md` |
| Automação Robot e CI | `docs/testes-robot.md` |
| PostgreSQL local | `docs/postgresql-local.md` |
| Hospedagem (variáveis e comandos) | `docs/deploy-render-neon.md` |
