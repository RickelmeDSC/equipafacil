# Modelagem proposta — EquipaFácil

> **RASCUNHO PROVISÓRIO — PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.1 — 01/11/2026. **Nada aqui está implementado**: não existe projeto Django, model ou migration no repositório.
>
> **Limitação:** a auditoria do Jira (Tarefa 08A-WEB) não foi concluída. Os critérios oficiais de DEV-01 (EQF-13), DEV-02 (EQF-14) e DEV-03 (EQF-15) não foram conferidos, e o Documento de Requisitos v1.1 não foi consultado diretamente. Itens marcados **[verificar]** dependem dessa conferência.
>
> **Fontes:** [`rastreabilidade.md`](rastreabilidade.md) e [`arquitetura-planejada.md`](arquitetura-planejada.md) (resumos da especificação técnica v3), o [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md) e as decisões I1–I5 aprovadas por Rickelme em 01/11/2026. Nesta branch, baseada na `main`, os resumos ainda tratam I1–I5 como pendentes; a atualização deles está no PR #1.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

## 1. Princípios

| Princípio | Como a modelagem atende | Origem |
|-----------|-------------------------|--------|
| Disponibilidade derivada | Não há campo `disponivel`; ela é calculada (ativo e sem aluguel ativo) | RN001 |
| Um aluguel ativo por equipamento | Restrição única parcial no banco + bloqueio de linha na transação | RN001 |
| Valores exatos | `DecimalField` com duas casas; nunca `float` | RN004 |
| Datas de negócio | `DateField` interpretado no calendário `America/Recife` | RN004, TZ |
| Valor contratado congelado | Diária, quantidade de diárias e valor contratado copiados para o aluguel no registro | RF003, RF006 |
| Histórico preservado | Chaves estrangeiras com `PROTECT`; aluguéis nunca são editados nem excluídos | RN003, I2 |
| Sem status manual de aluguel | Situação calculada a partir das datas | RF008 |
| Validação no backend | Restrições no banco + validação em formulários e serviços; a tela nunca é a única barreira | RN002 |

Convenções propostas: chave primária `BigAutoField` (padrão do Django), nomes de campos em português, restrições nomeadas. As restrições usam o parâmetro `condition=` de `CheckConstraint`, disponível em todas as séries do Django compatíveis com Python 3.13 listadas na arquitetura planejada.

## 2. Equipamento

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `nome` | `CharField(max_length=120)` | Obrigatório | Obrigatoriedade aprovada (RF001); tamanho é proposta |
| `codigo` | `CharField(max_length=30, unique=True)` | Obrigatório e único; imutável após o primeiro aluguel | Aprovado (RF001, RF003); tamanho e normalização são proposta |
| `categoria` | `CharField(max_length=30, choices=Categoria.choices)` | Uma das cinco categorias fixas | Aprovado (RF001) |
| `descricao` | `TextField(blank=True)` | Opcional | Aprovado (RF001) |
| `valor_diaria` | `DecimalField(max_digits=10, decimal_places=2)` | Maior que R$ 0,00 | Aprovado (RF001); `max_digits` é proposta |
| `ativo` | `BooleanField(default=True)` | Criado ativo; muda só por inativação ou reativação | Aprovado (RF001, RF004) |

**Categorias (`TextChoices`):** Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil e Outros. Os rótulos são exatamente esses; os valores internos sugeridos são `ferramentas`, `audiovisuais`, `informatica`, `construcao_civil` e `outros`.

**Restrições no banco:**

- `equipamento_codigo_unico`: unicidade de `codigo`.
- `equipamento_diaria_positiva`: `valor_diaria > 0`.

**Atributos calculados (backend):**

| Atributo | Regra |
|----------|-------|
| `disponivel` | `ativo` e nenhum aluguel com `data_devolucao_real` vazia |
| `tem_historico` | Existe pelo menos um aluguel do equipamento |
| `tem_aluguel_ativo` | Existe aluguel com `data_devolucao_real` vazia |
| `codigo_editavel` | Não `tem_historico` |
| `pode_excluir` | Não `tem_historico` |
| `pode_inativar` | `ativo` e não `tem_aluguel_ativo` — **[verificar]** se equipamento sem histórico também pode ser inativado ou se, nesse caso, só a exclusão é oferecida (RF004 cita "inativação com histórico") |
| `pode_reativar` | Não `ativo` — **[verificar]** demais condições de reativação inválida (I3) |

**Decisões pendentes:** normalização do código (remover espaços? diferenciar maiúsculas de minúsculas?). Se a unicidade tiver de ignorar maiúsculas, a restrição passa a ser sobre `Lower("codigo")`.

## 3. Cliente

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `nome_completo` | `CharField(max_length=150)` | Obrigatório | Aprovado (RF005); tamanho e critério de "completo" **[verificar]** |
| `cpf` | `CharField(max_length=11, unique=True)` | Exatamente 11 dígitos armazenados; entrada com ou sem máscara; dígitos verificadores; único; imutável após o primeiro aluguel | Aprovado (RF005, I5) |
| `telefone` | `CharField(max_length=11, blank=True)` | Opcional; só dígitos; 10 ou 11 dígitos com DDD | Aprovado (RF005) |
| `email` | `EmailField(blank=True)` | Opcional; formato validado | Aprovado (RF005) |

Clientes **não são excluídos** nem inativados: não há campo `ativo` e não haverá view de exclusão (RF005).

**Restrições no banco:**

- `cliente_cpf_unico`: unicidade de `cpf`.
- `cliente_cpf_onze_digitos`: `cpf` corresponde a `^[0-9]{11}$`.
- `cliente_telefone_digitos` (opcional): `telefone` vazio ou com 10 a 11 dígitos.

A validação dos dígitos verificadores fica no formulário/serviço, porque não é uma checagem simples de banco. Rejeitar CPFs com todos os dígitos iguais é prática comum — **[verificar]** se o Documento v1.1 exige.

**Atributos calculados:** `cpf_formatado` (`000.000.000-00`), `telefone_formatado` e `cpf_editavel` (nenhum aluguel associado).

## 4. Aluguel

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `equipamento` | `ForeignKey(Equipamento, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `cliente` | `ForeignKey(Cliente, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `data_retirada` | `DateField` | Hoje ou no futuro no registro, no calendário `America/Recife` | Aprovado (RN004, I1) |
| `data_devolucao_prevista` | `DateField` | Não anterior à retirada | Derivado da fórmula de diárias (mínimo de 1) — **[verificar]** |
| `data_devolucao_real` | `DateField(null=True, blank=True)` | Vazia enquanto ativo; preenchida uma única vez, entre a retirada e a data atual | Aprovado (RF007, I2) |
| `valor_diaria_contratada` | `DecimalField(max_digits=10, decimal_places=2)` | Cópia da diária do equipamento no registro | Aprovado (RF003, RF006) |
| `quantidade_diarias` | `PositiveIntegerField` | `(prevista − retirada) + 1`, calculada no registro | Aprovado (RN004) |
| `valor_contratado` | `DecimalField(max_digits=12, decimal_places=2)` | `quantidade_diarias × valor_diaria_contratada`, congelado | Aprovado (RF006, CT11) |

Não há campo de status, multa, cancelamento, pagamento ou funcionário responsável: nada disso está na especificação.

**Restrições no banco:**

- `aluguel_um_ativo_por_equipamento`: `UniqueConstraint(fields=["equipamento"], condition=Q(data_devolucao_real__isnull=True))`. Garante, no próprio PostgreSQL, no máximo um aluguel ativo por equipamento.
- `aluguel_prevista_apos_retirada`: `data_devolucao_prevista >= data_retirada`.
- `aluguel_devolucao_apos_retirada`: `data_devolucao_real` vazia ou `>= data_retirada`.
- `aluguel_valores_positivos`: `valor_diaria_contratada > 0`, `quantidade_diarias >= 1` e `valor_contratado > 0`.

"Retirada não anterior à data atual" e "devolução real não posterior à data atual" dependem do dia corrente e **não** podem ser restrições de banco. Ficam no serviço, que recebe `hoje` calculado em `America/Recife`.

## 5. Estados derivados

**Situação do aluguel** (calculada com `hoje = timezone.localdate()` em `America/Recife`), exposta como `situacao` (rótulo exibido) e `situacao_codigo` (código para estilo):

| `situacao` | `situacao_codigo` | Condição |
|----------|--------------------|----------|
| Ativo | `ativo` | Sem devolução e `hoje <= data_devolucao_prevista` |
| Atrasado | `atrasado` | Sem devolução e `hoje > data_devolucao_prevista` |
| Encerrado | `encerrado` | Devolvido com `data_devolucao_real <= data_devolucao_prevista` |
| Encerrado com atraso | `encerrado_com_atraso` | Devolvido com `data_devolucao_real > data_devolucao_prevista` |

Aluguel com retirada futura (I1) aparece como **Ativo**, já que a especificação lista só essas quatro situações — **[verificar]** se o Documento v1.1 prevê rótulo próprio.

**`pode_devolver`:** sem devolução e `hoje >= data_retirada`. Antes da retirada não existe data real válida, porque o intervalo "entre a retirada e a data atual" fica vazio.

## 6. Imutabilidade e preservação histórica

| Regra | Proteção proposta |
|-------|-------------------|
| Código do equipamento imutável após o primeiro aluguel (RF003) | Campo desabilitado no formulário (o Django ignora valor enviado) e checagem no serviço dentro da transação |
| CPF imutável após o primeiro aluguel (RF005) | Mesma abordagem do código |
| Nova diária não afeta aluguéis existentes (RF003) | Valores copiados para o aluguel; o equipamento nunca é usado para recalcular |
| Sem edição de aluguel ou devolução registrados (I2) | Não haverá view de edição; o serviço de devolução só grava quando `data_devolucao_real` está vazia |
| Equipamento com histórico não é excluído (RN003) | `on_delete=PROTECT` no banco + checagem prévia no serviço para mensagem amigável |
| Cliente nunca é excluído (RF005) | Nenhuma view de exclusão + `PROTECT` |

O Django Admin, se habilitado, **não** deve registrar `Equipamento`, `Cliente` nem `Aluguel` com edição livre, porque isso contornaria as regras de serviço (ver [contrato técnico](contrato-tecnico-frontend-backend.md)).

## 7. Concorrência (PostgreSQL)

Todas as operações que alteram estado rodam em `transaction.atomic()` nos serviços.

| Cenário | Risco | Proteção proposta |
|---------|-------|-------------------|
| Dois aluguéis simultâneos do mesmo equipamento | Dois aluguéis ativos | `select_for_update()` na linha do equipamento antes de validar; restrição única parcial como última barreira; `IntegrityError` vira a mensagem de indisponibilidade (CT12) |
| Aluguel × inativação ou exclusão | Inativar ou excluir enquanto um aluguel é criado | As duas operações bloqueiam a mesma linha de `Equipamento` e revalidam as condições dentro da transação; `PROTECT` impede a exclusão com aluguel |
| Duas devoluções do mesmo aluguel | Devolução dupla (CT14) | Atualização condicional: `filter(pk=..., data_devolucao_real__isnull=True).update(...)`; zero linhas afetadas significa "já encerrado" |
| Edição de código ou CPF × primeiro aluguel | Alterar o identificador no mesmo instante do primeiro aluguel | O registro de aluguel bloqueia equipamento e cliente (sempre nessa ordem, para evitar deadlock); a edição bloqueia a mesma linha e revalida "sem histórico" |
| Cadastros simultâneos com o mesmo código ou CPF | Duplicidade | Restrições únicas; `IntegrityError` vira erro de campo |

O isolamento padrão do PostgreSQL (READ COMMITTED) é suficiente com bloqueio de linha e restrições. O SQLite ignora `select_for_update()`, portanto **os testes de concorrência precisam rodar em PostgreSQL** (decisão de ambiente em DEV-02).

## 8. Índices

- Os índices únicos de `codigo` e `cpf` e os índices automáticos das chaves estrangeiras atendem às consultas previstas.
- A restrição única parcial cria o índice usado para verificar se existe aluguel ativo do equipamento.
- Pesquisa por nome ou código com `icontains` não exige índice adicional no volume de um projeto acadêmico.
- Ordenação proposta do histórico: `-data_retirada`, `-id`. Índice próprio só se houver necessidade medida.

## 9. Configurações relacionadas

- `TIME_ZONE = "America/Recife"`, `USE_TZ = True`, `LANGUAGE_CODE = "pt-br"`.
- "Data atual" sempre com `timezone.localdate()`; os serviços aceitam `hoje` como parâmetro para facilitar testes com datas relativas.
- `USE_THOUSAND_SEPARATOR = True`, para que o template exiba `R$ 1.500,00` sem cálculo no frontend.

## 10. Pontos em aberto

1. Tamanhos máximos de `nome`, `codigo` e `nome_completo` — **[verificar]** no Documento v1.1.
2. Normalização e sensibilidade a maiúsculas do código.
3. Inativação de equipamento sem histórico (RF004) e condições de reativação inválida (I3).
4. Rejeição de CPF com dígitos repetidos.
5. Rótulo da situação para aluguel com retirada futura.
6. Campos técnicos de auditoria (por exemplo, data de criação) — não incluídos, por não estarem na especificação.
