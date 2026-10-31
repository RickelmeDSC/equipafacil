# Rastreabilidade — requisitos, regras e testes

> **Documento não finalizado.** Resumo da especificação funcional **v3** registrada no Jira (épicos EQF-4, EQF-5 e EQF-6, 30/10/2026). As decisões técnicas foram aprovadas, mas a documentação acadêmica **ainda aguarda revisão** das equipes de Requisitos (Rafael Ferreira e Ivisson) e Testes (Alexandre Abreu e Vinícius Soares). Em caso de divergência, vale o Jira.

## Requisitos funcionais

| ID | Nome | Prioridade | Resumo | RN |
|----|------|-----------|--------|----|
| RF001 | Cadastrar equipamentos | Alta | Nome, código único, categoria da lista fixa, descrição opcional e diária > R$ 0,00; criado ativo | RN002 |
| RF002 | Consultar e pesquisar equipamentos | Alta | Pesquisa por nome ou código, com situação e disponibilidade calculada no backend | RN001, RN003 |
| RF003 | Editar informações de equipamentos | Alta | Mesmas validações do RF001; código imutável após o primeiro aluguel; nova diária não afeta aluguéis existentes | RN002, RN003, RN004 |
| RF004 | Excluir, inativar ou reativar equipamentos | Alta | Exclusão só sem histórico; inativação com histórico e sem aluguel ativo; reativação preservando histórico | RN003, RN002 |
| RF005 | Cadastrar, listar, consultar e editar clientes | Alta | Nome completo e CPF válido e único; CPF imutável após o primeiro aluguel; telefone e e-mail opcionais; sem exclusão | RN002, RN003 |
| RF006 | Registrar aluguel | Alta | Equipamento disponível; datas em America/Recife; diárias inclusivas; valor contratado congelado | RN001–RN004 |
| RF007 | Registrar devolução | Alta | Somente aluguel ativo, uma única vez; data real entre retirada e data atual; indica atraso, sem multa | RN001, RN004 |
| RF008 | Consultar histórico de aluguéis | Média | Lista aluguéis com datas, diárias, valores e situação; mensagem quando não há registros | RN004 |

Requisito técnico transversal (sem numeração RF): acesso restrito a funcionários autenticados via Django Auth (decisão D1), coberto pela cobertura complementar FC12.

## Regras de negócio

| ID | Regra | Pontos principais |
|----|-------|-------------------|
| RN001 | Aluguéis simultâneos e disponibilidade | Máximo um aluguel ativo por equipamento; verificação no backend com proteção contra concorrência; disponibilidade derivada; devolução libera o equipamento |
| RN002 | Validação de dados | Campos obrigatórios; formatos (CPF, telefone, e-mail, categoria, diária); unicidade de código e CPF; imutabilidade após o primeiro aluguel; validação no backend |
| RN003 | Integridade e exclusão/inativação | Exclusão física só sem histórico; inativação sem aluguel ativo; reativação; clientes não são excluídos; devoluções não são alteradas retroativamente |
| RN004 | Datas, duração e valores | Datas em America/Recife; retirada ≥ data atual; diárias = (prevista − retirada) + 1; valor em decimal exato; regras de atraso, sem multa |

## Cenários de teste planejados

Exatamente 16 cenários Gherkin obrigatórios (um positivo e um negativo por RF), sem Esquema do Cenário.

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

Cobertura das RN nos 16 cenários: RN001 (CT03, CT12, CT13); RN002 (CT01, CT02, CT06, CT09, CT10); RN003 (CT07, CT08); RN004 (CT05, CT11, CT13, CT14, CT15, CT16).

Há ainda uma cobertura complementar (FC01–FC14), fora da contagem acadêmica, descrita no épico EQF-6.

## Atividades no Jira

| Área | Atividades |
|------|-----------|
| Requisitos | REQ-03 (EQF-9) RF; REQ-04 (EQF-10) RN; REQ-05 (EQF-11) revisão; REQ-06 (EQF-12) finalização |
| Desenvolvimento | DEV-04 (EQF-16) CT01–CT08; DEV-05 (EQF-17) CT09–CT10; DEV-06 (EQF-18) CT11–CT14; DEV-07 (EQF-19) CT15–CT16 |
| Testes | QA-02 (EQF-22) positivos; QA-03 (EQF-23) negativos; QA-04 (EQF-24) revisão; QA-05 (EQF-25) dados; QA-06 (EQF-26) execução |

## Pendências da especificação

As inconsistências I1–I5 da v3 têm propostas registradas no Jira, **ainda pendentes de aprovação**. Nenhuma foi aplicada aos RF ou RN acima.
