# Modelagem proposta — EquipaFácil

> **PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.2 — 01/11/2026, reconciliada com o Documento de Requisitos v1.1 e com a auditoria do Jira de 01/11/2026. **Nada aqui está implementado**: não existe projeto Django, model ou migration no repositório. A implementação dos models, das migrations e do diagrama de dados é escopo de DEV-03 (EQF-15).
>
> **Fontes:** Documento de Requisitos v1.1 (RF001–RF008, RN001–RN004, decisões D1–D9, N2–N6, TZ e I1–I5), [`rastreabilidade.md`](rastreabilidade.md), [`arquitetura-planejada.md`](arquitetura-planejada.md) e o [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md). Nesta branch, baseada na `main`, os resumos do repositório ainda tratam I1–I5 como pendentes; a atualização deles está no PR #1.

Documentos relacionados: [contrato técnico frontend × backend](contrato-tecnico-frontend-backend.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

## 1. Princípios

| Princípio | Como a modelagem atende | Origem |
|-----------|-------------------------|--------|
| Disponibilidade derivada | Não há campo `disponivel`; ela é calculada (ativo e sem aluguel aberto) | RN001 c |
| Aluguel aberto persistido | **Proposta:** `data_devolucao_real` nula é o indicador persistido de aluguel aberto. Não existe coluna de status | RN001, RN004 f |
| Um aluguel aberto por equipamento | Restrição única parcial sobre a coluna persistida + bloqueio de linha na transação | RN001 a, b |
| Situação apenas de apresentação | Ativo, Atrasado, Encerrado e Encerrado com atraso são calculados; **nenhuma restrição de banco depende deles** | RF008, RN004 g |
| Valores exatos | `DecimalField` com duas casas; nunca `float` | RN004 e, D9 |
| Datas de negócio | `DateField` interpretado no calendário `America/Recife` | RN004 a, TZ |
| Valor contratado congelado | Diária, quantidade de diárias e valor contratado copiados para o aluguel no registro | RF003, RF006, D3 |
| Histórico preservado | Chaves estrangeiras com `PROTECT`; aluguéis não são editados nem excluídos | RN003, I2 |
| Validação no backend | Restrições no banco + validação em formulários e serviços; a tela nunca é a única barreira | RN002 e |

Convenções propostas: chave primária `BigAutoField` (padrão do Django), nomes de campos em português, restrições nomeadas. As restrições usam `CheckConstraint(condition=...)`, disponível desde o Django 5.1 e, portanto, em todas as séries candidatas (5.2 LTS, 6.0 e 6.1).

## 2. Equipamento

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `nome` | `CharField(max_length=120)` | Obrigatório | Obrigatoriedade aprovada (RF001); tamanho é proposta |
| `codigo` | `CharField(max_length=30, unique=True)` | Obrigatório e único; imutável após o primeiro aluguel | Aprovado (RF001, RF003, RN002, N3); tamanho é proposta |
| `categoria` | `CharField(max_length=30, choices=Categoria.choices)` | Uma das cinco categorias fixas | Aprovado (RF001, D8) |
| `descricao` | `TextField(blank=True)` | Opcional | Aprovado (RF001) |
| `valor_diaria` | `DecimalField(max_digits=10, decimal_places=2)` | Maior que R$ 0,00, duas casas | Aprovado (RF001, D9); `max_digits` é proposta |
| `ativo` | `BooleanField(default=True)` | Criado ativo; muda só por inativação ou reativação | Aprovado (RF001, RF004) |

**Categorias (`TextChoices`):** Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil e Outros. Valores internos sugeridos: `ferramentas`, `audiovisuais`, `informatica`, `construcao_civil` e `outros`.

**Restrições no banco:** `equipamento_codigo_unico` (unicidade de `codigo`) e `equipamento_diaria_positiva` (`valor_diaria > 0`).

**Atributos calculados (backend, nunca persistidos):**

| Atributo | Regra | Origem |
|----------|-------|--------|
| `disponivel` | `ativo` e nenhum aluguel aberto | RN001 c |
| `tem_historico` | Existe pelo menos um aluguel do equipamento | RN003 |
| `tem_aluguel_ativo` | Existe aluguel aberto | RN003 c |
| `codigo_editavel` | Não `tem_historico` | RF003, N3 |
| `pode_excluir` | Não `tem_historico` | RF004, RN003 a |
| `pode_inativar` | `ativo`, `tem_historico` e não `tem_aluguel_ativo` | RF004, RN003 b, c — **interpretação pendente** para equipamento sem histórico |
| `pode_reativar` | Não `ativo`, dados cadastrais válidos e não `tem_aluguel_ativo` | RF004, RN003 e, N4 |

"Dados cadastrais válidos" na reativação significa revalidar o registro com as regras atuais (RN002) antes de reativar. Pela interface não se cria esse estado inválido; o teste usa massa preparada e é complementar (I3).

**Interpretações pendentes:** inativação de equipamento sem histórico; normalização do código e sensibilidade a maiúsculas. Nenhuma das duas está decidida e nenhuma restrição foi proposta para elas.

## 3. Cliente

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `nome_completo` | `CharField(max_length=150)` | Obrigatório | Aprovado (RF005, RN002); tamanho é proposta |
| `cpf` | `CharField(max_length=11, unique=True)` | Entrada com ou sem pontuação; remove **apenas** pontos e hífen e recusa qualquer outro caractere; exatamente 11 dígitos; dígitos verificadores; único; exibido formatado; imutável após o primeiro aluguel | Aprovado (RF005, RN002, N3, I5) |
| `telefone` | `CharField(max_length=11, blank=True)` | Opcional; brasileiro com DDD, 10 ou 11 dígitos; armazenado só com dígitos; exibido formatado | Aprovado (RF005, N5) |
| `email` | `EmailField(blank=True)` | Opcional; formato validado quando informado | Aprovado (RF005, RN002) |

Clientes **não são excluídos** nem inativados (RF005, RN003 f, D7).

**Restrições no banco:** `cliente_cpf_unico` (unicidade de `cpf`), `cliente_cpf_onze_digitos` (`cpf` corresponde a `^[0-9]{11}$`) e, opcionalmente, `cliente_telefone_digitos` (vazio ou com 10 a 11 dígitos).

Dígitos verificadores ficam no formulário/serviço. **Propostas não aprovadas:** recusar CPF com todos os dígitos iguais; quais caracteres do telefone são removidos na normalização.

**Atributos calculados:** `cpf_formatado` (`000.000.000-00`), `telefone_formatado` e `cpf_editavel` (nenhum aluguel associado).

## 4. Aluguel

| Campo | Tipo proposto | Regras | Situação |
|-------|---------------|--------|----------|
| `equipamento` | `ForeignKey(Equipamento, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `cliente` | `ForeignKey(Cliente, on_delete=PROTECT, related_name="alugueis")` | Obrigatório | Aprovado (RF006) |
| `data_retirada` | `DateField` | Não anterior à data atual no registro (retirada futura permitida) | Aprovado (RF006, RN004 b, D2/D6, I1) |
| `data_devolucao_prevista` | `DateField` | Igual ou posterior à retirada; mínimo de 1 diária | Aprovado (RF006, RN004 c) |
| `data_devolucao_real` | `DateField(null=True, blank=True)` | Nula enquanto aberto; preenchida uma única vez, entre a retirada e a data atual | Aprovado (RF007, RN004 f, N2, I2) |
| `valor_diaria_contratada` | `DecimalField(max_digits=10, decimal_places=2)` | Cópia da diária do equipamento no registro | Aprovado (RF006, D3) |
| `quantidade_diarias` | `PositiveIntegerField` | `(prevista − retirada) + 1`, calculada no registro | Aprovado (RN004 d, D3) |
| `valor_contratado` | `DecimalField(max_digits=12, decimal_places=2)` | `quantidade_diarias × valor_diaria_contratada`, congelado | Aprovado (RN004 e, CT11) |

Não há campo de status, multa, cancelamento, pagamento ou funcionário responsável: nada disso está na especificação.

**Restrições no banco (todas sobre colunas persistidas):**

- `aluguel_um_aberto_por_equipamento`: `UniqueConstraint(fields=["equipamento"], condition=Q(data_devolucao_real__isnull=True))`. No máximo um aluguel aberto por equipamento, garantido pelo próprio PostgreSQL. Aluguéis com retirada futura também estão abertos, o que bloqueia o equipamento desde o registro (I1).
- `aluguel_prevista_apos_retirada`: `data_devolucao_prevista >= data_retirada`.
- `aluguel_devolucao_apos_retirada`: `data_devolucao_real` nula ou `>= data_retirada`.
- `aluguel_valores_positivos`: `valor_diaria_contratada > 0`, `quantidade_diarias >= 1` e `valor_contratado > 0`.

Regras que dependem do dia corrente — retirada não anterior à data atual e devolução real não posterior à data atual — **não** podem ser restrições de banco. Ficam no serviço, que recebe `hoje` calculado em `America/Recife`.

## 5. Estados derivados (apresentação)

**Situação do aluguel**, calculada com `hoje = timezone.localdate()` em `America/Recife` e exposta como `situacao` (rótulo) e `situacao_codigo` (estilo). É só apresentação: o banco não a armazena nem a usa em restrições.

| `situacao` | `situacao_codigo` | Condição (RN004 g) |
|------------|-------------------|--------------------|
| Ativo | `ativo` | Aberto e devolução prevista não anterior à data atual |
| Atrasado | `atrasado` | Aberto e devolução prevista anterior à data atual |
| Encerrado | `encerrado` | Devolvido com data real não posterior à prevista |
| Encerrado com atraso | `encerrado_com_atraso` | Devolvido com data real posterior à prevista |

Aluguel com retirada futura aparece como **Ativo** (v1.1, limitações: "um aluguel registrado, inclusive com retirada futura, fica ativo").

**`pode_devolver`:** aberto e `hoje` igual ou posterior à retirada (I1: "a devolução não pode ser registrada antes da data de retirada").

## 6. Revisão de compatibilidade

| Ponto verificado | Resultado |
|------------------|-----------|
| Aluguel aberto × data real de devolução | Mesmo conceito: aberto = `data_devolucao_real` nula (indicador persistido proposto) |
| Situação de apresentação × restrição única parcial | A restrição usa a coluna persistida; a situação calculada não entra no banco |
| Restrição única × bloqueio concorrente | Complementares: o bloqueio dá mensagem amigável; a restrição é a última barreira |
| Preservação do histórico | `PROTECT` em `equipamento` e `cliente`; nenhuma rota de edição ou exclusão de aluguel |
| Unicidade do CPF | Restrição única sobre os 11 dígitos normalizados |
| Decimal para preços | `DecimalField` em diária e valores contratados |
| Fuso `America/Recife` | `TIME_ZONE` e `timezone.localdate()`; nunca o dia UTC |
| Diárias inclusivas | `(prevista − retirada) + 1`, com mínimo de 1 garantido por restrição |
| Retirada futura | Permitida; o aluguel fica aberto e bloqueia o equipamento desde o registro |
| Ausência de cancelamento | Nenhum campo, rota ou estado de cancelamento |

## 7. Imutabilidade e preservação histórica

| Regra | Proteção proposta |
|-------|-------------------|
| Código imutável após o primeiro aluguel (RF003, N3) | Campo desabilitado no formulário (o Django ignora valor enviado) e checagem no serviço dentro da transação |
| CPF imutável após o primeiro aluguel (RF005, N3) | Mesma abordagem do código |
| Nova diária não afeta aluguéis existentes (RF003) | Valores copiados para o aluguel; o equipamento nunca é usado para recalcular |
| Sem edição de aluguel ou devolução (I2) | Nenhuma view de edição; a devolução só grava quando `data_devolucao_real` está nula |
| Equipamento com histórico não é excluído (RN003 b) | `PROTECT` + checagem prévia no serviço para mensagem amigável |
| Cliente nunca é excluído (RN003 f) | Nenhuma view de exclusão + `PROTECT` |

`Equipamento`, `Cliente` e `Aluguel` não devem ser registrados no Django Admin para edição livre, pois isso contornaria as regras de serviço.

## 8. Concorrência (PostgreSQL)

Todas as operações que alteram estado rodam em `transaction.atomic()` nos serviços.

| Cenário | Risco | Proteção proposta |
|---------|-------|-------------------|
| Dois aluguéis simultâneos do mesmo equipamento | Dois aluguéis abertos | `select_for_update()` na linha do equipamento antes de validar; restrição única parcial como última barreira; `IntegrityError` vira a mensagem de indisponibilidade (CT12) |
| Parâmetro HTTP manipulado (RN001 b) | Alugar equipamento fora da lista de disponíveis | O serviço revalida disponibilidade a partir do banco, ignorando o que a tela ofereceu |
| Aluguel × inativação ou exclusão | Inativar ou excluir durante um aluguel | As duas operações bloqueiam a mesma linha de `Equipamento` e revalidam dentro da transação; `PROTECT` impede exclusão com aluguel |
| Duas devoluções do mesmo aluguel | Devolução dupla (CT14) | Atualização condicional `filter(pk=..., data_devolucao_real__isnull=True).update(...)`; zero linhas afetadas significa "já encerrado" |
| Edição de código ou CPF × primeiro aluguel | Alterar o identificador no instante do primeiro aluguel | O registro de aluguel bloqueia equipamento e cliente (sempre nessa ordem, para evitar deadlock); a edição bloqueia a mesma linha e revalida "sem histórico" |
| Cadastros simultâneos com mesmo código ou CPF | Duplicidade | Restrições únicas; `IntegrityError` vira erro de campo |

O isolamento padrão do PostgreSQL (READ COMMITTED) é suficiente com bloqueio de linha e restrições. O SQLite ignora `select_for_update()`, portanto **os testes de concorrência precisam rodar em PostgreSQL** (ambiente definido em DEV-02).

## 9. Índices

- Índices únicos de `codigo` e `cpf` e índices automáticos das chaves estrangeiras.
- A restrição única parcial cria o índice usado para verificar se há aluguel aberto do equipamento.
- Pesquisa por nome ou código com `icontains` não exige índice adicional no volume de um projeto acadêmico.
- Ordenação proposta do histórico: `-data_retirada`, `-id`.

## 10. Configurações relacionadas

- `TIME_ZONE = "America/Recife"`, `USE_TZ = True`, `LANGUAGE_CODE = "pt-br"`.
- "Data atual" sempre com `timezone.localdate()`; os serviços aceitam `hoje` como parâmetro para testes com datas relativas.
- `USE_THOUSAND_SEPARATOR = True`, para exibir `R$ 1.500,00` sem cálculo no template.

## 11. Pontos em aberto

1. Confirmar `data_devolucao_real` nula como indicador persistido de aluguel aberto.
2. Inativação de equipamento sem histórico (interpretação pendente).
3. Normalização e sensibilidade a maiúsculas do código (proposta não aprovada).
4. Recusa de CPF com dígitos repetidos e normalização do telefone (propostas não aprovadas).
5. Tamanhos máximos de `nome`, `codigo` e `nome_completo` (não definidos no v1.1).
6. Diagrama de dados oficial, a produzir em DEV-03.
