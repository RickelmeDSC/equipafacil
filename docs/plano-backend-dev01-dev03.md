# Plano backend — DEV-01 a DEV-03

> **PROPOSTA — AGUARDANDO VALIDAÇÃO DE RICKELME E RAPHAEL.**
>
> Versão 0.4 — 01/11/2026, com revisão editorial em 02/11/2026 (referências de integração, sem mudança técnica). Reflete o Jira depois da atualização de 01/11/2026: D10–D15 registradas no EQF-5 e DEV-01 (EQF-13) em andamento. Planejamento apenas: **DEV-02 e DEV-03 não foram iniciados**, não existe código Django no repositório e este documento não altera nada no Jira. Os documentos do DEV-01 entram na `main` por Pull Request próprio, somente depois da revisão de Raphael.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [modelagem proposta](modelagem-proposta.md).

## 1. Retrato do Jira

Retrato de 01/11/2026, depois da atualização do Jira; não é uma consulta em tempo real.

| Atividade | Status | Responsável no Jira | Prioridade | Prazo | Registros |
|-----------|--------|---------------------|------------|-------|-----------|
| EQF-5 — épico de desenvolvimento | A Fazer | — | Medium | — | Descrição atualizada com D10–D15 em 01/11/2026 |
| EQF-13 — DEV-01 | **Em Andamento** | Rickelme, com Raphael como colaborador | Medium | 06/11/2026 | Um comentário de progresso (01/11/2026) |
| EQF-14 — DEV-02 | A Fazer | Rickelme | Medium | 07/11/2026 | Nenhum |
| EQF-15 — DEV-03 | A Fazer, **bloqueado** | Rickelme | Medium | 08/11/2026 | Nenhum |
| EQF-10 — REQ-04 | Em Andamento | Ivisson | Highest | 03/11/2026 | Sem comentários nem validação final registrada |

Nessa data, o comentário no EQF-13 registrava o progresso, sem anexo nem link para os documentos do DEV-01, que ainda não estavam publicados; o PR #1 estava aberto.

## 2. Responsáveis no Jira e responsáveis técnicos

- **Responsável no Jira:** dono da entrega da atividade. Os responsáveis atuais são preservados.
- **Responsável técnico pelo backend:** Rickelme (models, forms, services, views, URLs, migrations, testes de backend, infraestrutura).
- **Responsável técnico pelo frontend:** Raphael (templates, Bootstrap, CSS, JavaScript, responsividade).

| Atividade | Título no Jira | Responsável no Jira | Backend | Frontend |
|-----------|----------------|---------------------|---------|----------|
| DEV-01 (EQF-13) | Definir arquitetura Django e organização do projeto | Rickelme (Raphael colaborador) | Rickelme | Raphael valida o contrato |
| DEV-02 (EQF-14) | Preparar repositório, ambiente virtual, dependências e configuração inicial | Rickelme | Rickelme | — |
| DEV-03 (EQF-15) | Modelar banco de dados de equipamentos, clientes e aluguéis | Rickelme | Rickelme | — |
| DEV-04 (EQF-16) | Implementar CRUD de equipamentos | **Raphael** | Rickelme | Raphael (P02, P03, P04) |
| DEV-05 (EQF-17) | Implementar cadastro de clientes | **Raphael** | Rickelme | Raphael (P05, P06) |
| DEV-06 (EQF-18) | Implementar registro de aluguéis e devoluções | Rickelme | Rickelme | Raphael (P07, P09) |
| DEV-07 (EQF-19) | Implementar consulta do histórico de aluguéis | **Raphael** | Rickelme | Raphael (P08) |
| DEV-08 (EQF-20) | Realizar integração, revisão técnica e preparação da demonstração | Rickelme | Rickelme (inclui o deploy no Render previsto no EQF-5) | Integração e revisão conjuntas |

Em DEV-04, DEV-05 e DEV-07, os arquivos de backend serão implementados por Rickelme e os de frontend por Raphael, com **integração conjunta e revisão cruzada** por Pull Request (fluxo no [contrato, seção 10](contrato-tecnico-frontend-backend.md#10-divisão-de-arquivos)). Essa colaboração está **planejada, ainda não realizada**.

## 3. Escopo oficial e critérios de aceite

**DEV-01 (EQF-13) — em andamento:**

1. Aplicações Django definidas e justificadas.
2. Estrutura de pastas e convenções documentadas.
3. Decisões arquiteturais registradas na atividade.

Decisões técnicas da especificação: Django Auth, páginas operacionais protegidas, contas criadas administrativamente, `America/Recife`, valores com Decimal e Bootstrap no layout base.

**DEV-02 (EQF-14) — não iniciado; aguarda autorização:**

1. Repositório acessível.
2. Ambiente virtual e dependências preparados.
3. Projeto Django funcionando sem erros.
4. README com instruções.

Requisitos técnicos: Django Auth; fuso `America/Recife`; configuração inicial de templates e static; estrutura da tela de login; preparação para PostgreSQL por variáveis de ambiente; nenhuma credencial no repositório. Neon e Render ainda não estão autorizados.

**DEV-03 (EQF-15) — formalmente bloqueado por REQ-04 (EQF-10):**

1. Models `Equipamento`, `Cliente` e `Aluguel`.
2. RN001–RN004 refletidas.
3. Migrations aplicadas sem erro.
4. Diagrama do modelo anexado à atividade.

Regras: no máximo um aluguel aberto por equipamento, com restrição efetiva no PostgreSQL; preservação do histórico; sem exclusão em cascata; Decimal para dinheiro; `America/Recife`; código e CPF imutáveis após o primeiro aluguel. Detalhes na [modelagem](modelagem-proposta.md).

## 4. Decisões D10–D15

Aprovadas por Rickelme e **já registradas na descrição do EQF-5** (01/11/2026).

| Decisão | Conteúdo | Onde está nos documentos do DEV-01 |
|---------|----------|---------------------------------|
| D10 — Inativação | Todo equipamento ativo sem aluguel aberto pode ser inativado, com ou sem histórico; exclusão física só sem histórico e sem aluguel aberto; reativação exige dados válidos e nenhum aluguel aberto | Modelagem §2; contrato P04 e §9.2 |
| D11 — Código | Remove espaços das extremidades; único sem diferenciar maiúsculas; grafia preservada; reforço no PostgreSQL; imutável após o primeiro aluguel | Modelagem §2; contrato §7.1 |
| D12 — CPF e telefone | CPF: remove só pontos e hífen, recusa outros caracteres, 11 dígitos, dígitos verificadores, recusa dígitos todos iguais, único, formatado, imutável. Telefone: opcional, máscara usual, DDD, 10 ou 11 dígitos, formatado | Modelagem §3; contrato §7.2 |
| D13 — Aluguel em uma etapa | Formulário único; resumo antes de registrar; aviso de ausência de cancelamento; sem página adicional; backend recalcula e revalida | Modelagem §4; contrato §7.3 e P07 |
| D14 — Clientes | Consulta pela listagem; cadastro e edição; sem pesquisa; sem página de detalhe | Contrato P05 |
| D15 — Funcionários | Django Auth; contas pelo Django Admin; Admin restrito a administradores autorizados; sem cadastro público; sem recuperação de senha; sem perfis novos | Contrato §3; modelagem §7 |

A validação acadêmica da autenticação como requisito transversal continua pendente.

## 5. Como DEV-01 atende os critérios de aceite

| Critério | Evidência nos documentos | Situação |
|----------|-----------------|----------|
| 1. Aplicações definidas e justificadas | [Contrato §2](contrato-tecnico-frontend-backend.md#2-arquitetura-dev-01) | Proposta, aguardando aceite |
| 2. Estrutura e convenções documentadas | Contrato §2 a §10; [modelagem](modelagem-proposta.md) | Proposta, aguardando aceite |
| 3. Decisões registradas na atividade | Comentário de progresso no EQF-13 (01/11/2026); texto final na seção 11 | **Parcial**: o registro das decisões finais depende do aceite do contrato |

DEV-01 **não** deve ir para Em Revisão ou Concluído antes de o contrato estar publicado e submetido à validação de Rickelme e Raphael.

## 6. Dependências formais

1. **DEV-01** → **DEV-02** → **DEV-03** → **DEV-04** e **DEV-05** → **DEV-06** → **DEV-07** → **DEV-08**.
2. **DEV-03** também depende de **REQ-04 (EQF-10)**, em andamento: continua **formalmente bloqueado**.
3. **DEV-02** bloqueia **QA-05** (EQF-25, dados de teste).
4. **Frontend (Raphael):** design estático pode começar já; a integração de cada página depende do contrato aceito e da atividade DEV correspondente.

Nenhuma dependência foi removida e nenhuma atividade bloqueada foi iniciada.

## 7. Cronograma sugerido

Sugestão para discussão, que não altera prazos do Jira; prioridades do Jira permanecem como estão (I4).

| Período sugerido | Backend (Rickelme) | Prazo oficial | Frontend (Raphael) |
|------------------|--------------------|---------------|--------------------|
| 02/11 a 03/11 | DEV-01: aceite do contrato e registro das decisões no EQF-13; primeira entrega acadêmica em 03/11 | 06/11 | Ler repositório, guia e contrato; design estático |
| 03/11 a 05/11 | DEV-02 (após autorização) | 07/11 | Layout base, P10 e P01 em HTML estático |
| Após REQ-04, até 08/11 | DEV-03 | 08/11 | P02 a P06 em HTML estático |
| 08/11 a 10/11 | Backend de DEV-04 e DEV-05 | Conferir no Jira | Frontend de DEV-04 e DEV-05 (P02 a P06) |
| 10/11 a 12/11 | DEV-06 | Conferir no Jira | P07 e P09 |
| 12/11 | Backend de DEV-07 | Conferir no Jira | Frontend de DEV-07 (P08) |
| 12/11 a 14/11 | DEV-08 (deploy após autorização) e apoio aos testes (QA-06, EQF-26) | Conferir no Jira | Revisão responsiva e de acessibilidade |
| 14/11 a 15/11 | Correções e entrega final | 15/11 | Correções e entrega final |

## 8. Mensagens, indicadores e aceite de Raphael

- **Mensagens:** o EQF-5 traz 21 mensagens propostas, transcritas literalmente no [contrato §8](contrato-tecnico-frontend-backend.md#8-mensagens). Sem texto no Jira: mensagens de sucesso, aviso de ausência de cancelamento, indicação de atraso, credenciais inválidas e avisos de P07.
- **Indicadores:** `pode_excluir`, `pode_inativar`, `pode_reativar`, `codigo_editavel`, `cpf_editavel` e `pode_devolver` vêm do EQF-5; os demais são propostas técnicas ([contrato §9.2](contrato-tecnico-frontend-backend.md#92-indicadores-de-contexto)).
- **Aceite de Raphael:** a lista objetiva está no [contrato §13](contrato-tecnico-frontend-backend.md#13-conferência-do-contrato-com-raphael).

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
3. **Instruções anteriores ao PR #1:** enquanto o PR #1 não estiver integrado, a `main` e as branches criadas a partir dela tratam I1–I5 como pendentes e não citam D10–D15 no `CLAUDE.md` nem na rastreabilidade; valem as decisões aprovadas registradas no Jira.
4. **Divisão de trabalho:** em DEV-04, DEV-05 e DEV-07 o responsável no Jira (Raphael) depende do backend de Rickelme; atrasos no backend atrasam a entrega dele.
5. **Concorrência:** testes exigem PostgreSQL local ou de desenvolvimento.
6. **Mensagens sem texto** (sucesso, aviso de cancelamento, atraso) precisam ser definidas antes da implementação.

**Ordem recomendada de integração das branches documentais** (merges feitos por Rickelme na interface do GitHub, com "Create a merge commit"; squash ou rebase mudariam os commits do PR #1 e os duplicariam no PR do guia):

1. PR #1 (`docs/alinhamento-workspace`): instruções, permissões do Claude Code e rastreabilidade com I1–I5 e D10–D15.
2. `docs/guia-integracao-raphael`: herda os dois primeiros commits do PR #1; o PR do guia, aberto depois do merge do PR #1, mostra só os commits do guia.
3. `docs/contrato-tecnico-dev01`: criada a partir da `main` inicial e sem arquivos em comum com as anteriores, por isso não precisa ser atualizada antes do PR. O PR pode ser aberto como rascunho para a revisão de Raphael; o merge vem por último, depois do aceite (contrato, seção 14).

## 11. Texto final para o EQF-13

Um comentário de **progresso** já foi registrado no EQF-13 em 01/11/2026. O texto abaixo, com as **decisões finais**, fica para depois do aceite do contrato; ainda não foi registrado.

> **DEV-01 — arquitetura e organização (decisões aceitas por Rickelme e Raphael em [data do aceite])**
>
> - **Apps:** `equipamentos` (RF001–RF004, P02–P04), `clientes` (RF005, P05–P06) e `alugueis` (RF006–RF008, P07–P09); projeto `config` com página inicial (P01) e rotas `login`/`logout` (P10). Sem app de autenticação nem perfis novos.
> - **Autenticação (D1, D15):** Django Auth nativo; `LoginRequiredMiddleware` (Django 5.1 ou superior); logout só por POST com CSRF; contas criadas pelo Django Admin, restrito a administradores; sem cadastro público nem recuperação de senha.
> - **Organização:** regras em `services.py`; templates globais em `templates/` (Raphael); Bootstrap 5.3 local em `static/`; 16 rotas e 14 templates mapeados às páginas P01–P10 do EQF-5; revisão cruzada por Pull Request.
> - **Dados:** aluguel aberto indicado por data real de devolução nula; restrição única parcial no PostgreSQL; código único sem diferenciar maiúsculas (D11); CPF e telefone normalizados (D12); `PROTECT` nas relações; Decimal; `America/Recife`.
> - **Decisões incorporadas:** I1–I5 e D10–D15.
> - **Documentos:** `docs/contrato-tecnico-frontend-backend.md`, `docs/modelagem-proposta.md` e `docs/plano-backend-dev01-dev03.md` [link após a publicação].

## 12. Pendências

Nenhuma das pendências abaixo está resolvida.

**Contrato:**

1. Aceite do contrato por Rickelme e Raphael.
2. Aprovação da prévia em JavaScript de P07 (D13).
3. Textos das mensagens de sucesso, do aviso de ausência de cancelamento e da indicação de atraso.
4. Configuração do Bootstrap 5.3 (versão exata, local dos arquivos e responsável).

**Documentação acadêmica e Jira:**

1. Documento de Requisitos v1.1: validação final da equipe de Requisitos (Rafael Ferreira e Ivisson) ainda pendente.
2. A equipe de Requisitos avaliar se D10, D11 e D12 exigem atualização do DOCX.
3. EQF-5: o painel de estado ainda diz que nenhum "repositório" foi iniciado, embora o repositório exista no GitHub (correção a combinar).
4. Validação acadêmica da autenticação como requisito transversal, com o professor.

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
4. Definir os textos ainda sem mensagem proposta que as validações de modelo usarem.
