# Contrato técnico frontend × backend — EquipaFácil

> **RASCUNHO PROVISÓRIO — PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.1 — 01/11/2026. **Nada aqui está implementado**: não existe projeto Django, URL, view, formulário ou template no repositório. Raphael **não aprovou** nenhum nome de rota, campo, variável ou template deste documento.
>
> **Limitação:** a auditoria do Jira (Tarefa 08A-WEB) não foi concluída. Não foram conferidos os critérios oficiais de DEV-01 (EQF-13), DEV-02 (EQF-14) e DEV-03 (EQF-15) nem a tabela de mensagens do épico EQF-5. **Todos os textos de mensagem são provisórios.** Itens marcados **[verificar]** dependem dessa conferência.
>
> **Relação com o guia:** este documento detalha a seção 5 do [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md) (branch `docs/guia-integracao-raphael`) e **não o substitui**. As diferenças estão listadas na seção 9.

Documentos relacionados: [modelagem proposta](modelagem-proposta.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

## 1. Legenda de situação

| Marcação | Significado |
|----------|-------------|
| **Aprovado** | Consta da especificação técnica v3, do resumo em [`rastreabilidade.md`](rastreabilidade.md) ou das decisões I1–I5 |
| **Proposta** | Sugestão técnica de Rickelme, ainda não validada |
| **Decisão conjunta** | Precisa do acordo de Rickelme e Raphael antes de implementar |
| **Depende de implementação** | Só será confirmado quando o código existir (DEV-02 em diante) |

## 2. Arquitetura proposta

Um único projeto Django com renderização no servidor. Sem API REST, sem endpoints JSON e sem framework de frontend (**Aprovado**: Django Templates + Bootstrap).

| Parte | Nome proposto | Conteúdo | Situação |
|-------|---------------|----------|----------|
| Projeto | `config` | `settings.py`, `urls.py`, `wsgi.py`, `asgi.py` | Proposta |
| Início | app `core`, namespace `core` | Página inicial (P01) e utilidades compartilhadas do backend | Proposta |
| Equipamentos | app `equipamentos`, namespace `equipamentos` | RF001–RF004 | Proposta |
| Clientes | app `clientes`, namespace `clientes` | RF005 | Proposta |
| Aluguéis | app `alugueis`, namespace `alugueis` | RF006–RF008 (aluguel, devolução e histórico) | Proposta |
| Autenticação | **sem app própria**: views do `django.contrib.auth`, nomes `login` e `logout` sem namespace | Login e logout (D1) | Decisão conjunta |
| Templates | diretório global `templates/` | Todas as páginas | Proposta (alinhada ao guia) |
| Estáticos | `static/css/`, `static/js/`, `static/vendor/bootstrap/` | CSS, JS e Bootstrap 5.3 local | Decisão conjunta |

**Por que não criar app de autenticação:** login e logout usam `LoginView` e `LogoutView` do Django sem código próprio, e as contas são criadas pelo administrador (D1). Isso resolve a decisão pendente do guia (`accounts` ou `usuarios`) sem criar app nova — mas **depende do acordo de Raphael**.

**Proteção das rotas (Aprovado: login obrigatório):** proposta de usar `LoginRequiredMiddleware`, disponível em todas as séries do Django compatíveis com Python 3.13 listadas na arquitetura. Assim toda página exige login, exceto `login`, marcada como pública. Usuário não autenticado é levado a `login` com `?next=`.

**Criação de contas de funcionário (D1):** feita pelo administrador, sem cadastro público nem recuperação de senha por e-mail. Mecanismo proposto: `createsuperuser` e o Django Admin restrito ao cadastro de usuários, **sem** registrar `Equipamento`, `Cliente` e `Aluguel` para edição livre. **[verificar]** o critério oficial de D1 no Jira.

## 3. Convenções gerais

1. **GET** só lê dados. Toda alteração usa **POST** com `{% csrf_token %}`.
2. **POST bem-sucedido redireciona** (padrão POST/redirect/GET) e mostra a mensagem pelo framework `messages` do Django.
3. **POST inválido** devolve a mesma página (HTTP 200) com o formulário preenchido e os erros.
4. Recurso inexistente (`pk` inválido) retorna **404**; método não permitido retorna **405**.
5. Todo cálculo (disponibilidade, diárias, valores, situação, atraso) vem pronto do backend. O template só exibe.
6. Mensagens usam os níveis `success`, `warning` e `error`. O backend mapeia `error` para a classe `danger` do Bootstrap (`MESSAGE_TAGS`).
7. Datas são exibidas como `dd/mm/aaaa` e valores como `R$ 1.500,00`, pela localização `pt-br` do Django, sem cálculo no template.
8. Variáveis padrão do Django ficam em inglês (`object_list`, `object`, `form`, `page_obj`), por convenção do framework; atributos de domínio ficam em português (`disponivel`, `pode_excluir`).

## 4. Contrato de rotas

Todas as rotas são **Proposta**; caminhos e nomes dependem de **decisão conjunta**. Todas exigem login, exceto a de login.

| Funcionalidade | Método | Caminho sugerido | Nome da URL | View responsável | Template | Dados de entrada | Redirecionamento após sucesso | Vazio ou erro |
|----------------|--------|------------------|-------------|------------------|----------|------------------|-------------------------------|---------------|
| Login (D1) | GET, POST | `/login/` | `login` | `LoginView` (Django) | `registration/login.html` | `username`, `password`, `next` | `next` ou `core:inicio` | Credenciais inválidas: mesma página com erro |
| Logout (D1) | POST | `/logout/` | `logout` | `LogoutView` (Django) | — | Só CSRF | `login` | GET retorna 405 |
| Início (P01) | GET | `/` | `core:inicio` | `InicioView` | `inicio.html` | — | — | — |
| Listar e pesquisar equipamentos (RF002) | GET | `/equipamentos/` | `equipamentos:lista` | `EquipamentoListView` | `equipamentos/lista.html` | `?q=` (nome ou código) | — | Sem resultados: `empty_message` (CT04) |
| Cadastrar equipamento (RF001) | GET, POST | `/equipamentos/novo/` | `equipamentos:criar` | `EquipamentoCreateView` | `equipamentos/formulario.html` | `EquipamentoForm` | `equipamentos:detalhe` | Erros de validação no formulário (CT02) |
| Detalhes e ações do equipamento (RF002, RF004 — P04) | GET | `/equipamentos/<int:pk>/` | `equipamentos:detalhe` | `EquipamentoDetailView` | `equipamentos/detalhe.html` | `pk` | — | 404 |
| Editar equipamento (RF003) | GET, POST | `/equipamentos/<int:pk>/editar/` | `equipamentos:editar` | `EquipamentoUpdateView` | `equipamentos/formulario.html` | `EquipamentoForm` | `equipamentos:detalhe` | Erros no formulário (CT06) |
| Excluir equipamento (RF004) | GET (confirmação), POST | `/equipamentos/<int:pk>/excluir/` | `equipamentos:excluir` | `EquipamentoExcluirView` | `equipamentos/confirmar_exclusao.html` | Só CSRF | `equipamentos:lista` | Com histórico: volta a `equipamentos:detalhe` com erro (CT08) |
| Inativar equipamento (RF004) | POST | `/equipamentos/<int:pk>/inativar/` | `equipamentos:inativar` | `EquipamentoInativarView` | — | Só CSRF | `equipamentos:detalhe` | Aluguel ativo: volta ao detalhe com erro |
| Reativar equipamento (RF004, I3) | POST | `/equipamentos/<int:pk>/reativar/` | `equipamentos:reativar` | `EquipamentoReativarView` | — | Só CSRF | `equipamentos:detalhe` | Reativação inválida: volta ao detalhe com erro |
| Listar clientes (RF005) | GET | `/clientes/` | `clientes:lista` | `ClienteListView` | `clientes/lista.html` | — | — | Sem clientes: `empty_message` |
| Cadastrar cliente (RF005) | GET, POST | `/clientes/novo/` | `clientes:criar` | `ClienteCreateView` | `clientes/formulario.html` | `ClienteForm` | `clientes:detalhe` | Erros no formulário (CT10) |
| Consultar cliente (RF005) | GET | `/clientes/<int:pk>/` | `clientes:detalhe` | `ClienteDetailView` | `clientes/detalhe.html` | `pk` | — | 404 |
| Editar cliente (RF005) | GET, POST | `/clientes/<int:pk>/editar/` | `clientes:editar` | `ClienteUpdateView` | `clientes/formulario.html` | `ClienteForm` | `clientes:detalhe` | Erros no formulário |
| Listar aluguéis / histórico (RF008) | GET | `/alugueis/` | `alugueis:historico` | `AluguelHistoricoView` | `alugueis/historico.html` | — | — | Sem registros: `empty_message` (CT16) |
| Registrar aluguel (RF006) | GET, POST | `/alugueis/novo/` | `alugueis:criar` | `AluguelCreateView` | `alugueis/formulario.html` | `AluguelForm` e `etapa` | `alugueis:historico` | Indisponível (CT12) ou data inválida: formulário com erro |
| Registrar devolução (RF007) | GET, POST | `/alugueis/<int:pk>/devolver/` | `alugueis:devolver` | `DevolucaoView` | `alugueis/devolver.html` | `DevolucaoForm` | `alugueis:historico` | Já encerrado (CT14): volta ao histórico com erro |

**Fora do contrato:** exclusão de cliente, edição ou cancelamento de aluguel e devolução, cadastro público, recuperação de senha, endpoints JSON e qualquer rota de multa, pagamento ou reserva.

**Pesquisa de clientes:** RF005 fala em listar e consultar, não em pesquisar. Nenhuma pesquisa foi prevista — **[verificar]**.

**Confirmação de inativação e reativação:** só a exclusão tem página de confirmação (CT07). Se inativação e reativação também precisarem de confirmação, ela pode ser um modal do Bootstrap no detalhe, sem rota nova — **decisão conjunta**.

## 5. Contrato dos formulários

Os nomes pedidos na tarefa (EquipmentForm, ClientForm, RentalForm, ReturnForm, LoginForm) foram mapeados para nomes em português, seguindo a convenção de domínio do `CLAUDE.md`. Isso é **Proposta**. **Todos os textos de mensagem são provisórios** até a conferência da tabela do EQF-5.

**Responsabilidade comum a todos:**

- **Backend:** validação, normalização, unicidade, imutabilidade, cálculo e gravação via serviço. Classes do Bootstrap 5.3 aplicadas pelos widgets (`form-control`, `form-select` e `is-invalid` quando há erro), para que Raphael não precise editar `forms.py`.
- **Apresentação (Raphael):** layout, rótulos visíveis, ordem visual, máscaras apenas visuais, exibição de `form.non_field_errors` e dos erros de cada campo, e acessibilidade.

### 5.1 `EquipamentoForm` (pedido: EquipmentForm) — RF001, RF003, RN002

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `nome` | Texto (até 120) | Sim | Não vazio | "Informe o nome do equipamento." |
| `codigo` | Texto (até 30) | Sim | Único; imutável após o primeiro aluguel | "Já existe um equipamento com este código." |
| `categoria` | Seleção (5 opções fixas) | Sim | Valor da lista | "Selecione uma categoria válida." |
| `descricao` | Texto longo | Não | — | — |
| `valor_diaria` | Decimal, 2 casas, aceita vírgula | Sim | Maior que R$ 0,00 | "A diária deve ser maior que R$ 0,00." |

- **Valores iniciais:** formulário vazio no cadastro. `ativo` não aparece no formulário: o equipamento nasce ativo.
- **Imutabilidade:** na edição, se `codigo_editavel` for falso, o campo `codigo` vem desabilitado e o backend ignora qualquer valor enviado.
- **Sucesso (provisório):** "Equipamento cadastrado com sucesso." e "Equipamento atualizado com sucesso."

### 5.2 `ClienteForm` (pedido: ClientForm) — RF005, RN002, I5

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `nome_completo` | Texto (até 150) | Sim | Não vazio | "Informe o nome completo do cliente." |
| `cpf` | Texto, com ou sem máscara | Sim | Normaliza para 11 dígitos; dígitos verificadores; único; imutável após o primeiro aluguel | "CPF inválido." e "Já existe um cliente com este CPF." |
| `telefone` | Texto, com ou sem máscara | Não | Normaliza para dígitos; 10 ou 11 com DDD | "Informe um telefone com DDD (10 ou 11 dígitos)." |
| `email` | E-mail | Não | Formato | "Informe um e-mail válido." |

- **Valores iniciais:** na edição, CPF e telefone são exibidos formatados.
- **Imutabilidade:** se `cpf_editavel` for falso, o campo `cpf` vem desabilitado e o backend ignora o valor enviado.
- **Sucesso (provisório):** "Cliente cadastrado com sucesso." e "Cliente atualizado com sucesso."

### 5.3 `AluguelForm` (pedido: RentalForm) — RF006, RN001, RN004, I1

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `cliente` | Seleção de cliente | Sim | Cliente existente | "Selecione um cliente." |
| `equipamento` | Seleção só de equipamentos disponíveis | Sim | Ativo e sem aluguel ativo, revalidado dentro da transação | "Equipamento indisponível para aluguel." (CT12) |
| `data_retirada` | Data | Sim | Hoje ou no futuro, em `America/Recife` (I1) | "A data de retirada não pode ser anterior à data atual." |
| `data_devolucao_prevista` | Data | Sim | Não anterior à retirada | "A devolução prevista não pode ser anterior à retirada." |

- **Valores iniciais:** `data_retirada` igual à data atual em `America/Recife`.
- **Calculado pelo backend, nunca enviado pelo formulário:** `valor_diaria_contratada`, `quantidade_diarias` e `valor_contratado`.
- **Etapas (Proposta):** campo oculto `etapa` com valor `dados` ou `revisao`. No primeiro envio, o backend valida e devolve a mesma página com o **resumo calculado** e o aviso de que não há cancelamento nesta versão (I1). No envio de confirmação, o backend **revalida tudo**, recalcula e grava. Isso entrega o valor "servido pelo backend" sem endpoint JSON.
- **Sucesso (provisório):** "Aluguel registrado. Valor contratado: R$ 150,00."

### 5.4 `DevolucaoForm` (pedido: ReturnForm) — RF007, I2

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `data_devolucao_real` | Data | Sim | Entre a retirada e a data atual; aluguel ainda ativo | "A data de devolução deve estar entre a retirada e a data atual." e "Este aluguel já foi encerrado." (CT14) |

- **Valores iniciais:** data atual em `America/Recife`.
- **Imutabilidade:** depois de gravada, a devolução não pode ser editada (I2).
- **Sucesso (provisório):** "Devolução registrada." Se houver atraso: "Devolução registrada com atraso." Nunca há multa.

### 5.5 Login (pedido: LoginForm) — D1

Usa o `AuthenticationForm` padrão do Django, sem formulário próprio: campos `username` e `password` e a mensagem de erro padrão traduzida para pt-BR. Sem "lembrar-me", sem "esqueci minha senha" e sem link de cadastro.

## 6. Contrato dos templates

Contexto disponível em todas as páginas: `user`, `messages`, `request` e `csrf_token`. Nomes, diretórios e blocos são **Proposta**, alinhados à seção 5.3 do guia.

| Template | URL | Variáveis de contexto | Formulário | Estados | Ações |
|----------|-----|-----------------------|------------|---------|-------|
| `base.html` | Todas | Globais | — | Autenticado; página de login sem menu | Blocos `title` e `content`; carrega Bootstrap local |
| `includes/navbar.html` | Todas autenticadas | `user` | Logout (POST) | — | Links: Início, Equipamentos, Clientes, Novo aluguel, Histórico; sair |
| `includes/messages.html` | Todas | `messages` | — | Sucesso, atenção, erro | Fechar alerta |
| `includes/form_errors.html` | Páginas com formulário | `form` | — | Com ou sem `non_field_errors` | — |
| `registration/login.html` | `login` | `form`, `next` | `AuthenticationForm` | Inicial; credenciais inválidas | Entrar |
| `inicio.html` | `core:inicio` | `user` | — | — | Atalhos para as áreas (P01) |
| `equipamentos/lista.html` | `equipamentos:lista` | `object_list`, `query`, `empty_message` | Pesquisa (GET `q`) | Com resultados; sem cadastro; pesquisa sem resultado (CT04) | Pesquisar; novo; ver detalhe |
| `equipamentos/formulario.html` | `equipamentos:criar`, `equipamentos:editar` | `form`, `object` (edição), `codigo_editavel` (edição) | `EquipamentoForm` | Cadastro; edição; código bloqueado; erro de validação | Salvar; voltar |
| `equipamentos/detalhe.html` | `equipamentos:detalhe` | `object`, `tem_historico`, `tem_aluguel_ativo`, `pode_excluir`, `pode_inativar`, `pode_reativar` | Inativar e reativar (POST) | Ativo disponível; ativo alugado; inativo | Editar; excluir; inativar; reativar — só os permitidos |
| `equipamentos/confirmar_exclusao.html` | `equipamentos:excluir` | `object` | Confirmação (POST) | — | Confirmar; cancelar |
| `clientes/lista.html` | `clientes:lista` | `object_list`, `empty_message` | — | Com clientes; sem clientes | Novo; ver detalhe |
| `clientes/formulario.html` | `clientes:criar`, `clientes:editar` | `form`, `object` (edição), `cpf_editavel` (edição) | `ClienteForm` | Cadastro; edição; CPF bloqueado; erro | Salvar; voltar |
| `clientes/detalhe.html` | `clientes:detalhe` | `object` | — | — | Editar (sem excluir) |
| `alugueis/formulario.html` | `alugueis:criar` | `form`, `etapa`, `resumo` (na revisão), `sem_equipamentos_disponiveis`, `sem_clientes` | `AluguelForm` | Dados; revisão; erro; nenhum equipamento disponível; nenhum cliente | Revisar; confirmar; voltar |
| `alugueis/devolver.html` | `alugueis:devolver` | `object` (aluguel), `form` | `DevolucaoForm` | Formulário; erro de data | Confirmar devolução; voltar |
| `alugueis/historico.html` | `alugueis:historico` | `object_list`, `empty_message` | — | Com registros; sem registros (CT16) | Registrar devolução quando `pode_devolver` |

**Atributos de domínio disponíveis nos objetos** (calculados no backend; ver a [modelagem](modelagem-proposta.md)):

| Objeto | Atributos para exibição |
|--------|-------------------------|
| Equipamento | `nome`, `codigo`, `get_categoria_display`, `descricao`, `valor_diaria`, `ativo`, `disponivel` |
| Cliente | `nome_completo`, `cpf_formatado`, `telefone_formatado`, `email` |
| Aluguel | `cliente`, `equipamento`, `data_retirada`, `data_devolucao_prevista`, `data_devolucao_real`, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado`, `situacao`, `situacao_codigo`, `pode_devolver` |
| `resumo` (revisão do aluguel) | `cliente`, `equipamento`, `data_retirada`, `data_devolucao_prevista`, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado` |

**Regras de apresentação:**

- Botões de ação só aparecem quando a flag correspondente é verdadeira. O backend revalida tudo mesmo assim.
- `situacao_codigo` (`ativo`, `atrasado`, `encerrado`, `encerrado_com_atraso`) serve só para escolher o estilo do selo; o texto exibido é `situacao`.
- Estados vazios usam `empty_message` dentro de `{% empty %}`, sem tabela vazia nem dados inventados (CT04, CT16).
- Paginação não está prevista na v1. Se for adotada, a variável é `page_obj`.
- Nenhum `|safe` em dado digitado por usuário; nenhum `href` montado à mão: sempre `{% url %}`.

## 7. Divisão de arquivos

Cada arquivo tem **um** responsável. Ninguém edita arquivo do outro.

| Responsável | Arquivos |
|-------------|----------|
| **Rickelme (backend)** | `manage.py`, `config/**`, `*/models.py`, `*/forms.py`, `*/views.py`, `*/urls.py`, `*/services.py`, `*/admin.py`, `*/apps.py`, `*/migrations/**`, `*/tests/**`, dependências, `.env.example`, `CLAUDE.md`, `.claude/**` |
| **Raphael (frontend)** | `templates/**/*.html`, `static/css/**`, `static/js/**`, `static/img/**`, `static/vendor/bootstrap/**` (decisão conjunta) |
| **Ambos, via PR revisado pelos dois** | Este contrato e o guia de integração |

**Procedimento para pedir mudança em arquivo do outro:**

1. Descrever o pedido em comentário de PR ou mensagem: tela afetada, rota, campo ou variável, exemplo de uso e motivo.
2. O responsável pelo arquivo avalia e implementa na **própria** branch.
3. Se o contrato mudar, atualizar este documento numa branch `docs/*`, com revisão dos dois.
4. Até lá, a tela não depende do que foi pedido: usar dado fictício só em HTML estático, nunca em código integrado.
5. Exceção (editar arquivo do outro) só com acordo explícito registrado no PR.

## 8. Regras aprovadas cobertas

| Regra | Onde aparece neste contrato |
|-------|-----------------------------|
| CPF com 11 dígitos armazenados, entrada com ou sem máscara, exibição formatada (I5) | 5.2; `cpf_formatado` |
| Aluguel futuro permitido e indisponibilidade imediata após o registro (I1) | 5.3; restrição de aluguel ativo na modelagem |
| Sem cancelamento (I1) | Fora do contrato; aviso na revisão do aluguel |
| Sem edição de aluguel ou devolução registrados (I2) | Nenhuma rota de edição; 5.4 |
| Valor diário congelado e diárias inclusivas (RN004) | Calculados pelo backend na gravação |
| Sem multas | 5.4; nenhuma rota de multa |
| Datas em `America/Recife` (TZ) | 5.3 e 5.4 |
| Exclusão condicionada ao histórico (RN003) | Rota de exclusão; `pode_excluir` |
| Reativação validada (I3) | Rota de reativação com erro no detalhe |
| Login obrigatório (D1) | `LoginRequiredMiddleware`; todas as rotas, exceto `login` |

## 9. Diferenças em relação ao guia de integração

| Guia (branch `docs/guia-integracao-raphael`) | Este rascunho | Motivo |
|----------------------------------------------|---------------|--------|
| `<app_autenticacao>:login` e `<app_autenticacao>:logout` | `login` e `logout`, sem namespace e sem app própria | Usa as views do Django sem código próprio |
| Não lista página inicial | `core:inicio` e `inicio.html` | Página P01 da arquitetura planejada |
| Não lista detalhe de equipamento | `equipamentos:detalhe` e `equipamentos/detalhe.html` | Página P04 (excluir, inativar, reativar) |
| `confirmar_exclusao.html` | Mantido | — |
| Variáveis `object_list`, `object`, `form`, `query`, `empty_message` | Mantidas | — |
| Bootstrap 5.3 local "dentro de `static/`" | Sugere `static/vendor/bootstrap/` | Separa biblioteca de terceiros do CSS próprio |

## 10. Pontos que exigem validação de Raphael

1. Nomes das apps e dos namespaces, e a autenticação sem app própria.
2. Caminhos e nomes das URLs da seção 4.
3. Lista de templates, blocos de `base.html` e includes.
4. Nomes das variáveis de contexto e dos atributos de domínio.
5. Classes do Bootstrap aplicadas pelos widgets, em vez de renderização manual de cada campo.
6. Fluxo de duas etapas do aluguel (dados → revisão → confirmação).
7. Confirmação de inativação e reativação (modal ou página).
8. Local e responsável pelos arquivos do Bootstrap em `static/vendor/bootstrap/`.

## 11. Aceite

Este documento não vale como contrato até o aceite registrado dos dois.

- Rickelme — revisão e aprovação: **pendente**.
- Raphael — revisão e aprovação: **pendente**.
