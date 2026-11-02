# Modelagem implementada — DEV-03 (EQF-15)

> **Situação em 02/11/2026: implementação local, não publicada.** Branch `feat/backend-eqf-15-modelagem`, criada a partir de `feat/backend-dev02-foundation` (`87d23fb`), porque a `main` ainda não tem a fundação Django. No Jira, o DEV-03 continua formalmente bloqueado pela REQ-04 (EQF-10); este trabalho não encerra nem altera essa dependência. O PR do DEV-03 só deve ser aberto depois da integração (ou do alinhamento) da base DEV-02, para não misturar entregas.

Base: `docs/modelagem-proposta.md` (v0.4, proposta no PR #2), `docs/rastreabilidade.md`, RF001–RF008, RN001–RN004, I1–I5, D10–D15 e as mensagens propostas no EQF-5. Nada de interface foi implementado: não há views, formulários, URLs nem templates de domínio.

## Classificação das fontes

| Tipo | O que foi usado |
|------|-----------------|
| Regras aprovadas | RF001–RF008, RN001–RN004, I1–I5, D10–D15, categorias fixas (D8), Decimal (D9), fuso `America/Recife` |
| Propostas técnicas de Rickelme (modelagem v0.4) | Tamanhos de campo (`codigo` 30, `nome` 120, `nome_completo` 150), valores internos das categorias, `data_devolucao_real` nula como indicador de aluguel aberto, nomes das restrições, restrições opcionais de reforço |
| Dependem do aceite de Raphael | Nomes expostos aos templates (`pode_*`, `situacao`, `disponivel` etc.) e a prévia em JavaScript do aluguel: não usados por nenhuma tela nesta etapa |
| Aguardam validação acadêmica | Documento de Requisitos v1.1 (Rafael Ferreira e Ivisson), inclusive se D10–D12 exigem atualização |
| Mensagens | Textos propostos no EQF-5, centralizados em `config/mensagens.py`; não são textos definitivamente aprovados |

## Modelos

| Modelo | Campos | Observações |
|--------|--------|-------------|
| `Equipamento` | `codigo`, `nome`, `categoria`, `valor_diaria`, `descricao`, `ativo` | Código sem espaços nas extremidades e único sem diferenciar maiúsculas (D11); grafia preservada; diária `Decimal` > 0 com até duas casas; criado ativo. Sem campo de disponibilidade |
| `Cliente` | `nome_completo`, `cpf`, `telefone`, `email` | CPF persistido com 11 dígitos (I5); remove só pontos e hífen e recusa outros caracteres, dígitos verificadores inválidos e dígitos todos iguais (D12); telefone opcional com 10 ou 11 dígitos; sem endereço, exclusão, pesquisa ou detalhe (D14) |
| `Aluguel` | `equipamento`, `cliente`, `data_retirada`, `data_devolucao_prevista`, `data_devolucao_real`, `valor_diaria_contratada`, `quantidade_diarias`, `valor_contratado` | Aberto = `data_devolucao_real` nula; diárias inclusivas; diária e valor congelados no registro; sem status, multa, cancelamento ou pagamento |

Sem campos de criação e atualização: não estão previstos na arquitetura nem na modelagem. Os modelos de domínio não são registrados no Django Admin (D15; modelagem, seção 7).

Atributos calculados, nunca persistidos: `Equipamento.disponivel`, `tem_historico`, `tem_aluguel_aberto`, `codigo_editavel`; `Cliente.cpf_formatado`, `telefone_formatado`, `cpf_editavel`; `Aluguel.aberto`, `situacao()`, `situacao_codigo()` e `pode_devolver()`, calculados com a data atual em `America/Recife`. Consultas: `Equipamento.objects.disponiveis()` e `Aluguel.objects.abertos()` / `encerrados()`.

`alugueis.services.registrar_aluguel` é a base transacional do registro (DEV-06 construirá formulário e view sobre ela): recebe só identificadores e datas, bloqueia equipamento e cliente nessa ordem, revalida a disponibilidade e recalcula diárias e valor a partir do banco (D13).

## Onde cada invariante é garantido

| Invariante | Banco (PostgreSQL e SQLite) | Modelo (`save()` → `full_clean()`) | Serviço transacional |
|------------|-----------------------------|------------------------------------|----------------------|
| Código único sem diferenciar maiúsculas (D11) | `equipamento_codigo_unico_ci` (índice único em `LOWER(codigo)`) | Erro de campo "Já existe um equipamento com este código." | — |
| Código sem espaços nas extremidades e não vazio | `equipamento_codigo_normalizado` | Normaliza antes de validar | — |
| Nome, categoria e diária válidos | `equipamento_nome_preenchido`, `equipamento_categoria_valida`, `equipamento_diaria_positiva` | Mensagens do EQF-5 | — |
| Diária com no máximo duas casas | **Não**: `numeric(10,2)` do PostgreSQL arredonda em silêncio | Recusa 3 casas ou mais | — |
| Código e CPF imutáveis após o primeiro aluguel | — | Recusa a alteração, inclusive só de maiúsculas no código | Código: o serviço de edição do DEV-04 bloqueia a linha do equipamento ([`equipamentos-operacional.md`](equipamentos-operacional.md)); CPF: DEV-05 |
| CPF com 11 dígitos, único e sem dígitos repetidos | `cliente_cpf_unico`, `cliente_cpf_onze_digitos`, `cliente_cpf_nao_repetido` | Normaliza, valida dígitos verificadores e caracteres | — |
| Telefone com 10 ou 11 dígitos | `cliente_telefone_digitos` | Normaliza a máscara e valida | — |
| Um aluguel aberto por equipamento (RN001) | **Índice único parcial** `aluguel_um_aberto_por_equipamento` (`WHERE data_devolucao_real IS NULL`) | Recusa o segundo aberto | `select_for_update()` no equipamento; `IntegrityError` vira "Este equipamento não está disponível para aluguel." |
| Equipamento ativo para alugar | — | Recusa no registro | Revalida dentro da transação |
| Retirada não anterior à data atual | Não (depende do dia) | Não (valeria só no registro) | Recusa com a data atual em `America/Recife` |
| Prevista ≥ retirada; devolução ≥ retirada | `aluguel_prevista_apos_retirada`, `aluguel_devolucao_apos_retirada` | Mensagens do EQF-5 | Também valida antes de bloquear |
| Valores positivos e pelo menos 1 diária | `aluguel_valores_positivos` | — | Sempre calculados |
| Diárias e valor coerentes com datas e diária | Não (aritmética de datas e decimais difere entre bancos) | Recusa valores inconsistentes no registro | Calcula a partir do banco |
| Aluguel não é editado; devolução gravada uma única vez (I2) | — | Recusa qualquer alteração além da primeira devolução | Devolução com data atual: DEV-06 |
| Histórico preservado | Chaves estrangeiras impedem apagar equipamento ou cliente referenciado | `PROTECT` | — |

Operações em lote (`bulk_create`, `update`) ignoram o modelo: nelas valem só as restrições do banco, e os testes cobrem esse caminho. Validação de aplicação não elimina corridas; a proteção concorrente vem do bloqueio de linha e do índice único parcial.

## PostgreSQL × SQLite

| Ponto | PostgreSQL | SQLite (temporário) |
|-------|------------|---------------------|
| Restrições `CHECK`, índice parcial e índice por expressão | Garantidos | Também garantidos (as restrições com expressão regular usam a função `REGEXP` que o Django registra) |
| `select_for_update()` | Bloqueia a linha | Sem efeito |
| `LOWER()` em letras acentuadas | Converte conforme a localidade do banco | Só converte letras ASCII |
| Testes de concorrência | Executados (2 testes com threads; o DEV-04 acrescenta 6) | Pulados |
| Introspecção de índices e restrições | Executada (4 testes) | Pulada |

## Pendências

1. Aceite do contrato e da modelagem no PR #2 (Raphael), principalmente dos nomes expostos aos templates.
2. Confirmar a adoção das restrições opcionais de reforço (código normalizado, CPF sem dígitos repetidos, dígitos do telefone, nome preenchido), adotadas aqui por implementarem regras já aprovadas.
3. Mensagens sem texto no EQF-5 usadas internamente: "Aluguel registrado não pode ser alterado." e a de valores inconsistentes; nenhuma tela as exibe nesta etapa.
4. Diagrama de dados a anexar ao EQF-15.
5. REQ-04 (EQF-10) e a validação acadêmica do Documento v1.1.
6. Serviço de edição de clientes (DEV-05) e devolução (DEV-06). Os serviços de equipamentos e os indicadores `pode_excluir`, `pode_inativar` e `pode_reativar` foram implementados no DEV-04 ([`equipamentos-operacional.md`](equipamentos-operacional.md)).
