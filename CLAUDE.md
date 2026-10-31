# CLAUDE.md — EquipaFácil

Instruções para sessões do Claude Code neste repositório. Leia antes de qualquer alteração.

## Contexto

EquipaFácil é um sistema web acadêmico (ADS/UNIBRA) de gestão de aluguel de equipamentos, usado por funcionários autenticados de uma locadora: equipamentos, clientes, aluguéis, devoluções e histórico.

- Planejamento: Jira, projeto `EQF` — https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2
- **Especificação funcional v3** (épicos EQF-4 Requisitos, EQF-5 Desenvolvimento, EQF-6 Testes) é a referência **provisória**: decisões técnicas aprovadas, documentação acadêmica ainda em revisão. Resumo em `docs/rastreabilidade.md`.
- Inconsistências I1–I5 da v3 e suas propostas estão **pendentes de aprovação**. Não as trate como decididas.
- Prazos: primeira entrega 03/11/2026; entrega final 15/11/2026.

## Estado atual

Repositório apenas com documentação. **Django ainda não foi iniciado.** Não crie aplicação, models, views, forms, templates, migrations, dependências, banco Neon, configuração no Render nem deploy, a menos que a tarefa da sessão autorize explicitamente.

## Stack definida

- Python + **Django** (framework definido; não sugerir troca).
- Django Templates + Bootstrap no frontend (sem SPA).
- PostgreSQL (Neon previsto); Render previsto para hospedagem.
- Django Auth para autenticação (sem cadastro público, sem recuperação de senha por e-mail).

## Responsabilidades

| Pessoa / equipe | Papel |
|-----------------|-------|
| Rickelme David | Backend, banco de dados, regras RN001–RN004, autenticação, fuso, integração, infraestrutura, deploy, revisão técnica |
| Raphael Eloi | Frontend: templates, Bootstrap, HTML/CSS/JS, responsividade, exibição de estados e mensagens vindas do backend |
| Requisitos (Rafael Ferreira, Ivisson) | Validação acadêmica dos RF/RN |
| Testes (Alexandre Abreu, Vinícius Soares) | Validação acadêmica dos cenários CT01–CT16 e execução dos testes |

Mudanças no contrato frontend × backend devem ser combinadas entre Rickelme e Raphael antes de implementar.

## Regras de domínio que não podem ser violadas

- Toda regra e todo cálculo ficam no **backend**; campo somente leitura na tela não substitui validação no servidor.
- Valores monetários com `DecimalField`/`Decimal`, duas casas — **nunca `float`**.
- "Data atual" sempre no fuso `America/Recife`, nunca o dia UTC.
- Disponibilidade é **derivada** (ativo e sem aluguel ativo); não criar campo manual.
- No máximo um aluguel ativo por equipamento, com proteção contra concorrência.
- Diárias inclusivas: `(prevista − retirada) + 1`; valor contratado congelado no registro.
- Categorias fixas: Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil, Outros.

## Escopo

- Implemente apenas requisitos aprovados na especificação vigente (RF001–RF008, RN001–RN004 e decisões D1–D9, N2–N6, D8, TZ).
- Não invente requisitos, campos, telas ou integrações (ex.: multa, WhatsApp, reservas, pagamentos).
- Ambiguidade de requisito → pare e pergunte; registre a dúvida para o Jira em vez de decidir sozinho.
- Não altere atividades do Jira sem pedido explícito.

## Convenções de código Python

- PEP 8, formatação com `black` e lint com `ruff` (quando o projeto for configurado).
- Nomes de domínio em português, coerentes com a especificação (`Equipamento`, `Cliente`, `Aluguel`); código Python em `snake_case`, classes em `PascalCase`.
- Type hints em funções de serviço; regras de negócio em camada de serviço/model, não em views ou templates.
- Mensagens ao usuário em português, conforme a tabela de mensagens do épico EQF-5.

## Testes

- Nenhuma funcionalidade é considerada concluída sem testes automatizados passando (`python manage.py test` ou `pytest`, conforme definido em DEV-02).
- Relacione testes aos cenários `CTxx` e às coberturas complementares `FCxx`.
- Datas em testes devem ser relativas à data atual em `America/Recife`.

## Git e revisão

- Commits semânticos em português: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Uma branch por atividade (`feat/eqf-16-crud-equipamentos`); nunca commitar direto na `main`.
- PR com o template do repositório, citando a atividade Jira e os RF/RN/CT.
- **Revisão humana obrigatória antes de merge e antes de qualquer deploy.** Não fazer merge, force push ou deploy por conta própria.

## Segurança

- Nunca publicar credenciais (GitHub, Jira, Neon, Render, `SECRET_KEY`, URLs de banco com senha).
- Configuração por variáveis de ambiente; apenas `.env.example` com valores fictícios entra no Git.
- Não versionar dados reais de clientes (CPF, telefone, e-mail). Usar dados fictícios em fixtures.
- Não publicar documentos originais do professor nem dados pessoais da equipe sem avaliação prévia.
- Se encontrar um segredo commitado, pare e avise: ele deve ser revogado, não apenas removido.
