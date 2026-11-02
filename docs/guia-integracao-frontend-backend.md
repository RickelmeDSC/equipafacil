# EquipaFácil — Guia de Integração Frontend ↔ Backend

**Versão:** 1.0 — alinhamento pré-implementação  
**Data:** 01/11/2026  
**Status:** Proposta de contrato para leitura e validação conjunta de Rickelme e Raphael; **não é contrato técnico já implementado**.  
**Referências:** Documento de Requisitos v1.1 (01/11/2026); especificação técnica v3 e decisões I1–I5 aprovadas no Jira EQF.  
**Jira:** https://rickelmepe.atlassian.net/jira/software/projects/EQF/boards/2  
**Repositório:** https://github.com/RickelmeDSC/equipafacil

## Acordo operacional confirmado por mensagem (02/11/2026)

Raphael confirmou que fará seu trabalho **em uma branch separada** e que, depois, Rickelme fará a **auditoria antes de qualquer merge**. Esse acordo confirma o fluxo Git, **não** constitui aceite dos nomes propostos de URLs, variáveis de contexto ou templates. Rickelme também orientou Raphael a ler o repositório antes de trabalhar e a avisar ao finalizar seus commits.

**Rotina combinada:** (1) ler o repositório e este guia; (2) abrir branch `feat/frontend-eqf-NN-*` na base acordada; (3) implementar só o escopo frontend aprovado; (4) criar commits e comunicar Rickelme; (5) abrir PR apenas quando alinhado; (6) Rickelme audita e revisa antes de autorizar merge. O merge **não é automático**. Os dois devem observar a proteção de `main` e evitar conflito com o PR #1 aberto.

## 1. Objetivo deste guia

Garantir que Rickelme (backend) e Raphael (frontend) consigam desenvolver em paralelo, com um único projeto Django, sem criar contratos incompatíveis nem sobrescrever arquivos um do outro.

**Regra principal:** o frontend usa **Django Templates + Bootstrap + HTML/CSS/JavaScript leve**. Não criar aplicação React, Next.js, API REST independente ou infraestrutura separada sem nova decisão explícita.

O documento acadêmico de Requisitos v1.1 ainda aguarda validação final de Rafael e Ivisson. Em caso de conflito entre este guia e os requisitos, não implementar a divergência; registrar a dúvida e decidir em conjunto.

## 2. Responsabilidades

| Responsável | É dono de | Deve consultar o outro antes de |
|---|---|---|
| **Rickelme (backend)** | Projeto Django, configuração, models, migrations, formulários/validações, services, views, URLs efetivas, autenticação/autorização, consultas, testes de regras de negócio, PostgreSQL e deploy | Alterar nomes de rotas, nomes de campos, contexto ou contratos usados em templates |
| **Raphael (frontend)** | Templates HTML, layout Bootstrap, componentes visuais, CSS, JavaScript de interação não sensível, responsividade, acessibilidade básica e mensagens ao usuário | Criar ou alterar views, models, forms, migrations, URLs de backend e regras de negócio |
| **Ambos** | Revisão de PRs, demonstração integrada, consistência da navegação e critérios de aceite visuais | Mudar requisitos, criar dependências, ampliar escopo ou assumir funcionalidade ainda não acordada |

A equipe de Testes (Alexandre/Vinícius) mantém os cenários Gherkin CT01–CT16; o desenvolvimento implementa o comportamento definido, não muda os testes silenciosamente para fazer o código passar.

## 3. Escopo de telas para Raphael

| Tela | Comportamento de interface esperado | RF |
|---|---|---|
| Login | Campos de usuário e senha; indicação de falha; navegação protegida | Requisito transversal (D1) |
| Layout-base | Menu, cabeçalho, feedback de sucesso/erro, área de conteúdo, estados vazios, adaptação mobile | Transversal |
| Equipamentos — listagem | Busca por nome/código, tabela/cartões com categoria, diária, ativo/inativo, disponível/indisponível; estado vazio | RF002 |
| Equipamentos — cadastro | Nome, código, categoria fixa, valor de diária, descrição opcional; exibir erros do Django Form | RF001 |
| Equipamentos — edição | Mesmos campos; indicar código bloqueado após histórico; não prometer edição retroativa | RF003 |
| Equipamentos — ações | Confirmação de exclusão, inativação ou reativação quando permitidas; mensagens de bloqueio | RF004 |
| Clientes — listagem/detalhe | Busca/navegação se prevista no contrato; exibir dados e estado vazio | RF005 |
| Clientes — cadastro/edição | Nome completo, CPF, telefone opcional, e-mail opcional; máscaras apenas visuais | RF005 |
| Aluguéis — registro | Seleção de cliente/equipamento disponível, retirada, devolução prevista, resumo da quantidade de diárias e do valor **servido pelo backend** | RF006 |
| Devolução | Identificar aluguel ativo, informar data real, confirmação e resultado com atraso sem multa | RF007 |
| Histórico | Listagem de cliente/equipamento/datas/diária contratada/total/status; mensagem para lista vazia | RF008 |

**Não incluir na v1:** cadastro público, recuperação de senha por e-mail, cobrança, multa, manutenção, WhatsApp/SMS, exclusão de clientes, edição/cancelamento de aluguéis ou devoluções já registrados.

## 4. Regras funcionais que o frontend deve refletir — sem duplicar validação no cliente

1. **Equipamentos:** categorias fixas: Ferramentas, Equipamentos Audiovisuais, Informática, Construção Civil, Outros. Diária estritamente maior que R$ 0,00 com duas casas decimais. Equipamento recém-criado fica ativo.
2. **Disponibilidade:** disponível apenas quando o equipamento está ativo **e** não tem aluguel ativo. Não criar checkbox/campo manual de disponibilidade; usar resultado do backend.
3. **Imutabilidade:** código do equipamento e CPF do cliente ficam imutáveis após o primeiro aluguel associado. O bloqueio real acontece no backend; o frontend apenas o comunica.
4. **Clientes:** CPF válido e único. Entrada com ou sem pontos/hífen; backend normaliza, armazena **11 dígitos**, aplica dígitos verificadores e fornece exibição formatada. Telefone com DDD é opcional, 10 ou 11 dígitos; e-mail opcional e validado.
5. **Aluguéis (I1):** retirada **hoje ou no futuro**, nunca no passado, no calendário `America/Recife`. Ao registrar aluguel futuro, o equipamento fica indisponível **imediatamente**. **Não existe cancelamento** nessa versão; destacar isso antes de confirmar quando relevante.
6. **Diárias e valor:** diárias inclusivas = `(devolução prevista − retirada) + 1`; valor contratado = diárias × diária do equipamento no registro. O backend calcula e congela o valor decimal. Qualquer prévia em JS é apenas informativa e nunca fonte da verdade.
7. **Devoluções:** data real entre a retirada e a data atual local; somente uma devolução por aluguel ativo. O atraso gera indicação visual, **sem multa**. Devolução registrada não pode ser editada (I2).
8. **Exclusão/inativação:** equipamento sem histórico pode ser excluído após confirmação; com histórico, apenas inativado quando sem aluguel ativo; com aluguel ativo, não excluir nem inativar. Reativação validada no backend (I3).
9. **Histórico:** status Ativo, Atrasado, Encerrado e Encerrado com atraso; mostrar estado vazio corretamente (CT16).
10. **Autenticação:** somente funcionários com conta criada administrativamente e Django Auth. Nunca disponibilizar fluxo público de cadastro. A contagem acadêmica de oito RFs ainda depende da confirmação do professor.

**Segurança:** máscara, campo desabilitado, `required`, limites de data no navegador e remoção de botões são somente UX, não garantias de autorização ou integridade. O servidor sempre revalida.

## 5. Contrato de integração a fechar ANTES de criar as telas finais

Os nomes a seguir são **sugestões** para um documento de contrato assinado por ambos; **não são URLs implementadas nem decisões definitivas**.

### 5.1 Rotas propostas

| Área | Nome Django sugerido (`{% url ... %}`) | Método/uso pretendido |
|---|---|---|
| Login | `accounts:login` | GET/POST |
| Logout | `accounts:logout` | POST |
| Equipamentos | `equipamentos:lista` | GET |
| Cadastro equipamento | `equipamentos:criar` | GET/POST |
| Edição equipamento | `equipamentos:editar` | GET/POST |
| Ações equipamento | `equipamentos:excluir`, `equipamentos:inativar`, `equipamentos:reativar` | POST para mutações; GET de confirmação se necessário |
| Clientes | `clientes:lista`, `clientes:detalhe`, `clientes:criar`, `clientes:editar` | GET e/ou GET/POST |
| Aluguel | `alugueis:criar` | GET/POST |
| Devolução | `alugueis:devolver` | GET/POST |
| Histórico | `alugueis:historico` | GET |

**Pendente:** o backend deve publicar a tabela final contendo `namespace`, `name`, parâmetros (`pk` ou outro), métodos, URL e a view responsável. Raphael deve usar `{% url %}` em vez de caminhos hardcoded.

### 5.2 Contexto e formulários propostos

**Padrões recomendados, sujeitos à validação do backend:**

- Listas: `object_list` ou nome acordado; `query`, `page_obj` quando houver paginação; `empty_message` para estado vazio.
- Detalhes: `object` ou nome acordado.
- Formulários: `form` como instância de Django Form/ModelForm, com `form.non_field_errors` e erros por campo.
- Mensagens: framework de mensagens do Django (`messages`) para sucesso, atenção e erro.
- Rotulagem dos status: propriedades/choices exibidos pelo backend, não lógica de datas duplicada em JavaScript.
- Valores: formatar exibição em BRL sem fazer cálculos autoritativos no template.

**Pendente:** Rickelme confirma os nomes reais das variáveis, campos de formulários, estados de disponibilidade/status, URLs e redirecionamentos antes de Raphael implementar cada tela. Uma tela não deve depender de `context` suposto.

### 5.3 Templates e organização proposta

```text
templates/
  base.html
  includes/
    navbar.html
    messages.html
    form_errors.html
  registration/
    login.html
  equipamentos/
    lista.html
    formulario.html
    confirmar_exclusao.html
  clientes/
    lista.html
    detalhe.html
    formulario.html
  alugueis/
    formulario.html
    devolver.html
    historico.html
static/
  css/
    app.css
  js/
    app.js
```

Nomes e estrutura são **proposta para alinhar a integração**, não obrigação de recriar os arquivos antes de combinar com Rickelme. Evitar misturar `templates/` de app e globais sem acordo explícito.

### 5.4 Regras de formulários

- Todos os formulários que alteram dados devem utilizar `{% csrf_token %}` e método HTTP adequado.
- Renderizar valores e mensagens com escaping padrão do Django; não usar `|safe` com entrada do usuário.
- Mostrar erros do backend (campo e formulário) sem transformar erros em mensagens genéricas.
- Em POST inválido, preservar dados submetidos quando seguro.
- Ações destrutivas exigem confirmação explícita; não executar exclusão por link GET.
- Não adicionar scripts CDN ou dependências externas sem acordo e avaliação de conectividade/deploy.

## 6. Divisão de arquivos para evitar conflitos

| Área/arquivo | Responsável principal |
|---|---|
| `config/`, `*/models.py`, `*/forms.py`, `*/services.py`, `*/views.py`, `*/urls.py`, migrations, testes de domínio | Rickelme |
| `templates/**`, `static/css/**`, `static/js/**` | Raphael |
| `CLAUDE.md`, `.claude/**`, `docs/arquitetura-planejada.md`, dependências e deploy | Rickelme, com revisão de Raphael quando afetar a interface |
| `docs/contrato-frontend-backend.md` (documento de contrato após acordo) | Ambos, com alterações revisadas |

Se o frontend precisar de campo/contexto/rota diferente, abrir solicitação com exemplo de tela e uso. **Não editar backend para “fazer a página funcionar” sem coordenação.** De modo equivalente, o backend não deve renomear contratos consumidos sem avisar Raphael.

## 7. Fluxo de Git e Pull Requests

- `main` está protegida e exige PR e aprovação; sem push direto, force push ou exclusão.
- Rickelme trabalha em branches `feat/backend-eqf-NN-*`; Raphael em `feat/frontend-eqf-NN-*`; documentação em `docs/*`.
- Um PR por entrega lógica, com descrição do RF/CT afetado, prints quando houver interface e comandos de teste.
- Nunca misturar trabalho da branch `docs/alinhamento-workspace` ou do PR #1 em outra branch por acidente.
- Antes de abrir PR: atualizar branch de forma não destrutiva e conferir diff/arquivos alterados; resolver conflitos em conjunto.
- Não fazer merge sem revisão humana; usar exceção administrativa apenas por decisão explícita e registrada.
- Não publicar `.env`, credenciais, banco local, dados de clientes ou arquivos acadêmicos não autorizados no repositório público.

## 8. Sequência de trabalho acordável

**Etapa 0 — Agora:** Raphael lê este guia, confere Requisitos v1.1 no Jira e sinaliza dúvidas. Rickelme prepara a fundação Django em branch independente.

**Etapa 1 — Contrato:** Rickelme publica o contrato real de rotas, forms, contexto, nomes de templates e autenticação; Raphael aprova ou pede ajustes. *Sem essa etapa, criar apenas wireframes/HTML estático sem suposições de integração.*

**Etapa 2 — Frontend:** Raphael implementa `base.html`, navegação, login, listas, formulários, detalhe de cliente, devolução e histórico conforme contrato; faz revisão responsiva e de acessibilidade.

**Etapa 3 — Integração:** ambos verificam cenários CT01–CT16 com QA; corrigem incompatibilidades sem reescrever as regras de negócio.

**Etapa 4 — Finalização:** revisão cruzada, smoke test no ambiente integrado, documentação de execução e deploy apenas quando autorizado.

## 9. Checklist para Raphael antes do primeiro PR

- [ ] Li RF001–RF008, RN001–RN004 e as limitações I1/I2 do Documento de Requisitos v1.1.
- [ ] Confirmei com Rickelme os nomes de URL, variáveis de contexto, campos de forms e templates utilizados.
- [ ] Minha branch foi criada a partir da base combinada; não editei models, migrations nem views do backend.
- [ ] As telas são responsivas, com labels visíveis, navegação por teclado e mensagens de erro claras.
- [ ] Uso `{% csrf_token %}`, `{% url %}` e escaping padrão do Django.
- [ ] Disponibilidade, datas e valores apresentados vêm das respostas do backend.
- [ ] Tratei estados vazios (CT04 e CT16) e exibição de bloqueios de ação.
- [ ] Não incluí funcionalidades fora do escopo ou credenciais.
- [ ] Incluí capturas de tela ou evidência visual no PR, além de instruções para testar.
- [ ] Solicitei revisão cruzada antes de integrar.

## 10. Pendências para validação conjunta

1. **URLs e names finais:** validar após DEV-01/DEV-02, antes de templates finais.
2. **Campos reais dos Forms e contexto:** definir com exemplos de GET/POST e estados de erro.
3. **Convenção de templates e layout:** aprovar os diretórios sugeridos.
4. **Fluxo de autenticação:** URLs e tela de login; professor ainda precisa confirmar a classificação como transversal.
5. **Identidade GitHub de Raphael:** username confirmado e convite `Write` aceito.
6. **PR #1 documental:** integrar após revisão, sem depender disso para rascunhar a interface, mas sem perder as regras de segurança.
7. **Modelo acadêmico final e testes Gherkin:** acompanhar a validação da documentação até 03/11.

---

**Aceite do guia (não é aprovação automática):**

- Rickelme — leitura e aprovação do contrato: **pendente**.
- Raphael — leitura, dúvidas e aprovação do contrato: **pendente**.

**Princípio de controle:** nenhum nome de URL, campo, contexto ou comportamento novo fica “aprovado por silêncio”. Registrar o acordo em `docs/contrato-frontend-backend.md` ou em comentário de PR antes de depender dele na implementação.
