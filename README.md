# EquipaFácil — Sistema de Aluguel de Equipamentos

> **Situação:** em planejamento. **O sistema ainda não foi implementado.** Este repositório contém apenas a estrutura documental inicial; nenhuma funcionalidade descrita abaixo está disponível ou em funcionamento.

Sistema acadêmico de gestão de aluguel de equipamentos, desenvolvido com Python/Django e PostgreSQL.

## Objetivo

Oferecer a funcionários autenticados de uma locadora uma aplicação web para cadastrar equipamentos e clientes, registrar aluguéis e devoluções e consultar o histórico de locações, com regras de disponibilidade, datas e valores verificadas no backend.

## Contexto acadêmico

Projeto em equipe do curso de Análise e Desenvolvimento de Sistemas (ADS) da UNIBRA. O trabalho é dividido entre as equipes de Requisitos, Desenvolvimento e Testes de Software, e o planejamento funcional é acompanhado no Jira.

### Referências

| Referência | Papel | Situação |
|------------|-------|----------|
| Especificação técnica v3 (Jira, épicos EQF-4, EQF-5 e EQF-6) | Referência de planejamento | Vigente |
| Documento de Requisitos v1.1 | Documento acadêmico | Revisado tecnicamente; validação acadêmica final aguardando Rafael Ferreira e Ivisson. Não é publicado neste repositório |
| Decisões I1–I5 | Ajustes da especificação | Aprovadas por Rickelme David em 01/11/2026 |

A especificação v3 e o Documento de Requisitos v1.1 não são versões concorrentes do mesmo arquivo: a primeira organiza o planejamento no Jira; o segundo é o documento acadêmico de requisitos.

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
| Backend | Python 3.13, Django (versão definida em DEV-02) |
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

- [x] Planejamento no Jira (especificação técnica v3)
- [x] Repositório e documentação inicial
- [x] Revisão técnica do Documento de Requisitos v1.1 e aprovação das decisões I1–I5
- [ ] Validação acadêmica final dos requisitos (Rafael Ferreira e Ivisson)
- [ ] Revisão dos cenários de teste (equipe de Testes)
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

Planejamento, atividades e especificação técnica v3: [Quadro EQF no Jira](https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2) (acesso restrito aos membros do projeto).

## Como colaborar

### Branches

| Branch | Uso |
|--------|-----|
| `main` | Versão integrada e revisada. Protegida: só recebe alterações por Pull Request |
| `docs/<descricao>` | Documentação |
| `feat/backend-eqf-NN-<descricao>` | Backend, banco e regras de negócio (ex.: `feat/backend-eqf-16-equipamentos`) |
| `feat/frontend-eqf-NN-<descricao>` | Templates, estilos e interface (ex.: `feat/frontend-eqf-16-equipamentos`) |
| `fix/eqf-NN-<descricao>` | Correções |

`NN` é o número da atividade no Jira. Crie a branch a partir da `main` atualizada e nunca faça commits diretamente na `main`.

### Fluxo de qualidade

1. **Planejamento antes da implementação:** confirme a atividade do Jira, os RF/RN/CT envolvidos e, se houver tela, o contrato frontend × backend.
2. **Testes automatizados** vinculados aos RF e aos cenários CT; nenhuma funcionalidade é concluída sem testes passando.
3. **Commits semânticos** em português ([Conventional Commits](https://www.conventionalcommits.org/pt-br/)), por exemplo `feat: adiciona cadastro de equipamentos`.
4. **Verificação de segurança** antes de cada commit e PR: revise o diff e confirme que não há segredos, `.env` ou dados reais.
5. **Pull Request** com o template, citando a atividade do Jira (ex.: `EQF-16`) e os RF/RN/CT relacionados.
6. **Code review** humano antes do merge.
7. **Alterações de requisitos** passam por revisão humana das equipes responsáveis e são registradas no Jira; implemente apenas requisitos aprovados.
8. **Deploy** somente após autorização explícita do responsável técnico (Rickelme David).

**Nunca** publique senhas, tokens, arquivos `.env` ou dados reais de pessoas. Use `.env.example` com valores fictícios.

## Licença

Projeto acadêmico, sem licença de uso definida até o momento.
