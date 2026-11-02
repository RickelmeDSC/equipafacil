# Modelagem proposta — EquipaFácil

> **PROPOSTA — AGUARDANDO VALIDAÇÃO DE RICKELME E RAPHAEL.**
>
> Versão 0.3 — 01/11/2026. Consolida o Documento de Requisitos v1.1, as decisões I1–I5 e D10–D15 e o escopo de DEV-03 (EQF-15) registrado no Jira. **Nada aqui está implementado**: não existe projeto Django, model ou migration no repositório. Models, migrations e diagrama de dados são entregas de DEV-03, que segue **bloqueado** pela REQ-04 (EQF-10).
>
> **Fontes:** Documento de Requisitos v1.1 (RF001–RF008, RN001–RN004, D1–D9, N2–N6, TZ, I1–I5), decisões D10–D15 aprovadas por Rickelme, auditoria do Jira de 01/11/2026, [`rastreabilidade.md`](rastreabilidade.md), [`arquitetura-planejada.md`](arquitetura-planejada.md) e o [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md). Nesta branch, baseada na `main`, os resumos do repositório ainda tratam I1–I5 como pendentes; a atualização deles está no PR #1.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

**Legenda:** **Aprovado** (v1.1, I1–I5, D10–D15); **Jira (texto antigo)** (texto superado por decisão posterior); **Proposta técnica** (sugestão de Rickelme); **Pendente de validação** (depende de aceite ou decisão adicional).

## 1. Princípios

| Princípio | Como a modelagem atende | Origem |
|-----------|-------------------------|--------|
| Disponibilidade derivada | Sem campo `disponivel`; calculada como ativo e sem aluguel aberto | Aprovado (RN001 c) |
| Aluguel aberto | Indicado por `data_devolucao_real` nula. "Aberto" equivale a "ativo" na terminologia do v1.1. Sem coluna de status | Proposta técnica |
| Um aluguel aberto por equipamento | Restrição única parcial sobre a coluna persistida + bloqueio de linha na transação | Aprovado (RN001 a, b) |
| Situação apenas de apresentação | Ativo, Atrasado, Encerrado e Encerrado com atraso são calculados; nenhuma restrição de banco depende deles | Aprovado (RN004 g) |
| Valores exatos | `DecimalField` com duas casas; nunca `float` | Aprovado (RN004 e, D9) |
| Datas de negócio | `DateField` no calendário `America/Recife` | Aprovado (RN004 a, TZ) |
| Valor contratado congelado | Diária, diárias e valor copiados para o aluguel no registro | Aprovado (RF006, D3) |
| Histórico preservado | Chaves estrangeiras com `PROTECT`; sem exclusão em cascata; aluguéis não são editados nem excluídos | Aprovado (RN003, I2) |
| Validação no backend | Restrições no banco + formulários e serviços; a tela nunca é a única barreira | Aprovado (RN002 e) |

Convenções propostas: chave primária `BigAutoField`, nomes de campos em português e restrições nomeadas. As restrições usam `CheckConstraint(condition=...)` e `UniqueConstraint` com expressões, disponíveis nas séries candidatas do Django (5.2 LTS, 6.0 e 6.1).

## 2. Equipamento

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `codigo` | `CharField(max_length=30)` | Obrigatório; espaços das extremidades removidos; único **sem diferenciar maiúsculas e minúsculas**; grafia cadastrada preservada para exibição; imutável após o primeiro aluguel | Aprovado (RF001, RF003, N3, D11); tamanho é proposta técnica |
| `nome` | `CharField(max_length=120)` | Obrigatório | Aprovado (RF001); tamanho é proposta técnica |
| `categoria` | `CharField(max_length=30, choices=Categoria.choices)` | Uma das cinco categorias fixas | Aprovado (RF001, D8) |
| `valor_diaria` | `DecimalField(max_digits=10, decimal_places=2)` | Maior que R$ 0,00, até duas casas | Aprovado (RF001, D9); `max_digits` é proposta técnica |
| `descricao` | `TextField(blank=True)` | Opcional | Aprovado (RF001) |
| `ativo` | `BooleanField(default=True)` | Criado ativo; muda só por inativação ou reativação | Aprovado (RF001, RF004) |

**Categorias (`TextChoices`):** Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil e Outros. Valores internos sugeridos: `ferramentas`, `audiovisuais`, `informatica`, `construcao_civil` e `outros`.

**Restrições no banco:**

- `equipamento_codigo_unico_ci`: `UniqueConstraint(Lower("codigo"))` — unicidade sem diferenciar maiúsculas, garantida pelo PostgreSQL (D11). Substitui o `unique=True` simples.
- `equipamento_diaria_positiva`: `valor_diaria > 0`.
- Opcional (proposta técnica): `equipamento_codigo_sem_espacos_extremos`, com `codigo` igual a `Trim("codigo")`, como reforço da normalização.

**Tratamento de colisões de código (D11, proposta técnica):**

1. O formulário remove os espaços das extremidades e recusa código vazio.
2. Antes de gravar, o serviço verifica se já existe código igual comparando com a mesma expressão do banco (`Lower`), excluindo o próprio registro na edição.
3. Se dois cadastros simultâneos passarem pela verificação, a restrição do banco recusa o segundo; o `IntegrityError` vira o erro de campo "Já existe um equipamento com este código." (mensagem proposta do EQF-5).
4. Como o banco ainda não existe, não há colisões antigas a migrar.

**Atributos calculados (backend, nunca persistidos):**

| Atributo | Regra | Origem |
|----------|-------|--------|
| `disponivel` | `ativo` e nenhum aluguel aberto | Aprovado (RN001 c) |
| `tem_historico` | Existe pelo menos um aluguel do equipamento | Aprovado (RN003) |
| `tem_aluguel_ativo` | Existe aluguel aberto | Aprovado (RN003 c) |
| `codigo_editavel` | Não `tem_historico` | Aprovado (RF003, N3) |
| `pode_excluir` | Não `tem_historico` (o que implica nenhum aluguel aberto) | Aprovado (RF004, RN003 a, D10) |
| `pode_inativar` | `ativo` e não `tem_aluguel_ativo`, **com ou sem histórico** | Aprovado (D10) |
| `pode_reativar` | Não `ativo`, dados cadastrais válidos e não `tem_aluguel_ativo` | Aprovado (RN003 e, N4, D10) |

"Dados cadastrais válidos" significa revalidar o registro com as regras atuais (RN002, D11) antes de reativar. Pela interface não se cria esse estado inválido; o teste usa massa preparada e é complementar (I3).

## 3. Cliente

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `nome_completo` | `CharField(max_length=150)` | Obrigatório | Aprovado (RF005); tamanho é proposta técnica |
| `cpf` | `CharField(max_length=11)` | Entrada com ou sem pontuação; remove **apenas** pontos e hífen; recusa qualquer outro caractere; exatamente 11 dígitos; dígitos verificadores válidos; **recusa sequência com todos os dígitos iguais**; único; exibido formatado; imutável após o primeiro aluguel | Aprovado (RF005, RN002, N3, I5, D12) |
| `telefone` | `CharField(max_length=11, blank=True)` | Opcional; aceita a máscara brasileira comum; recusa outros caracteres; DDD obrigatório; persiste só 10 ou 11 dígitos; exibido formatado | Aprovado (RF005, N5, D12) |
| `email` | `EmailField(blank=True)` | Opcional; formato validado quando informado | Aprovado (RF005, RN002) |

**Máscara do telefone (proposta técnica, interpretação de D12):** caracteres aceitos além dos dígitos: parênteses, espaço e hífen, como em `(81) 99999-9999` ou `(81) 3333-4444`. Qualquer outro caractere, inclusive `+`, é recusado. Depois da remoção, restam 10 ou 11 dígitos, sendo os dois primeiros o DDD.

Clientes **não são excluídos** nem inativados (RF005, RN003 f, D7, D14).

**Restrições no banco:**

- `cliente_cpf_unico`: unicidade de `cpf`.
- `cliente_cpf_onze_digitos`: `cpf` corresponde a `^[0-9]{11}$`.
- Opcionais (proposta técnica): `cliente_cpf_nao_repetido` (recusa os 11 dígitos iguais) e `cliente_telefone_digitos` (vazio ou com 10 a 11 dígitos).

Dígitos verificadores e caracteres aceitos ficam no formulário/serviço; as restrições de banco são reforço.

**Atributos calculados:** `cpf_formatado` (`000.000.000-00`), `telefone_formatado` e `cpf_editavel` (nenhum aluguel associado).

## 4. Aluguel

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `equipamento` | `ForeignKey(Equipamento, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `cliente` | `ForeignKey(Cliente, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `data_retirada` | `DateField` | Não anterior à data atual no registro; retirada futura permitida | Aprovado (RF006, RN004 b, D2/D6, I1) |
| `data_devolucao_prevista` | `DateField` | Igual ou posterior à retirada; mínimo de 1 diária | Aprovado (RF006, RN004 c) |
| `data_devolucao_real` | `DateField(null=True, blank=True)` | Nula enquanto aberto; preenchida uma única vez, entre a retirada e a data atual | Aprovado (RF007, RN004 f, N2, I2) |
| `valor_diaria_contratada` | `DecimalField(max_digits=10, decimal_places=2)` | Cópia da diária do equipamento no registro | Aprovado (RF006, D3) |
| `quantidade_diarias` | `PositiveIntegerField` | `(prevista − retirada) + 1`, calculada no registro | Aprovado (RN004 d, D3) |
| `valor_contratado` | `DecimalField(max_digits=12, decimal_places=2)` | `quantidade_diarias × valor_diaria_contratada`, congelado | Aprovado (RN004 e, CT11) |

Não há campo de status, multa, cancelamento, pagamento ou funcionário responsável.

**Registro em uma etapa (D13):** um único envio do formulário. Uma prévia de diárias e valor pode aparecer na tela (proposta técnica, depende do aceite de Raphael), mas **nunca é usada**: dentro da transação, o serviço relê a diária do equipamento, recalcula `quantidade_diarias` e `valor_contratado`, revalida datas e disponibilidade e só então grava.

**Restrições no banco (todas sobre colunas persistidas):**

- `aluguel_um_aberto_por_equipamento`: `UniqueConstraint(fields=["equipamento"], condition=Q(data_devolucao_real__isnull=True))`. Garante no PostgreSQL no máximo um aluguel aberto por equipamento, inclusive os de retirada futura, que bloqueiam o equipamento desde o registro (I1).
- `aluguel_prevista_apos_retirada`: `data_devolucao_prevista >= data_retirada`.
- `aluguel_devolucao_apos_retirada`: `data_devolucao_real` nula ou `>= data_retirada`.
- `aluguel_valores_positivos`: `valor_diaria_contratada > 0`, `quantidade_diarias >= 1` e `valor_contratado > 0`.

Regras que dependem do dia corrente (retirada não anterior à data atual; devolução real não posterior à data atual) **não** podem ser restrições de banco: ficam no serviço, que recebe `hoje` calculado em `America/Recife`.

## 5. Estados derivados (apresentação)

`situacao` (rótulo) e `situacao_codigo` (estilo) são propostas técnicas de nome para o conceito exigido pelo EQF-5, calculados com `hoje = timezone.localdate()` em `America/Recife`. O banco não os armazena.

| `situacao` | `situacao_codigo` | Condição (RN004 g) |
|------------|-------------------|--------------------|
| Ativo | `ativo` | Aberto e devolução prevista não anterior à data atual |
| Atrasado | `atrasado` | Aberto e devolução prevista anterior à data atual |
| Encerrado | `encerrado` | Devolvido com data real não posterior à prevista |
| Encerrado com atraso | `encerrado_com_atraso` | Devolvido com data real posterior à prevista |

Aluguel com retirada futura aparece como **Ativo** (v1.1, limitações). **`pode_devolver`:** aberto e `hoje` igual ou posterior à retirada (I1).

## 6. Revisão de compatibilidade

| Ponto | Resultado |
|-------|-----------|
| Aluguel aberto × data real de devolução | Mesmo conceito: aberto = `data_devolucao_real` nula |
| Situação × restrição única parcial | A restrição usa a coluna persistida; a situação não entra no banco |
| Restrição única × bloqueio concorrente | Complementares: o bloqueio dá mensagem amigável; a restrição é a última barreira |
| Preservação do histórico | `PROTECT` em `equipamento` e `cliente`; sem cascata; sem edição ou exclusão de aluguel |
| Unicidade de código (D11) e CPF (D12) | Restrições únicas no PostgreSQL sobre os valores normalizados |
| Decimal e diárias inclusivas | `DecimalField`; mínimo de 1 diária garantido por restrição |
| Retirada futura e ausência de cancelamento | Permitida; o aluguel fica aberto desde o registro; não há campo nem rota de cancelamento |
| Registro em uma etapa (D13) | Valores sempre recalculados no serviço, nunca recebidos da tela |

## 7. Imutabilidade, histórico e administração

| Regra | Proteção proposta |
|-------|-------------------|
| Código imutável após o primeiro aluguel (RF003, N3, D11) | Campo somente leitura no formulário (o Django ignora o valor enviado) e checagem no serviço na transação; inclui mudança só de maiúsculas |
| CPF imutável após o primeiro aluguel (RF005, N3, D12) | Mesma abordagem |
| Nova diária não afeta aluguéis existentes (RF003) | Valores copiados para o aluguel |
| Sem edição de aluguel ou devolução (I2) | Nenhuma view de edição; a devolução só grava se `data_devolucao_real` estiver nula |
| Equipamento com histórico não é excluído (RN003 b) | `PROTECT` + checagem prévia no serviço |
| Cliente nunca é excluído (RN003 f, D14) | Nenhuma view de exclusão + `PROTECT` |
| Administração de funcionários (D15) | O Django Admin registra só os modelos de usuário do Django Auth. `Equipamento`, `Cliente` e `Aluguel` **não** são registrados no Admin, para não contornar as regras de serviço |

## 8. Concorrência (PostgreSQL)

Todas as operações que alteram estado rodam em `transaction.atomic()` nos serviços.

| Cenário | Risco | Proteção proposta |
|---------|-------|-------------------|
| Dois aluguéis simultâneos do mesmo equipamento | Dois aluguéis abertos | `select_for_update()` na linha do equipamento antes de validar; restrição única parcial como última barreira; `IntegrityError` vira "Este equipamento não está disponível para aluguel." (CT12) |
| Parâmetro HTTP manipulado (RN001 b) | Alugar equipamento fora da lista | O serviço revalida disponibilidade a partir do banco |
| Aluguel × inativação ou exclusão | Inativar ou excluir durante um aluguel | As operações bloqueiam a mesma linha de `Equipamento` e revalidam na transação; `PROTECT` impede exclusão com aluguel |
| Duas devoluções do mesmo aluguel | Devolução dupla (CT14) | `filter(pk=..., data_devolucao_real__isnull=True).update(...)`; zero linhas afetadas significa "Este aluguel já foi encerrado." |
| Edição de código ou CPF × primeiro aluguel | Alterar o identificador no instante do primeiro aluguel | O registro de aluguel bloqueia equipamento e cliente, sempre nessa ordem; a edição bloqueia a mesma linha e revalida "sem histórico" |
| Cadastros simultâneos com mesmo código (sem diferenciar maiúsculas) ou CPF | Duplicidade | Restrições únicas; `IntegrityError` vira erro de campo |

O isolamento padrão do PostgreSQL (READ COMMITTED) é suficiente com bloqueio de linha e restrições. O SQLite ignora `select_for_update()`: **os testes de concorrência precisam de PostgreSQL**.

## 9. Índices e configurações

- Índices das restrições únicas (`Lower(codigo)`, `cpf`, aluguel aberto por equipamento) e das chaves estrangeiras.
- Pesquisa de equipamentos por nome ou código com `icontains`, sem índice adicional no volume de um projeto acadêmico. Não há pesquisa de clientes (D14).
- Ordenação proposta do histórico: `-data_retirada`, `-id`.
- `TIME_ZONE = "America/Recife"`, `USE_TZ = True`, `LANGUAGE_CODE = "pt-br"`, `USE_THOUSAND_SEPARATOR = True`; "data atual" sempre com `timezone.localdate()`.

## 10. Pendências

1. Confirmar `data_devolucao_real` nula como indicador persistido de aluguel aberto (proposta técnica).
2. Tamanhos máximos de `codigo`, `nome` e `nome_completo` (não definidos no v1.1).
3. Adotar ou não as restrições opcionais de reforço (código sem espaços, CPF não repetido, dígitos do telefone).
4. Diagrama de dados oficial, a anexar ao EQF-15 em DEV-03.
5. DEV-03 só começa depois da conclusão de REQ-04 (EQF-10).
