# CLAUDE.md — EquipaFácil

Instruções para sessões do Claude Code neste repositório. Leia antes de qualquer alteração.

## Contexto

EquipaFácil é um sistema web acadêmico (ADS/UNIBRA) de gestão de aluguel de equipamentos, usado por funcionários autenticados de uma locadora: equipamentos, clientes, aluguéis, devoluções e histórico.

- Planejamento: Jira, projeto `EQF` — https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2
- **Especificação técnica v3** no Jira (épicos EQF-4 Requisitos, EQF-5 Desenvolvimento, EQF-6 Testes): referência de **planejamento**. Resumo em `docs/rastreabilidade.md`.
- **Documento de Requisitos v1.1**: documento **acadêmico**, revisado tecnicamente. Não é publicado neste repositório — nunca adicione o DOCX ao Git. A v3 e a v1.1 não são versões concorrentes do mesmo arquivo.
- **Decisões I1–I5**: aprovadas por Rickelme em 01/11/2026. O detalhamento está no Jira e no Documento v1.1; o resumo `docs/rastreabilidade.md` não o reproduz. Antes de implementar algo afetado por I1–I5 (retirada futura, correção de registros, reativação, prioridades, armazenamento do CPF), consulte a decisão registrada; se ela não estiver disponível na sessão, pergunte.
- **Decisões complementares D10–D15**: aprovadas por Rickelme e registradas na descrição do épico EQF-5 no Jira em 01/11/2026. Complementam a interpretação técnica dos RF/RN, sem alterar o texto normativo nem criar requisitos novos:
  - D10 — inativação de equipamento sem aluguel aberto, com ou sem histórico (RF004);
  - D11 — normalização do código e unicidade sem diferenciar maiúsculas e minúsculas (RF001, RF003, RN002);
  - D12 — validações adicionais de CPF e telefone (RF005, RN002);
  - D13 — aluguel em formulário único, com resumo antes da gravação (RF006);
  - D14 — clientes sem pesquisa na primeira versão; consulta pela listagem (RF005);
  - D15 — contas de funcionários provisionadas pelo administrador via Django Admin (D1).

  Resumo em `docs/rastreabilidade.md`. O detalhamento técnico está em `docs/contrato-tecnico-frontend-backend.md`, `docs/modelagem-proposta.md` e `docs/plano-backend-dev01-dev03.md`, que continuam **propostas** até o aceite de Rickelme e Raphael e entram na `main` por PR próprio. Se esses arquivos não existirem na branch da sessão, o contrato do DEV-01 ainda não foi integrado: consulte o EQF-5 e, se a decisão não estiver disponível, pergunte. A equipe de Requisitos avalia se D10, D11 e D12 exigem atualização do Documento v1.1, que trata esses pontos de forma mais geral; divergência com o documento acadêmico é registrada para essa equipe, não resolvida pelo Claude.
- Validação acadêmica final dos requisitos: aguardando Rafael Ferreira e Ivisson.
- Prazos: primeira entrega 03/11/2026; entrega final 15/11/2026.

## Estado atual

Backend de RF001–RF008 **implementado e integrado à `main`** (marco de 02/11/2026: `main` em `85b4d1a`, PRs #1 e #3 a #8, com merge commit). Inclui a fundação DEV-02 (projeto `config`, autenticação nativa com `LoginRequiredMiddleware`, preparação para Render + Neon), os modelos do DEV-03 (`Equipamento`, `Cliente`, `Aluguel`, restrições no PostgreSQL, migrations `0001_initial`) e os fluxos de DEV-04 (equipamentos), DEV-05 (clientes) e DEV-06 (aluguéis, devoluções e histórico, com confirmação explícita `acao=registrar`). Detalhes em `docs/modelagem-implementada.md`, `docs/equipamentos-operacional.md`, `docs/clientes-operacional.md` e `docs/alugueis-operacional.md`. Validação 13A: 360 testes aprovados no PostgreSQL; no SQLite, 336 aprovados e 24 pulados. **Todos os templates são provisórios**: o frontend definitivo (DEV-07, Raphael) e a homologação visual estão pendentes, e o contrato técnico (PR #2) continua em rascunho, sem aprovação. **Não existem banco Neon, serviço no Render nem deploy.** Migrations só rodam no banco de testes `test_equipafacil_dev` (com `--keepdb`); nunca no `equipafacil_dev` nem no Neon sem autorização explícita. Não crie funcionalidades novas, templates definitivos (são do frontend), dependências novas, banco Neon, configuração no Render nem deploy, a menos que a tarefa da sessão autorize explicitamente.

## Stack definida

- Python 3.13 + **Django 5.2 LTS** (framework definido; não sugerir troca). Versão exata fixada em `requirements.txt` (5.2.18, escolhida em DEV-02); mudanças de versão só com revisão.
- Django Templates + Bootstrap no frontend (sem SPA).
- PostgreSQL (Neon previsto); Render previsto para hospedagem.
- Django Auth para autenticação (sem cadastro público, sem recuperação de senha por e-mail).

## Responsabilidades

| Pessoa / equipe | Papel |
|-----------------|-------|
| Rickelme David | Backend, banco de dados, regras RN001–RN004, autenticação, fuso, integração, infraestrutura, deploy, revisão técnica |
| Raphael Eloi | Frontend: templates, Bootstrap, HTML/CSS/JS, responsividade, exibição de estados e mensagens vindas do backend |
| Requisitos (Rafael Ferreira, Ivisson) | Validação acadêmica dos RF/RN |
| Testes (Alexandre Abreu, Vinícius Soares) | Validação acadêmica dos cenários CT01–CT16 e execução dos testes |

Mudanças no contrato frontend × backend devem ser combinadas entre Rickelme e Raphael antes de implementar.

## Regras de domínio que não podem ser violadas

- Toda regra e todo cálculo ficam no **backend**; campo somente leitura na tela não substitui validação no servidor.
- Valores monetários com `DecimalField`/`Decimal`, duas casas — **nunca `float`**.
- "Data atual" sempre no fuso `America/Recife`, nunca o dia UTC.
- Disponibilidade é **derivada** (ativo e sem aluguel ativo); não criar campo manual.
- No máximo um aluguel ativo por equipamento, com proteção contra concorrência.
- Diárias inclusivas: `(prevista − retirada) + 1`; valor contratado congelado no registro.
- Categorias fixas: Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil, Outros.

## Escopo

- Implemente apenas requisitos aprovados (RF001–RF008, RN001–RN004 e decisões D1–D9, N2–N6, TZ, I1–I5 e D10–D15), conforme a especificação técnica v3, incluindo as decisões complementares registradas no EQF-5, e o Documento de Requisitos v1.1.
- Não invente requisitos, campos, telas ou integrações (ex.: multa, WhatsApp, reservas, pagamentos).
- Ambiguidade de requisito → pare e pergunte; registre a dúvida para o Jira em vez de decidir sozinho.
- Não altere atividades do Jira sem pedido explícito.

## Convenções de código Python

- PEP 8, formatação com `black` e lint com `ruff`, configurados em `pyproject.toml` (versões em `requirements-dev.txt`). Antes de cada commit: `ruff check .` e `black --check .`; formate só os arquivos alterados na atividade.
- Nomes de domínio em português, coerentes com a especificação (`Equipamento`, `Cliente`, `Aluguel`); código Python em `snake_case`, classes em `PascalCase`.
- Type hints em funções de serviço; regras de negócio em camada de serviço/model, não em views ou templates.
- Mensagens ao usuário em português, conforme a tabela de mensagens do épico EQF-5.

## Testes

- Nenhuma funcionalidade é considerada concluída sem testes automatizados passando (`python manage.py test`, com o runner padrão do Django definido em DEV-02).
- Relacione testes aos cenários `CTxx` e às coberturas complementares `FCxx`.
- Datas em testes devem ser relativas à data atual em `America/Recife`.
- O CI (`.github/workflows/ci.yml`) repete as verificações em PRs para a `main`: PostgreSQL 18 e SQLite no runner, Ruff, Black, `check`, migrations e Gunicorn em Linux. Não substitui a execução local antes do commit e não usa segredos nem serviços externos.

## Fluxo de trabalho

1. **Planejar antes de implementar**: confirmar a atividade do Jira, os RF/RN/CT envolvidos e o contrato frontend × backend; apresentar um plano curto antes de escrever código.
2. **Uma branch por atividade**, criada a partir da `main` atualizada. Nunca commitar direto na `main`.
   **Uma única pasta de trabalho** (a raiz do repositório), com uma branch ativa por vez, trocada com `git switch`. **Não use `git worktree`** neste repositório (decisão de Rickelme em 02/11/2026). Antes de trocar de branch, a árvore precisa estar limpa; não use `git reset --hard` nem descarte alterações para trocar.

   | Branch | Uso |
   |--------|-----|
   | `main` | Versão integrada e revisada, sempre estável |
   | `docs/<descricao>` | Documentação |
   | `feat/backend-eqf-NN-<descricao>` | Backend, banco e regras de negócio (ex.: `feat/backend-eqf-16-equipamentos`) |
   | `feat/frontend-eqf-NN-<descricao>` | Templates, estilos e interface |
   | `fix/eqf-NN-<descricao>` | Correções |
   | `chore/<descricao>` | Manutenção (dependências, ferramentas, configuração) |

3. **Testes automatizados** vinculados aos RF e CT, passando antes de declarar algo concluído (ver seção Testes).
4. **Commits semânticos** em português: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
5. **Verificação de segurança** antes de cada commit: revisar o diff, confirmar que só entraram arquivos da atividade e que não há segredo, `.env` ou dado real.
6. **Pull Request** com o template do repositório, citando a atividade Jira e os RF/RN/CT; **code review humano obrigatório antes do merge**.
7. Mudanças em requisitos, regras de negócio ou cenários de teste exigem revisão humana das equipes responsáveis e registro no Jira — nunca são decididas pelo Claude.
8. **Deploy somente após autorização explícita** de Rickelme.

### Limites do Claude Code

- Não fazer push, abrir PR, merge, force push, deploy nem alterar recursos externos (GitHub, Jira, Neon, Render) sem autorização explícita na tarefa da sessão.
- Este arquivo orienta, mas **não é controle técnico**. Os bloqueios efetivos são as permissões em `.claude/settings.json` e o ruleset da `main` no GitHub. Não os altere para afrouxar regras sem pedido explícito.

## Segurança

- Nunca publicar credenciais (GitHub, Jira, Neon, Render, `SECRET_KEY`, URLs de banco com senha).
- Configuração por variáveis de ambiente; apenas `.env.example` com valores fictícios entra no Git.
- Não versionar dados reais de clientes (CPF, telefone, e-mail). Usar dados fictícios em fixtures.
- Não publicar documentos originais do professor nem dados pessoais da equipe sem avaliação prévia.
- Se encontrar um segredo commitado, pare e avise: ele deve ser revogado, não apenas removido.
