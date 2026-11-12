# Rastreabilidade — requisitos, regras e testes

> **Documento não finalizado.** Resumo da especificação técnica **v3** registrada no Jira (épicos EQF-4, EQF-5 e EQF-6, 30/10/2026), que é a referência de planejamento. O **Documento de Requisitos v1.1** é o documento acadêmico, revisado tecnicamente e não publicado neste repositório; a validação acadêmica final aguarda Rafael Ferreira e Ivisson, e a revisão dos cenários de teste segue com a equipe de Testes (Alexandre Abreu e Vinícius Soares). Em caso de divergência entre este resumo e as fontes oficiais (Jira e Documento v1.1), valem as fontes oficiais; divergências entre elas devem ser registradas no Jira.
>
> **RF009 e RF010 (10/11/2026):** acrescentados a pedido do professor no Documento de Requisitos v1.3 e no Documento de Casos de Teste v1.4 (CT17–CT20), com a decisão D16. Aprovados tecnicamente por Rickelme David no EQF-5 (comentário 10078) e implementados no EQF-43. A validação documental de Rafael Ferreira e Ivisson continua pendente e independente; não há homologação registrada.

## Requisitos funcionais

| ID | Nome | Prioridade | Resumo | RN |
|----|------|-----------|--------|----|
| RF001 | Cadastrar equipamentos | Alta | Nome, código único, categoria da lista fixa, descrição opcional e diária > R$ 0,00; criado ativo | RN002 |
| RF002 | Consultar e pesquisar equipamentos | Alta | Pesquisa por nome ou código, com situação e disponibilidade calculada no backend | RN001, RN003 |
| RF003 | Editar informações de equipamentos | Alta | Mesmas validações do RF001; código imutável após o primeiro aluguel; nova diária não afeta aluguéis existentes | RN002, RN003, RN004 |
| RF004 | Excluir, inativar ou reativar equipamentos | Alta | Exclusão só sem histórico; inativação com histórico e sem aluguel ativo; reativação preservando histórico. Interpretação técnica: D10 (abaixo) | RN003, RN002 |
| RF005 | Cadastrar, listar, consultar e editar clientes | Alta | Nome completo e CPF válido e único; CPF imutável após o primeiro aluguel; telefone e e-mail opcionais; sem exclusão | RN002, RN003 |
| RF006 | Registrar aluguel | Alta | Equipamento disponível; datas em America/Recife; diárias inclusivas; valor contratado congelado | RN001–RN004 |
| RF007 | Registrar devolução | Alta | Somente aluguel ativo, uma única vez; data real entre retirada e data atual; indica atraso, sem multa | RN001, RN004 |
| RF008 | Consultar histórico de aluguéis | Média | Lista aluguéis com datas, diárias, valores e situação; mensagem quando não há registros | RN004 |
| RF009 | Pesquisar clientes cadastrados | Média | Na lista de clientes, por parte do nome (sem diferenciar maiúsculas) ou do CPF (parcial ou completo, com ou sem máscara); ordem alfabética; termo preservado; "Nenhum registro encontrado." sem correspondência; só leitura (D16) | RN002 |
| RF010 | Filtrar histórico de aluguéis por situação | Média | Todas, Ativo, Atrasado, Encerrado ou Encerrado com atraso; situação calculada com a data atual em America/Recife; ordem do RF008; valor desconhecido vale "Todas"; seleção preservada; só leitura | RN004 |

Requisito técnico transversal (sem numeração RF): acesso restrito a funcionários autenticados via Django Auth (decisão D1), coberto pela cobertura complementar FC12. Vale também para RF009 e RF010.

## Regras de negócio

| ID | Regra | Pontos principais |
|----|-------|-------------------|
| RN001 | Aluguéis simultâneos e disponibilidade | Máximo um aluguel ativo por equipamento; verificação no backend com proteção contra concorrência; disponibilidade derivada; devolução libera o equipamento |
| RN002 | Validação de dados | Campos obrigatórios; formatos (CPF, telefone, e-mail, categoria, diária); unicidade de código e CPF; imutabilidade após o primeiro aluguel; validação no backend |
| RN003 | Integridade e exclusão/inativação | Exclusão física só sem histórico; inativação sem aluguel ativo; reativação; clientes não são excluídos; devoluções não são alteradas retroativamente |
| RN004 | Datas, duração e valores | Datas em America/Recife; retirada ≥ data atual; diárias = (prevista − retirada) + 1; valor em decimal exato; regras de atraso, sem multa |

## Decisões complementares D10–D15

Aprovadas por Rickelme David e registradas na descrição do épico EQF-5 no Jira em 01/11/2026. Complementam a interpretação técnica dos RF e RN acima: **não alteram o texto normativo** dos requisitos, não criam requisitos novos e não mudam os 16 cenários de teste. A equipe de Requisitos avalia se D10, D11 e D12 exigem atualização do Documento de Requisitos v1.1, que trata esses pontos de forma mais geral.

| Decisão | Interpretação técnica | RF / RN |
|---------|-----------------------|---------|
| D10 — Inativação | Todo equipamento ativo sem aluguel aberto pode ser inativado, com ou sem histórico; amplia a leitura do resumo do RF004 ("inativação com histórico"). Exclusão física continua só sem histórico e sem aluguel aberto; reativação exige dados válidos e nenhum aluguel aberto | RF004, RN003 |
| D11 — Código | Remove espaços das extremidades; único sem diferenciar maiúsculas e minúsculas; grafia informada preservada; reforço no PostgreSQL; imutável após o primeiro aluguel | RF001, RF003, RN002 |
| D12 — CPF e telefone | CPF: remove só pontos e hífen, recusa outros caracteres, 11 dígitos, dígitos verificadores, recusa dígitos todos iguais, único, exibido formatado, imutável após o primeiro aluguel. Telefone: opcional, máscara usual, DDD, 10 ou 11 dígitos, exibido formatado | RF005, RN002 |
| D13 — Aluguel em uma etapa | Formulário único; resumo antes da gravação; aviso de que não há cancelamento; sem página adicional; o backend recalcula e revalida antes de gravar | RF006, RN001, RN004 |
| D14 — Clientes | Consulta pela listagem, com cadastro e edição; sem página de detalhe. A parte "sem pesquisa" foi revisada pela D16 (abaixo) | RF005 |
| D15 — Funcionários | Django Auth; contas provisionadas pelo administrador via Django Admin, restrito a administradores autorizados; sem cadastro público, sem recuperação de senha e sem perfis novos | Requisito transversal (D1), FC12 |

### D16 — revisão da D14 (RF009)

Aprovada tecnicamente por Rickelme David em 10/11/2026, com RF009 e RF010, no comentário 10078 do EQF-5 (`https://rickelmepe.atlassian.net/browse/EQF-5?focusedCommentId=10078`). A lista de clientes passa a oferecer pesquisa por nome ou CPF (RF009); continua sem página de detalhe e sem exclusão de clientes (RN003 f). Nenhuma RN é alterada. A validação documental da equipe de Requisitos (Rafael Ferreira e Ivisson) segue pendente.

Decisões técnicas aprovadas no mesmo registro, implementadas no EQF-43:

| Ponto | Decisão |
|-------|---------|
| CPF na pesquisa | Parcial ou completo, com ou sem máscara: só pontos e hífen são desconsiderados (RN002 b); o termo vale como CPF se, sem eles, sobrarem apenas dígitos |
| Acentos | A pesquisa por nome não diferencia maiúsculas, mas **não ignora acentos** ("joao" não encontra "João") |
| Ordem do histórico filtrado | A mesma do RF008 implementado: `-data_retirada`, `-pk`. O texto "ordem decrescente de registro" da v1.3 é lido como "do aluguel mais recente para o mais antigo" |
| Filtro desconhecido | Vale "Todas" |
| Templates | P05 e P08 implementados no padrão de P02; revisados por Raphael em 11/11/2026 |

O detalhamento técnico de D10–D15 (rotas, formulários, modelagem) está nos documentos do DEV-01 (`contrato-tecnico-frontend-backend.md`, `modelagem-proposta.md` e `plano-backend-dev01-dev03.md`), que são propostas até o aceite de Rickelme e Raphael e entram na `main` por PR próprio.

## Cenários de teste planejados

Cenários Gherkin obrigatórios, um positivo e um negativo por RF, sem Esquema do Cenário: os 16 originais (CT01–CT16, preservados sem alteração) e, desde o Documento de Casos de Teste v1.4 (10/11/2026), CT17–CT20 para RF009 e RF010. CT17–CT20 ainda não foram executados pela equipe de Testes; a automação fica nos `test_cenarios_ct.py` de `clientes` e `alugueis`.

| CT | RF | RN | Tipo | Cenário |
|----|----|----|------|---------|
| CT01 | RF001 | RN002 | Positivo | Cadastrar equipamento com dados válidos — fica ativo e disponível |
| CT02 | RF001 | RN002 | Negativo | Cadastrar equipamento com código já existente — recusado |
| CT03 | RF002 | RN001 | Positivo | Pesquisar equipamento por código — exibe disponibilidade calculada |
| CT04 | RF002 | — | Negativo | Pesquisar termo inexistente — "Nenhum registro encontrado" |
| CT05 | RF003 | RN004 | Positivo | Editar diária — aluguel já registrado mantém o valor contratado |
| CT06 | RF003 | RN002 | Negativo | Editar equipamento com diária R$ 0,00 — recusado |
| CT07 | RF004 | RN003 | Positivo | Excluir equipamento sem histórico, com confirmação — removido |
| CT08 | RF004 | RN003 | Negativo | Excluir equipamento com histórico — bloqueado (inativação disponível) |
| CT09 | RF005 | RN002 | Positivo | Cadastrar cliente com nome e CPF válido, sem contatos — cadastrado |
| CT10 | RF005 | RN002 | Negativo | Cadastrar cliente com CPF já cadastrado — recusado |
| CT11 | RF006 | RN004 | Positivo | Registrar aluguel de 3 diárias a R$ 50,00 — valor contratado R$ 150,00 |
| CT12 | RF006 | RN001 | Negativo | Alugar equipamento com aluguel ativo — recusado |
| CT13 | RF007 | RN001, RN004 | Positivo | Registrar devolução com data atual — aluguel encerrado, equipamento disponível |
| CT14 | RF007 | RN004 | Negativo | Devolver aluguel já encerrado — recusado |
| CT15 | RF008 | RN004 | Positivo | Consultar histórico — exibe dados e situação de cada aluguel |
| CT16 | RF008 | RN004 | Negativo | Histórico sem registros — mensagem de ausência, sem dados inexistentes |
| CT17 | RF009 | RN002 | Positivo | Pesquisar "maria qa" — exibe "Maria QA Pesquisa" com CPF formatado, não exibe "João Silva" e mantém o termo |
| CT18 | RF009 | RN002 | Negativo | Pesquisar "CLIENTE_FANTASMA_999" — "Nenhum registro encontrado.", sem clientes na lista |
| CT19 | RF010 | RN004 | Positivo | Filtrar por "Encerrado" — só aluguéis encerrados, sem os ativos, opção mantida |
| CT20 | RF010 | RN004 | Negativo | Filtrar por "Encerrado com atraso" sem registros nessa situação — "Nenhum registro encontrado.", sem linhas |

Cobertura das RN nos 20 cenários: RN001 (CT03, CT12, CT13); RN002 (CT01, CT02, CT06, CT09, CT10, CT17, CT18); RN003 (CT07, CT08); RN004 (CT05, CT11, CT13, CT14, CT15, CT16, CT19, CT20).

Suítes da v1.4: **Smoke** CT01, CT03, CT09, CT11, CT13, CT15; **Sanity** CT09, CT15, CT16, CT17–CT20 (telas alteradas por RF009 e RF010); **Regression** CT01–CT20.

Há ainda uma cobertura complementar (FC01–FC14), fora da contagem acadêmica, descrita no épico EQF-6.

## Atividades no Jira

| Área | Atividades |
|------|-----------|
| Requisitos | REQ-03 (EQF-9) RF; REQ-04 (EQF-10) RN; REQ-05 (EQF-11) revisão; REQ-06 (EQF-12) finalização |
| Desenvolvimento | DEV-04 (EQF-16) CT01–CT08; DEV-05 (EQF-17) CT09–CT10; DEV-06 (EQF-18) CT11–CT14; DEV-07 (EQF-19) CT15–CT16; EQF-43 RF009 e RF010 (CT17–CT20) |
| Testes | QA-02 (EQF-22) positivos; QA-03 (EQF-23) negativos; QA-04 (EQF-24) revisão; QA-05 (EQF-25) dados; QA-06 (EQF-26) execução |

## Decisões I1–I5

As decisões I1–I5 da v3 foram **aprovadas por Rickelme David em 01/11/2026**. O detalhamento está no Jira e no Documento de Requisitos v1.1. O resumo de RF e RN acima **não reproduz** esse detalhamento: antes de implementar funcionalidade afetada (retirada futura, correção de registros, reativação, prioridades, armazenamento do CPF), consulte a decisão registrada.
