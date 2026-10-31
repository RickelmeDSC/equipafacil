# Arquitetura planejada

> **Estado: planejamento.** Nada abaixo foi implementado ou configurado. Não há projeto Django, banco de dados, ambiente de hospedagem nem deploy.

Referência: especificação v3, épico EQF-5 (Desenvolvimento do Sistema) no Jira. Detalhes de organização do projeto serão definidos em DEV-01 (EQF-13) e DEV-02 (EQF-14).

## Stack

| Camada | Tecnologia | Observação |
|--------|-----------|------------|
| Linguagem | Python 3 | Versão a definir em DEV-02 |
| Framework | Django | Aplicação monolítica com renderização no servidor |
| Interface | Django Templates + Bootstrap | HTML, CSS e JavaScript leve; responsiva |
| Autenticação | Django Auth | Apenas funcionários; contas criadas pelo administrador; sem cadastro público nem recuperação de senha por e-mail |
| Banco de dados | PostgreSQL | Hospedagem prevista no **Neon** |
| Hospedagem | **Render** | Previsto para DEV-08 |
| Fuso operacional | `America/Recife` | "Data atual" sempre no fuso local |

## Divisão frontend / backend

**Backend — Rickelme David**

- Models, regras RN001–RN004, validações, cálculos de diárias e valores (Decimal).
- Disponibilidade derivada e proteção contra aluguéis simultâneos.
- Autenticação, fuso, banco, integração, infraestrutura e deploy.
- Envia ao template estados já calculados (ex.: `pode_excluir`, `pode_inativar`, `pode_reativar`, `codigo_editavel`, `cpf_editavel`, `pode_devolver`).

**Frontend — Raphael Eloi**

- Templates, layout Bootstrap, responsividade.
- Exibição de listas, formulários, campos somente leitura, mensagens de erro e estados recebidos do backend.
- Máscaras apenas visuais (telefone, CPF, R$); nenhuma regra de negócio no cliente.

Mudanças nesse contrato são combinadas entre os dois antes da implementação.

## Páginas previstas

| Página | Função | Referência |
|--------|--------|-----------|
| P10 | Login | D1 |
| P01 | Início / menu | D1 |
| P02 | Lista e pesquisa de equipamentos | RF002 |
| P03 | Formulário de equipamento | RF001, RF003 |
| P04 | Excluir / inativar / reativar equipamento | RF004 |
| P05 | Lista de clientes | RF005 |
| P06 | Formulário de cliente | RF005 |
| P07 | Novo aluguel | RF006 |
| P08 | Histórico de aluguéis | RF008 |
| P09 | Registrar devolução | RF007 |

## Pontos em aberto

- Inconsistências I1–I5 da especificação v3 (aluguel com retirada futura, correção de registros, reativação inválida, prioridades, armazenamento do CPF) aguardam decisão.
- Estrutura de apps Django, versão do Python, ferramentas de teste e lint: DEV-01/DEV-02.
