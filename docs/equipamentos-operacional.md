# Gestão operacional de equipamentos — DEV-04 (EQF-16)

> **Situação:** integrado à `main` em 02/11/2026 pelo PR #6 (merge commit `0c24778`; marco da `main` integrada: `85b4d1a`). Desenvolvido na branch `feat/backend-eqf-16-equipamentos`, sobre DEV-03 e DEV-02. Rotas, nomes de template e variáveis seguem o contrato técnico **proposto** no PR #2 (v0.4), ainda em rascunho e sem aceite de Raphael. As páginas HTML são **provisórias**.

Escopo: RF001 (cadastro), RF002 (consulta e pesquisa), RF003 (edição), RF004 (exclusão e inativação), com RN002, RN003, D10, D11 e I3. Fora do escopo: clientes (DEV-05), registro de aluguel e devolução pela interface (DEV-06), layout definitivo e Bootstrap (frontend).

## Fluxos

| Página | Rota (nome) | Método | Comportamento |
|--------|-------------|--------|---------------|
| P02 — lista e pesquisa | `/equipamentos/` (`equipamentos:lista`) | GET | Lista ativos e inativos, ordenados por nome e código. `?q=` pesquisa só por código ou nome, sem diferenciar maiúsculas, ignorando espaços nas extremidades. Sem resultado: "Nenhum registro encontrado." |
| P03 — cadastro | `/equipamentos/novo/` (`equipamentos:criar`) | GET, POST | Cria o equipamento **ativo**. Sucesso → P02 (PRG); erro → mesma página com os erros por campo |
| P03 — edição | `/equipamentos/<pk>/editar/` (`equipamentos:editar`) | GET, POST | Altera código, nome, categoria, descrição e diária. Com histórico, o código fica somente leitura |
| P04 — ações | `/equipamentos/<pk>/acoes/` (`equipamentos:acoes`) | GET | Mostra o que pode ser feito e o motivo de cada bloqueio |
| Exclusão | `/equipamentos/<pk>/excluir/` (`equipamentos:excluir`) | POST | Exige `confirmacao=sim` no POST. Sucesso → P02; recusa → P04 com a mensagem |
| Inativação | `/equipamentos/<pk>/inativar/` (`equipamentos:inativar`) | POST | Sucesso → P02; recusa → P04 com a mensagem |
| Reativação | `/equipamentos/<pk>/reativar/` (`equipamentos:reativar`) | POST | Sucesso → P02; recusa → P04 com a mensagem |

Todas as rotas exigem login (`LoginRequiredMiddleware`). GET nunca altera dados; toda alteração é POST com CSRF. Outros métodos recebem 405; `pk` inexistente, 404.

## Formulário e views

- `equipamentos/forms.py` — `EquipamentoForm` com **apenas** `codigo`, `nome`, `categoria`, `descricao` e `valor_diaria`. `ativo`, `id` ou qualquer outro campo enviado são ignorados. A diária aceita vírgula decimal (`35,50`). Erros usam os textos do EQF-5 (`config/mensagens.py`). Com `codigo_editavel=False`, o campo `codigo` fica `disabled`: o Django usa o valor gravado e descarta o enviado.
- `equipamentos/views.py` — funções simples, sem regra de negócio: validam a forma dos dados, chamam o serviço e convertem `ValidationError` em erro de formulário (P03) ou em `messages.error` (P04).

## Serviços (`equipamentos/services.py`)

| Função | Regra |
|--------|-------|
| `cadastrar_equipamento(dados)` | RF001/RN002/D11: grava só os campos editáveis, ativo. `IntegrityError` do índice `equipamento_codigo_unico_ci` (corrida entre dois cadastros) vira erro de campo "Já existe um equipamento com este código.", nunca erro 500 |
| `editar_equipamento(pk, dados)` | RF003/D11: bloqueia a linha, revalida o histórico e recusa troca de código (inclusive só de maiúsculas) se já houver aluguel; demais campos seguem editáveis. Diária nova não altera aluguéis registrados |
| `excluir_equipamento(pk)` | RF004/RN003: bloqueia a linha; exclusão física só sem histórico e sem aluguel aberto |
| `inativar_equipamento(pk)` | D10: bloqueia a linha; todo equipamento ativo sem aluguel aberto pode ser inativado, com ou sem histórico. Já inativo: nada muda |
| `reativar_equipamento(pk)` | RN003/I3: bloqueia a linha; reativa só com dados cadastrais válidos pelas regras atuais e sem aluguel aberto. Já ativo: nada muda. O histórico não é alterado |
| `avaliar_acoes(equipamento)` | Indicadores `pode_excluir`, `pode_inativar`, `pode_reativar` e motivos, **só para exibição** |

## Concorrência

Todos os serviços que alteram um equipamento existente fazem `select_for_update()` na linha do equipamento antes de revalidar as regras — o mesmo primeiro bloqueio de `registrar_aluguel` (equipamento, depois cliente). Assim, edição, exclusão, inativação e o registro de aluguel do mesmo equipamento são serializados no PostgreSQL, sem risco de impasse por ordem de bloqueio. Quem bloqueia por último decide com o estado já gravado pelo primeiro.

| Corrida (primeira → segunda) | Resultado |
|------------------------------|-----------|
| Troca de código → primeiro aluguel | Ambos gravam; o aluguel nasce com o código novo |
| Primeiro aluguel → troca de código | Troca recusada: "O código não pode ser alterado porque o equipamento já possui aluguel registrado." |
| Exclusão → primeiro aluguel | Aluguel recusado: "Este equipamento não está disponível para aluguel." (`registrar_aluguel` passou a tratar o equipamento que sumiu durante a espera) |
| Primeiro aluguel → exclusão | Exclusão recusada: "Não é possível excluir ou inativar: equipamento com aluguel ativo." |
| Inativação → primeiro aluguel | Aluguel recusado (equipamento inativo) |
| Primeiro aluguel → inativação | Inativação recusada |

`equipamentos/tests/test_concorrencia.py` executa as seis corridas com threads no PostgreSQL e confirma que a segunda operação fica **parada no bloqueio** enquanto a primeira transação está aberta. Verificação de sensibilidade feita durante o desenvolvimento: sem o `select_for_update()` dos serviços de equipamento, três dos seis testes falham (código trocado depois do aluguel, inativação com aluguel aberto e `IntegrityError` na exclusão). No SQLite os testes são pulados (o bloqueio não tem efeito ali).

## Disponibilidade

Continua derivada (ativo e sem aluguel aberto, inclusive de retirada futura — RN001, I1); não há campo persistido. A lista usa `Equipamento.objects.com_situacao()`, que anota `possui_historico` e `possui_aluguel_aberto` na própria consulta: as propriedades `tem_historico`, `tem_aluguel_aberto`, `disponivel` e `codigo_editavel` usam essas anotações quando presentes. Um teste confirma que a quantidade de consultas da lista não cresce com o número de equipamentos.

## Exclusão, inativação e reativação

| Situação do equipamento | Excluir | Inativar | Reativar |
|-------------------------|---------|----------|----------|
| Ativo, sem histórico | Sim | Sim | — |
| Ativo, com histórico encerrado | Não ("…com histórico de locação. Utilize a inativação.") | Sim (D10) | — |
| Ativo, com aluguel aberto (inclusive retirada futura) | Não ("…com aluguel ativo.") | Não ("…com aluguel ativo.") | — |
| Inativo, dados válidos, sem aluguel aberto | Só se não tiver histórico | — (repetir não muda nada) | Sim |
| Inativo, dados inconsistentes (I3) | Só se não tiver histórico | — | Não ("Não é possível reativar: corrija os dados cadastrais ou encerre o aluguel ativo.") |

Os indicadores da tela não autorizam nada: um POST montado à mão para uma ação bloqueada é recusado pelo serviço (testado).

## Testes

| Arquivo | Testes | Cobertura |
|---------|--------|-----------|
| `equipamentos/tests/test_servicos.py` | 19 | Serviços: cadastro, corrida de código duplicado, edição com e sem histórico, exclusão, inativação, reativação, `avaliar_acoes` |
| `equipamentos/tests/test_views.py` | 36 | Cadastro (vírgula decimal, obrigatórios, duplicado sem diferenciar maiúsculas, categoria e diária inválidas, campos inesperados, `IntegrityError` sem erro 500), consulta (vazia, ativos e inativos, código, nome, descrição não pesquisada, sem resultado, disponibilidade, consultas por linha), edição, P04, exclusão, inativação e reativação, segurança (login, CSRF, métodos, 404, POST manipulado) |
| `equipamentos/tests/test_cenarios_ct.py` | 8 | CT01–CT08 automatizados (abaixo) |
| `equipamentos/tests/test_concorrencia.py` | 6 | Corridas com o primeiro aluguel (só PostgreSQL) |

Cenários **automatizados** (não houve execução manual): CT01 cadastro válido ativo e disponível; CT02 código existente recusado; CT03 pesquisa por código com disponibilidade calculada; CT04 termo inexistente com mensagem; CT05 nova diária sem alterar o valor contratado; CT06 diária zero recusada; CT07 exclusão sem histórico com confirmação; CT08 exclusão com histórico bloqueada e inativação disponível (D10). A validação acadêmica dos cenários continua com a equipe de Testes.

## Divergências e pontos a combinar com o frontend

1. **Mensagens de sucesso:** o EQF-5 não define texto ("Indefinida"); nenhuma mensagem de sucesso é enviada. O sucesso aparece pelo redirecionamento para P02.
2. **Confirmação de exclusão:** campo `confirmacao` com valor `sim` (escolha técnica provisória). Sem ele, a exclusão não acontece e P04 mostra "Confirme a exclusão para continuar." — texto interno provisório, sem equivalente no EQF-5. Na página provisória a confirmação é uma caixa de seleção; o frontend pode trocá-la por um modal, desde que envie o mesmo campo.
3. **Nomes:** o contexto de P04 usa `tem_aluguel_ativo` (nome do contrato); no modelo, a propriedade equivalente é `tem_aluguel_aberto`. Na lista, cada item traz `acoes` com os mesmos indicadores, mas `pode_reativar` não revalida o cadastro ali (só P04 e o serviço revalidam).
4. **Lista:** ordem por nome e código; sem paginação nem filtro por categoria ou situação (não previstos).
5. **Rotas e templates:** `equipamentos/lista.html`, `equipamentos/formulario.html` e `equipamentos/acoes.html` são provisórios, sem Bootstrap. A troca pelo frontend deve manter os nomes de rota, os campos do formulário, `{% csrf_token %}` nos POST e o escape automático.

## Pendências

1. Aceite do contrato (PR #2) por Raphael, principalmente rotas, variáveis e o campo de confirmação.
2. Definição dos textos de sucesso e da confirmação de exclusão no EQF-5.
3. Integração das bases DEV-02 e DEV-03: concluída (PRs #4 e #5).
4. DEV-05 (clientes, inclusive a corrida da troca de CPF com o primeiro aluguel) e DEV-06 (registro de aluguel e devolução pela interface): implementados e integrados (PRs #7 e #8).
