# EquipaFácil — Sistema de Aluguel de Equipamentos

> **Situação:** em planejamento. **O sistema ainda não foi implementado.** Este repositório contém apenas a estrutura documental inicial; nenhuma funcionalidade descrita abaixo está disponível ou em funcionamento.

Sistema acadêmico de gestão de aluguel de equipamentos, desenvolvido com Python/Django e PostgreSQL.

## Objetivo

Oferecer a funcionários autenticados de uma locadora uma aplicação web para cadastrar equipamentos e clientes, registrar aluguéis e devoluções e consultar o histórico de locações, com regras de disponibilidade, datas e valores verificadas no backend.

## Contexto acadêmico

Projeto em equipe do curso de Análise e Desenvolvimento de Sistemas (ADS) da UNIBRA. O trabalho é dividido entre as equipes de Requisitos, Desenvolvimento e Testes de Software, e o planejamento funcional é acompanhado no Jira.

A especificação funcional vigente é a **v3**, com decisões técnicas aprovadas, mas **a documentação acadêmica ainda aguarda revisão** das equipes de Requisitos e de Testes. Ela é uma referência provisória e pode mudar.

## Funcionalidades planejadas

| ID | Requisito funcional | Prioridade |
|----|---------------------|------------|
| RF001 | Cadastrar equipamentos | Alta |
| RF002 | Consultar e pesquisar equipamentos | Alta |
| RF003 | Editar informações de equipamentos | Alta |
| RF004 | Excluir, inativar ou reativar equipamentos | Alta |
| RF005 | Cadastrar, listar, consultar e editar clientes | Alta |
| RF006 | Registrar aluguel | Alta |
| RF007 | Registrar devolução | Alta |
| RF008 | Consultar histórico de aluguéis | Média |

Regras de negócio planejadas: RN001 (aluguéis simultâneos e disponibilidade), RN002 (validação de dados), RN003 (integridade e exclusão/inativação) e RN004 (datas, duração e valores). Detalhes e rastreabilidade em [`docs/rastreabilidade.md`](docs/rastreabilidade.md).

Requisito técnico transversal: acesso restrito a funcionários autenticados (Django Auth), sem cadastro público.

## Tecnologias previstas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python, Django |
| Frontend | Django Templates, Bootstrap, HTML, CSS, JavaScript |
| Banco de dados | PostgreSQL (hospedagem prevista no Neon) |
| Hospedagem | Render (previsto) |
| Gestão | Jira (Kanban), GitHub |

Nada disso está configurado ainda. Veja [`docs/arquitetura-planejada.md`](docs/arquitetura-planejada.md).

## Equipes

| Equipe | Integrantes | Responsabilidades |
|--------|-------------|-------------------|
| Requisitos | Rafael Ferreira, Ivisson | Documento de requisitos (RF, RN), revisão e validação acadêmica |
| Desenvolvimento | Rickelme David | Backend Django, banco de dados, regras de negócio, autenticação, integração, infraestrutura e deploy, coordenação técnica |
| Desenvolvimento | Raphael Eloi | Frontend (Django Templates, Bootstrap), responsividade e apresentação de dados e mensagens |
| Testes de Software | Alexandre Abreu, Vinícius Soares | 16 cenários Gherkin (CT01–CT16), execução de testes e registro de defeitos |

## Situação atual

- [x] Planejamento no Jira (especificação v3)
- [x] Repositório e documentação inicial
- [ ] Revisão acadêmica dos requisitos e cenários de teste
- [ ] Configuração do projeto Django
- [ ] Implementação de RF001–RF008
- [ ] Testes e demonstração
- [ ] Deploy

## Prazos

| Entrega | Data |
|---------|------|
| Primeira entrega (requisitos, regras de negócio, cenários Gherkin e Jira) | 03/11/2026 |
| Entrega final do sistema | 15/11/2026 |

## Jira

Planejamento, atividades e especificação v3: [Quadro EQF no Jira](https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2) (acesso restrito aos membros do projeto).

## Como colaborar

1. Não faça commits diretamente na `main`. Crie uma branch a partir dela (`feat/…`, `fix/…`, `docs/…`).
2. Use [commits semânticos](https://www.conventionalcommits.org/pt-br/) em português, por exemplo `feat: adiciona cadastro de equipamentos`.
3. Abra um Pull Request usando o template, citando a atividade do Jira (ex.: `EQF-16`) e os RF/RN/CT relacionados.
4. Todo PR precisa de revisão antes do merge.
5. Implemente apenas requisitos aprovados na especificação vigente; dúvidas de escopo vão para o Jira.
6. **Nunca** publique senhas, tokens, arquivos `.env` ou dados reais de pessoas. Use `.env.example` com valores fictícios.

## Licença

Projeto acadêmico, sem licença de uso definida até o momento.
