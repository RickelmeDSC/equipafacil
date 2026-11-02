# Plano backend — DEV-01 a DEV-03

> **PROPOSTA — AGUARDANDO VALIDAÇÃO DE RICKELME E RAPHAEL.**
>
> Versão 0.3 — 01/11/2026. Consolida o escopo oficial de DEV-01 a DEV-03 no Jira, as decisões D10–D15 e o contrato visual do EQF-5. Planejamento apenas: **nenhuma atividade foi iniciada nem concluída**, não existe código Django no repositório e este documento não altera status, prazos, prioridades, dependências nem comentários do Jira.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [modelagem proposta](modelagem-proposta.md).

## 1. Retrato do Jira

Retrato da auditoria de 01/11/2026, não uma consulta em tempo real.

| Atividade | Título | Status | Responsável | Prioridade | Prazo | Comentários e anexos |
|-----------|--------|--------|-------------|------------|-------|----------------------|
| EQF-13 — DEV-01 | Definir arquitetura Django e organização do projeto | A Fazer | Rickelme, com Raphael como colaborador | Medium | 06/11/2026 | Nenhum |
| EQF-14 — DEV-02 | Preparar repositório, ambiente virtual, dependências e configuração inicial | A Fazer | Rickelme | Medium | 07/11/2026 | Nenhum |
| EQF-15 — DEV-03 | Modelar banco de dados de equipamentos, clientes e aluguéis | A Fazer | Rickelme | Medium | 08/11/2026 | Nenhum |
| EQF-10 — REQ-04 | Regras de negócio | Em Andamento | Ivisson | Highest | 03/11/2026 | Nenhum checklist, comentário ou anexo; sem evidência de validação final |

A documentação produzida localmente ainda não está registrada no Jira.

## 2. Escopo oficial e critérios de aceite

**DEV-01 (EQF-13):**

1. Aplicações Django definidas e justificadas.
2. Estrutura de pastas e convenções documentadas.
3. Decisões arquiteturais registradas na atividade.

Decisões técnicas já presentes na especificação: Django Auth, páginas operacionais protegidas, contas criadas administrativamente, `America/Recife`, valores com Decimal e Bootstrap no layout base.

**DEV-02 (EQF-14) — não executar antes da autorização:**

1. Repositório acessível.
2. Ambiente virtual e dependências preparados.
3. Projeto Django funcionando sem erros.
4. README com instruções.

Requisitos técnicos: Django Auth; fuso `America/Recife`; configuração inicial de templates e static; estrutura da tela de login; preparação para PostgreSQL por variáveis de ambiente; nenhuma credencial no repositório. Neon e Render ainda não estão autorizados.

**DEV-03 (EQF-15) — bloqueado:**

1. Models `Equipamento`, `Cliente` e `Aluguel`.
2. RN001–RN004 refletidas.
3. Migrations aplicadas sem erro.
4. Diagrama do modelo anexado à atividade.

Regras: no máximo um aluguel aberto por equipamento, com restrição efetiva no PostgreSQL; preservação do histórico; sem exclusão em cascata; Decimal para dinheiro; `America/Recife`; código e CPF imutáveis após o primeiro aluguel. Detalhes na [modelagem](modelagem-proposta.md).

## 3. Decisões D10–D15 (aprovadas por Rickelme)

| Decisão | Conteúdo | Onde foi incorporada |
|---------|----------|----------------------|
| D10 — Inativação | Todo equipamento ativo sem aluguel aberto pode ser inativado, com ou sem histórico; exclusão física só sem histórico e sem aluguel aberto; reativação exige dados válidos e nenhum aluguel aberto | Modelagem §2; contrato P04 e §9.2 |
| D11 — Código | Remove espaços das extremidades; único sem diferenciar maiúsculas; grafia preservada; reforço no PostgreSQL; imutável após o primeiro aluguel | Modelagem §2; contrato §7.1 |
| D12 — CPF e telefone | CPF: remove só pontos e hífen, recusa outros caracteres, 11 dígitos, dígitos verificadores, recusa dígitos todos iguais, único, formatado, imutável. Telefone: opcional, máscara comum, DDD, 10 ou 11 dígitos, recusa outros caracteres, formatado | Modelagem §3; contrato §7.2 |
| D13 — Aluguel em uma etapa | Formulário único; resumo antes de registrar; aviso de ausência de cancelamento; sem página adicional; backend recalcula e revalida | Modelagem §4; contrato §7.3 e P07 |
| D14 — Clientes | Consulta pela listagem; cadastro e edição; sem pesquisa; sem página de detalhe | Contrato P05 |
| D15 — Funcionários | Django Auth; contas pelo Django Admin; Admin restrito a administradores autorizados; sem cadastro público; sem recuperação de senha; sem perfis novos | Contrato §3; modelagem §7 |

A validação acadêmica da autenticação como requisito transversal continua pendente.

## 4. Como DEV-01 atende os critérios de aceite

| Critério | Evidência local | Situação |
|----------|-----------------|----------|
| 1. Aplicações definidas e justificadas | [Contrato §2](contrato-tecnico-frontend-backend.md#2-arquitetura-dev-01) | Proposta, aguardando aceite |
| 2. Estrutura e convenções documentadas | Contrato §2 a §10; [modelagem](modelagem-proposta.md) | Proposta, aguardando aceite |
| 3. Decisões registradas na atividade | Texto da seção 11 deste plano | **Não registrado** no EQF-13 |

DEV-01 **não** deve ser marcado como concluído antes do aceite de Rickelme e Raphael e do registro no Jira.

## 5. Dependências formais

1. **DEV-01** → **DEV-02** → **DEV-03** → **DEV-04** e **DEV-05** → **DEV-06** → **DEV-07** → **DEV-08**.
2. **DEV-03** também depende de **REQ-04 (EQF-10)**, em andamento: continua **formalmente bloqueado**.
3. **DEV-02** bloqueia **QA-05** (EQF-25, dados de teste).
4. **Frontend (Raphael):** design estático pode começar já; a integração de cada página depende do contrato aceito e da atividade DEV correspondente.

Nenhuma dependência foi removida e nenhuma atividade bloqueada foi iniciada.

## 6. Cronograma sugerido

Sugestão para discussão, que não altera os prazos do Jira; prioridades do Jira permanecem como estão (I4).

| Período sugerido | Backend (Rickelme) | Prazo oficial | Frontend (Raphael) |
|------------------|--------------------|---------------|--------------------|
| 02/11 a 03/11 | DEV-01: aceite do contrato e registro no EQF-13; primeira entrega acadêmica em 03/11 | 06/11 | Ler repositório, guia e contrato; design estático |
| 03/11 a 05/11 | DEV-02 (após autorização) | 07/11 | Layout base, P10 e P01 em HTML estático |
| Após REQ-04, até 08/11 | DEV-03 | 08/11 | P02 a P06 em HTML estático |
| 08/11 a 10/11 | DEV-04 e DEV-05 | Conferir no Jira | Integrar P02 a P06 |
| 10/11 a 12/11 | DEV-06 | Conferir no Jira | Integrar P07 e P09 |
| 12/11 | DEV-07 | Conferir no Jira | Integrar P08 |
| 12/11 a 14/11 | DEV-08 (após autorização) e apoio aos testes (QA-06, EQF-26) | Conferir no Jira | Revisão responsiva e de acessibilidade |
| 14/11 a 15/11 | Correções e entrega final | 15/11 | Correções e entrega final |

## 7. Mensagens e indicadores do EQF-5

- **Mensagens:** o EQF-5 traz 15 mensagens classificadas pelo Jira como **"mensagem proposta"**, incorporadas com essa classificação no [contrato §8](contrato-tecnico-frontend-backend.md#8-mensagens). Sucesso, datas inválidas, bloqueio de código e CPF, aviso de ausência de cancelamento, indicação de atraso e avisos de P07 **não têm texto especificado** e precisam de definição antes da implementação.
- **Indicadores:** `pode_excluir`, `pode_inativar`, `pode_reativar`, `codigo_editavel`, `cpf_editavel` e `pode_devolver` são os nomes propostos pelo EQF-5. `data_atual`, `data_minima`, `data_maxima`, `disponivel`, `situacao` e os demais são propostas técnicas ([contrato §9.2](contrato-tecnico-frontend-backend.md#92-indicadores-de-contexto)).
- **Jira a alinhar depois:** texto antigo do EQF-5 em P04 (D10), P05 (D14) e P07 (D13).

## 8. Aprovação de Raphael

Antes de implementar as páginas, Raphael precisa aceitar: nomes de rotas e templates; nomes técnicos dos indicadores; confirmação de exclusão dentro de P04; classes do Bootstrap aplicadas pelo backend; local dos arquivos do Bootstrap; e o **uso de JavaScript para o resumo de P07** (D13). A lista completa está no [contrato §13](contrato-tecnico-frontend-backend.md#13-pontos-para-validação-de-rickelme-e-raphael).

## 9. Testes e dependências (propostas para DEV-02)

**Testes:** `python manage.py test` com `TestCase` do Django; banco de testes PostgreSQL (necessário para concorrência); datas relativas à data atual em `America/Recife`; nomes citando o cenário (`test_ct11_...`).

| Cenários | Requisito ou decisão | Atividade |
|----------|----------------------|-----------|
| CT01–CT08 | RF001–RF004, D10, D11 | DEV-04 |
| CT09–CT10 | RF005, D12, D14 | DEV-05 |
| CT11–CT14 | RF006–RF007, D13 | DEV-06 |
| CT15–CT16 | RF008 | DEV-07 |
| FC12 (login obrigatório) | D1, D15 | DEV-02 (estrutura da tela de login) |
| Reativação inválida com massa preparada (I3) | RF004 | DEV-04; complementar, fora dos 16 cenários; número FC a conferir no EQF-6 |

**Dependências candidatas (nenhuma instalada):** Django (série 5.2 LTS, 6.0 ou 6.1), psycopg 3, black e ruff em DEV-02; gunicorn e whitenoise em DEV-08; dj-database-url opcional.

## 10. Riscos e ordem de integração

**Riscos:**

1. **REQ-04 em andamento** mantém DEV-03 bloqueado e pode comprimir DEV-04 a DEV-08.
2. **Prazo:** sete dias entre o prazo de DEV-03 (08/11) e a entrega final (15/11).
3. **PR #1 aberto:** a `main`, e portanto esta branch, ainda trata I1–I5 como pendentes.
4. **Raphael:** consta como colaborador com permissão de escrita (verificado em 01/11/2026); falta exercitar o fluxo de branch própria e revisão de PR.
5. **Concorrência:** testes exigem PostgreSQL local ou de desenvolvimento.
6. **Mensagens indefinidas** e **texto antigo do EQF-5** podem gerar divergência na avaliação se não forem alinhados.

**Ordem de integração das branches documentais (pendência, sem alteração nesta tarefa):**

1. PR #1 (`docs/alinhamento-workspace`), de preferência com merge commit.
2. `docs/guia-integracao-raphael`, que herda os dois commits do PR #1.
3. `docs/contrato-tecnico-dev01`, baseada na `main`; antes do PR, atualizar com a `main` integrada, de forma não destrutiva.

## 11. Texto de evidência para o EQF-13

Preparado para Rickelme registrar no Jira. **Não foi registrado** e não marca a atividade como concluída.

> **DEV-01 — arquitetura e organização (proposta aguardando aceite de Rickelme e Raphael)**
>
> - **Apps:** `equipamentos` (RF001–RF004, P02–P04), `clientes` (RF005, P05–P06) e `alugueis` (RF006–RF008, P07–P09); projeto `config` com página inicial (P01) e rotas `login`/`logout` (P10). Sem app de autenticação nem perfis novos.
> - **Autenticação (D1, D15):** Django Auth nativo; `LoginRequiredMiddleware` (Django 5.1 ou superior); logout só por POST com CSRF; contas criadas pelo Django Admin, restrito a administradores; sem cadastro público nem recuperação de senha.
> - **Organização:** regras em `services.py`; templates globais em `templates/` (Raphael); Bootstrap 5.3 local em `static/`; 16 rotas e 14 templates mapeados às páginas P01–P10 do EQF-5.
> - **Dados:** aluguel aberto indicado por data real de devolução nula; restrição única parcial no PostgreSQL; código único sem diferenciar maiúsculas (D11); CPF e telefone normalizados (D12); `PROTECT` nas relações; Decimal; `America/Recife`.
> - **Decisões incorporadas:** I1–I5 e D10–D15.
> - **Documentos:** `docs/contrato-tecnico-frontend-backend.md`, `docs/modelagem-proposta.md` e `docs/plano-backend-dev01-dev03.md` (branch `docs/contrato-tecnico-dev01`, ainda local).
> - **Pendências:** aceite do contrato; textos de mensagem indefinidos; alinhamento do EQF-5 (P04, P05, P07); conclusão de REQ-04 para DEV-03.

## 12. Pendências para implementação

**DEV-02:**

1. Autorização para iniciar.
2. Série e versão exata do Django, com nova consulta às fontes oficiais.
3. Runner de testes e PostgreSQL de desenvolvimento e de testes.
4. Dependências fixadas, `.env.example` e instruções no README.
5. Verificar o login nativo e o login do Admin com `LoginRequiredMiddleware`.
6. Configuração segura de sessão e CSRF para produção (a concluir em DEV-08).
7. Versão exata do Bootstrap 5.3 e responsável pelos arquivos, com Raphael.

**DEV-03:**

1. Conclusão de REQ-04 (EQF-10).
2. Confirmar `data_devolucao_real` nula como indicador de aluguel aberto e as restrições opcionais.
3. Produzir e anexar o diagrama de dados.
4. Definir os textos de mensagem indefinidos usados pelas validações de modelo.
