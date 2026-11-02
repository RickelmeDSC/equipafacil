# Arquitetura planejada

> **Estado: planejamento, com a fundação de DEV-02 em preparação.** Existem o projeto Django, os apps sem modelos e a autenticação nativa (veja o README). Não há modelos de domínio, banco PostgreSQL configurado, ambiente de hospedagem nem deploy.

Referências: especificação técnica v3, épico EQF-5 (Desenvolvimento do Sistema) no Jira, e Documento de Requisitos v1.1 (acadêmico, não publicado neste repositório). Detalhes de organização do projeto serão definidos em DEV-01 (EQF-13) e DEV-02 (EQF-14).

## Stack

| Camada | Tecnologia | Observação |
|--------|-----------|------------|
| Linguagem | Python 3.13 | Versão disponível no ambiente local; confirmação final em DEV-02 |
| Framework | Django 5.2 LTS | Aplicação monolítica com renderização no servidor. Versão 5.2.18 fixada em `requirements.txt` (DEV-02) |
| Interface | Django Templates + Bootstrap | HTML, CSS e JavaScript leve; responsiva |
| Autenticação | Django Auth | Apenas funcionários; contas criadas pelo administrador; sem cadastro público nem recuperação de senha por e-mail |
| Banco de dados | PostgreSQL | Hospedagem planejada no **Neon** |
| Hospedagem | **Render** | Planejada para DEV-08 |
| Valores monetários | `Decimal` / `DecimalField` | Duas casas decimais; nunca `float` |
| Fuso operacional | `America/Recife` | "Data atual" e datas de negócio sempre no fuso local, nunca o dia UTC |

### Compatibilidade Django × Python 3.13

Consulta à documentação oficial do Django em 01/11/2026 ([FAQ de instalação](https://docs.djangoproject.com/en/dev/faq/install/) e [página de download](https://www.djangoproject.com/download/)). Séries com suporte oficial ativo que aceitam Python 3.13:

| Série | Suporte estendido até |
|-------|------------------------|
| 5.2 LTS | abril de 2028 |
| 6.0 | abril de 2027 |
| 6.1 | dezembro de 2027 |

Escolha em DEV-02 (02/11/2026): série **5.2 LTS**, versão **5.2.18**, a mais recente da série na página oficial de download e no PyPI nessa data.

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

- Decisões I1–I5 (aluguel com retirada futura, correção de registros, reativação inválida, prioridades, armazenamento do CPF) foram aprovadas em 01/11/2026. O detalhamento está no Jira e no Documento de Requisitos v1.1 e deve ser considerado na modelagem antes da implementação.
- Estrutura de apps Django: proposta no contrato DEV-01, ainda sem aceite. Versão do Django, runner de testes (padrão do Django) e ferramentas de qualidade (`ruff` e `black`) definidos em DEV-02. Validação em PostgreSQL pendente (`docs/postgresql-local.md`).
