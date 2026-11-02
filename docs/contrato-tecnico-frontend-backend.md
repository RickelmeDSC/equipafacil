# Contrato técnico frontend × backend — EquipaFácil

> **PROPOSTA — AGUARDANDO VALIDAÇÃO DE RICKELME E RAPHAEL.**
>
> Versão 0.3 — 01/11/2026. Consolida o Documento de Requisitos v1.1, as decisões I1–I5 e D10–D15 e o contrato visual do épico EQF-5 (páginas P01–P10, fluxos, mensagens propostas e indicadores), conforme a auditoria do Jira de 01/11/2026.
>
> **Nada aqui está implementado**: não existe projeto Django, URL, view, formulário ou template no repositório. Raphael **não aprovou** nenhum nome de rota, campo, variável ou template deste documento.
>
> **Relação com o guia:** detalha a seção 5 do [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md) (branch `docs/guia-integracao-raphael`) e **não o substitui**. Diferenças na seção 12.

Documentos relacionados: [modelagem proposta](modelagem-proposta.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

## 1. Legenda

| Marcação | Significado |
|----------|-------------|
| **Aprovado** | Documento de Requisitos v1.1, especificação técnica v3 ou decisões I1–I5 e D10–D15 |
| **Jira (texto antigo)** | Texto do EQF-5 superado por decisão posterior; precisa ser alinhado no Jira |
| **Mensagem proposta (EQF-5)** | Texto de interface que o Jira chama de "mensagem proposta": referência, não aprovação definitiva |
| **Proposta técnica** | Sugestão de Rickelme, sem aprovação |
| **Pendente de validação** | Depende do aceite de Rickelme e Raphael ou de decisão adicional |

## 2. Arquitetura (DEV-01)

Um único projeto Django, renderizado no servidor. Sem API REST, sem endpoints JSON e sem framework de frontend (**Aprovado**: Django Templates + Bootstrap).

| Parte | Nome | Conteúdo | Situação |
|-------|------|----------|----------|
| Projeto | `config` | Configurações, URLs raiz, página inicial e rotas de login e logout | Proposta técnica |
| Equipamentos | app e namespace `equipamentos` | RF001–RF004 (P02, P03, P04) | Proposta técnica |
| Clientes | app e namespace `clientes` | RF005 (P05, P06) | Proposta técnica |
| Aluguéis | app e namespace `alugueis` | RF006–RF008 (P07, P08, P09) | Proposta técnica |
| Autenticação | **sem app própria**: views nativas do Django Auth; rotas `login` e `logout` | P10 (D1, D15) | Proposta técnica |
| Templates | diretório global `templates/` | Todas as páginas | Proposta técnica (alinhada ao guia) |
| Estáticos | `static/css/`, `static/js/`, `static/vendor/bootstrap/` | CSS, JS e Bootstrap 5.3 local | Pendente de validação |

**Justificativa:**

- **Três apps de domínio**, uma por grupo de requisitos, com nomes ASCII. Aluguel, devolução e histórico ficam juntos por operarem sobre o mesmo modelo (`Aluguel`).
- **Sem app de autenticação nem `core`:** login, logout e Admin são nativos do Django (D15); a página inicial é uma `TemplateView` em `config/urls.py`. Nenhum perfil novo está previsto.
- **Regras de negócio em `services.py`**, com type hints; views orquestram; templates exibem.
- **Templates globais**, para que todo o frontend fique numa árvore só, sob responsabilidade de Raphael.

## 3. Autenticação e administração (D1, D15)

| Item | Contrato | Situação |
|------|----------|----------|
| Login (P10) | `LoginView` nativa, `AuthenticationForm`, `registration/login.html`; usuário e senha | Aprovado (D1); detalhes são proposta técnica |
| Proteção das páginas | `LoginRequiredMiddleware` (Django 5.1 ou superior, portanto compatível com 5.2 LTS, 6.0 e 6.1) depois de `AuthenticationMiddleware`; acesso sem login vai para P10 com `?next=` e, após o login, para `next` ou P01 | Aprovado (regra); mecanismo é proposta técnica |
| Isenção da tela de login | A documentação do Django não confirma se `LoginView` e o login do Admin já vêm isentos do middleware; verificar em DEV-02 e aplicar `login_not_required` se necessário | Pendente de validação |
| Logout seguro | `LogoutView` nativa, **somente POST com CSRF**, a partir do botão Sair (P01 e barra de navegação); redireciona para P10 | Proposta técnica |
| Contas de funcionários | Criadas pelo **Django Admin** | Aprovado (D15) |
| Acesso ao Admin | Restrito a administradores autorizados (`is_staff`). Funcionários comuns não têm acesso ao Admin | Aprovado (D15) |
| Modelos no Admin | Só os de usuário do Django Auth; `Equipamento`, `Cliente` e `Aluguel` não são registrados | Proposta técnica |
| Cadastro público e recuperação de senha | Não existem; o projeto **não** inclui `django.contrib.auth.urls`, que traria rotas de troca e recuperação de senha | Aprovado (D1, D15) |
| Perfis | Nenhum perfil funcional novo: todo funcionário autenticado tem o mesmo acesso às páginas P01–P09 | Aprovado (D15) |

A validação acadêmica da autenticação como requisito transversal, sem número de RF, continua pendente com o professor (v1.1).

## 4. Páginas e fluxos (EQF-5)

| Página | Rota | Template | Conteúdo previsto no EQF-5 | Decisão aplicada |
|--------|------|----------|----------------------------|------------------|
| P10 Login | `login` | `registration/login.html` | Usuário e senha; Django Auth; sem cadastro público; sem recuperação de senha | D1, D15 |
| P01 Início | `inicio` | `inicio.html` | Menu: Equipamentos, Clientes, Novo aluguel, Histórico; funcionário autenticado; botão Sair | — |
| P02 Lista de equipamentos | `equipamentos:lista` | `equipamentos/lista.html` | Pesquisa por nome ou código; código, nome, categoria, diária, situação, disponibilidade; ações conforme permitido | — |
| P03 Formulário de equipamento | `equipamentos:criar`, `equipamentos:editar` | `equipamentos/formulario.html` | Nome, código, categoria (5 fixas), descrição opcional, diária; código somente leitura após aluguel | D11 |
| P04 Ações de equipamento | `equipamentos:acoes` (+ POST `excluir`, `inativar`, `reativar`) | `equipamentos/acoes.html` | Excluir, inativar, reativar; só ações permitidas; explicar bloqueios | **D10** (Jira: texto antigo) |
| P05 Lista de clientes | `clientes:lista` | `clientes/lista.html` | Nome completo, CPF, telefone formatado, e-mail, Editar | **D14** (Jira: texto antigo) |
| P06 Formulário de cliente | `clientes:criar`, `clientes:editar` | `clientes/formulario.html` | Nome completo e CPF obrigatórios; telefone e e-mail opcionais; CPF somente leitura após aluguel; sem exclusão | D12 |
| P07 Novo aluguel | `alugueis:criar` | `alugueis/formulario.html` | Cliente, equipamento disponível, retirada a partir de hoje, devolução prevista, diárias, valor congelado, revalidação no backend | **D13** (Jira: texto antigo) |
| P08 Histórico | `alugueis:historico` | `alugueis/historico.html` | Cliente, equipamento, retirada, prevista, real, quantidade de diárias, diária contratada, valor contratado, situação; devolução só em aluguel aberto; estado vazio sem dados fictícios | — |
| P09 Devolução | `alugueis:devolver` | `alugueis/devolver.html` | Aluguel em leitura; data real sugerida com a data atual, entre retirada e hoje; atraso sem multa; sem segunda devolução | I1, I2 |

**Fluxos (EQF-5):**

- Autenticação: sem login → P10 → P01.
- Equipamentos: P01 → P02 → P03 → P02; P02 → P04 → P02.
- Clientes: P01 → P05 → P06 → P05.
- Aluguel: P01 → P07 → P08.
- Devolução: P08 → P09 → P08.
- Erros: volta ao formulário com os dados informados e as mensagens de validação.

Nenhuma página fora de P01–P10 é criada para o frontend. O Django Admin (D15) usa os templates do próprio Django e não faz parte do contrato visual.

## 5. Convenções gerais

1. **GET** só lê dados. Toda alteração usa **POST** com `{% csrf_token %}`.
2. **POST bem-sucedido redireciona** (POST/redirect/GET), seguindo os fluxos da seção 4, com mensagem do framework `messages`.
3. **POST inválido** devolve o mesmo formulário (HTTP 200) com os dados informados e os erros.
4. Recurso inexistente retorna **404**; método não permitido retorna **405**.
5. Todo cálculo e toda validação ficam no backend. Indicadores e limites enviados ao template servem só para apresentação e são **revalidados no backend** a cada ação (seção 9.2).
6. Níveis de mensagem `success`, `warning` e `error`; o backend mapeia `error` para a classe `danger` do Bootstrap.
7. Datas exibidas como `dd/mm/aaaa` e valores como `R$ 1.500,00`, pela localização `pt-br`.
8. Variáveis padrão do Django em inglês (`object_list`, `object`, `form`); atributos de domínio em português.

## 6. Tabela final do contrato

Todas as linhas são **Pendente de validação** até o aceite conjunto. Todas as rotas exigem login, exceto `login`. São 16 rotas e 14 templates.

| Caminho | Nome da URL | Namespace | Método | View | Form | Template | Variáveis de contexto | Redirecionamento | Requisito |
|---------|-------------|-----------|--------|------|------|----------|-----------------------|------------------|-----------|
| `/login/` | `login` | — | GET, POST | `LoginView` (nativa) | `AuthenticationForm` | `registration/login.html` | `form`, `next` | `next` ou `inicio` | D1, D15 (P10) |
| `/logout/` | `logout` | — | POST | `LogoutView` (nativa) | — | — | — | `login` | D1 |
| `/` | `inicio` | — | GET | `TemplateView` | — | `inicio.html` | `user` | — | D1 (P01) |
| `/equipamentos/` | `lista` | `equipamentos` | GET | `EquipamentoListView` | — (pesquisa `?q=`) | `equipamentos/lista.html` | `object_list`, `query`, `empty_message` | — | RF002 (P02) |
| `/equipamentos/novo/` | `criar` | `equipamentos` | GET, POST | `EquipamentoCreateView` | `EquipamentoForm` | `equipamentos/formulario.html` | `form` | `equipamentos:lista` | RF001 (P03) |
| `/equipamentos/<int:pk>/editar/` | `editar` | `equipamentos` | GET, POST | `EquipamentoUpdateView` | `EquipamentoForm` | `equipamentos/formulario.html` | `form`, `object`, `codigo_editavel` | `equipamentos:lista` | RF003 (P03) |
| `/equipamentos/<int:pk>/acoes/` | `acoes` | `equipamentos` | GET | `EquipamentoAcoesView` | — | `equipamentos/acoes.html` | `object`, `tem_historico`, `tem_aluguel_ativo`, `pode_excluir`, `pode_inativar`, `pode_reativar` | — | RF004 (P04) |
| `/equipamentos/<int:pk>/excluir/` | `excluir` | `equipamentos` | POST | `EquipamentoExcluirView` | Campo `confirmacao` | — | — | `equipamentos:lista`; recusa volta a `equipamentos:acoes` | RF004, RN003 (P04) |
| `/equipamentos/<int:pk>/inativar/` | `inativar` | `equipamentos` | POST | `EquipamentoInativarView` | — | — | — | `equipamentos:lista`; recusa volta a `equipamentos:acoes` | RF004, D10 (P04) |
| `/equipamentos/<int:pk>/reativar/` | `reativar` | `equipamentos` | POST | `EquipamentoReativarView` | — | — | — | `equipamentos:lista`; recusa volta a `equipamentos:acoes` | RF004, RN003, I3 (P04) |
| `/clientes/` | `lista` | `clientes` | GET | `ClienteListView` | — | `clientes/lista.html` | `object_list`, `empty_message` | — | RF005, D14 (P05) |
| `/clientes/novo/` | `criar` | `clientes` | GET, POST | `ClienteCreateView` | `ClienteForm` | `clientes/formulario.html` | `form` | `clientes:lista` | RF005, D12 (P06) |
| `/clientes/<int:pk>/editar/` | `editar` | `clientes` | GET, POST | `ClienteUpdateView` | `ClienteForm` | `clientes/formulario.html` | `form`, `object`, `cpf_editavel` | `clientes:lista` | RF005, D12 (P06) |
| `/alugueis/` | `historico` | `alugueis` | GET | `AluguelHistoricoView` | — | `alugueis/historico.html` | `object_list`, `empty_message` | — | RF008 (P08) |
| `/alugueis/novo/` | `criar` | `alugueis` | GET, POST | `AluguelCreateView` | `AluguelForm` | `alugueis/formulario.html` | `form`, `data_atual`, `data_minima`, `diarias_equipamentos`, `sem_equipamentos_disponiveis`, `sem_clientes` | `alugueis:historico` | RF006, D13 (P07) |
| `/alugueis/<int:pk>/devolver/` | `devolver` | `alugueis` | GET, POST | `DevolucaoView` | `DevolucaoForm` | `alugueis/devolver.html` | `object`, `form`, `pode_devolver`, `data_atual`, `data_minima`, `data_maxima` | `alugueis:historico` | RF007 (P09) |

**Notas:**

- **P04 (D10):** uma única interface com as ações permitidas; excluir, inativar e reativar são rotas POST internas distintas por terem regras e mensagens próprias, sem páginas extras. A confirmação da exclusão fica dentro de P04 (por exemplo, modal do Bootstrap) e o backend exige o campo `confirmacao`. Depois da ação, o fluxo volta a P02.
- **P05 (D14):** consulta pela listagem; sem pesquisa e sem página de detalhe.
- **P07 (D13):** formulário único; o resumo aparece antes do registro e os valores definitivos depois, no histórico.
- **Fora do contrato:** exclusão de cliente, edição ou cancelamento de aluguel e devolução, cadastro público, recuperação de senha, endpoints JSON, pesquisa de clientes, multa, pagamento e reserva.

## 7. Contrato dos formulários

Nomes em português, seguindo a convenção de domínio do `CLAUDE.md` (proposta técnica). As mensagens estão na seção 8.

**Responsabilidades comuns:**

- **Backend (Rickelme):** validação, normalização, unicidade, imutabilidade, cálculo e gravação via serviço; recusa de parâmetros HTTP manipulados (RN001 b, RN002 e). Classes do Bootstrap 5.3 aplicadas pelos widgets (`form-control`, `form-select`, `is-invalid`), para que Raphael não precise editar `forms.py`.
- **Apresentação (Raphael):** layout, rótulos visíveis, máscaras apenas visuais, exibição de `form.non_field_errors` e dos erros de cada campo, acessibilidade.

### 7.1 `EquipamentoForm` — P03 (RF001, RF003, RN002, D11)

| Campo | Tipo | Obrigatório | Validação no backend |
|-------|------|-------------|----------------------|
| `codigo` | Texto | Sim | Remove espaços das extremidades; único sem diferenciar maiúsculas; grafia preservada; imutável após o primeiro aluguel |
| `nome` | Texto | Sim | Não vazio |
| `categoria` | Seleção (5 opções fixas) | Sim | Valor da lista |
| `descricao` | Texto longo | Não | — |
| `valor_diaria` | Decimal, aceita vírgula | Sim | Maior que R$ 0,00, até duas casas |

Formulário vazio no cadastro; o equipamento nasce ativo. Na edição, se `codigo_editavel` for falso, o campo `codigo` fica somente leitura e o backend ignora o valor enviado, inclusive mudança só de maiúsculas.

### 7.2 `ClienteForm` — P06 (RF005, RN002, I5, D12)

| Campo | Tipo | Obrigatório | Validação no backend |
|-------|------|-------------|----------------------|
| `nome_completo` | Texto | Sim | Não vazio |
| `cpf` | Texto | Sim | Remove só pontos e hífen; recusa outros caracteres; 11 dígitos; dígitos verificadores; recusa todos os dígitos iguais; único; imutável após o primeiro aluguel |
| `telefone` | Texto | Não | Aceita a máscara comum (parênteses, espaço, hífen — interpretação técnica de D12); recusa outros caracteres; DDD obrigatório; persiste 10 ou 11 dígitos |
| `email` | E-mail | Não | Formato válido quando informado |

Na edição, CPF e telefone aparecem formatados. Se `cpf_editavel` for falso, o campo `cpf` fica somente leitura e o backend ignora o valor enviado.

### 7.3 `AluguelForm` — P07 (RF006, RN001, RN002, RN004, I1, D13)

| Campo | Tipo | Obrigatório | Validação no backend |
|-------|------|-------------|----------------------|
| `cliente` | Seleção de cliente | Sim | Cliente existente |
| `equipamento` | Seleção só de equipamentos disponíveis, com a diária exibida | Sim | Ativo e sem aluguel aberto, revalidado na transação, inclusive contra requisição simultânea ou manipulada |
| `data_retirada` | Data | Sim | Não anterior à data atual em `America/Recife` (retirada futura permitida) |
| `data_devolucao_prevista` | Data | Sim | Igual ou posterior à retirada (mínimo de 1 diária) |

**Registro em uma etapa (D13, Aprovado):** formulário único, resumo informativo antes de registrar e aviso explícito de que não há cancelamento, sem página adicional. O backend recalcula diárias e valor e revalida tudo ao gravar.

**Implementação do resumo (proposta técnica, pendente do aceite de Raphael):**

1. O backend envia `diarias_equipamentos` (diária de cada equipamento disponível) pelo filtro nativo `json_script`, sem API nova.
2. Um JavaScript simples em `static/js/` calcula na tela `(prevista − retirada) + 1` e diárias × diária, apenas como prévia.
3. O backend **não usa** os valores do navegador: relê a diária, recalcula e grava `valor_diaria_contratada`, `quantidade_diarias` e `valor_contratado`.
4. Depois de salvar, o fluxo vai para P08, onde a linha do aluguel mostra os valores definitivamente contratados.

Se o JavaScript não for aceito, a forma de exibir o resumo antes do registro precisa de nova decisão.

### 7.4 `DevolucaoForm` — P09 (RF007, RN004, I1, I2)

| Campo | Tipo | Obrigatório | Validação no backend |
|-------|------|-------------|----------------------|
| `data_devolucao_real` | Data | Sim | Não anterior à retirada; não posterior à data atual; aluguel ainda aberto; registrada uma única vez |

Valor inicial: `data_atual`. Sem devolução antes da retirada (I1) e sem edição depois de gravada (I2). Atraso é apenas indicado, sem multa.

### 7.5 Login — P10 (D1, D15)

`AuthenticationForm` nativo: usuário e senha. Sem "lembrar-me", sem "esqueci minha senha" e sem link de cadastro.

## 8. Mensagens

As mensagens com origem **Mensagem proposta (EQF-5)** são referências de interface do Jira, não textos definitivamente aprovados. As marcadas como **Indefinida** não têm texto especificado no Jira e **não** devem ser inventadas como oficiais: precisam de definição antes da implementação.

| Situação | Texto | Origem | Página |
|----------|-------|--------|--------|
| Login obrigatório | Faça login para continuar. | Mensagem proposta (EQF-5) | P10, ao chegar redirecionado |
| Credenciais inválidas | — | Indefinida (até decisão, mensagem padrão traduzida do Django) | P10 |
| Campo obrigatório | Preencha os campos obrigatórios. | Mensagem proposta (EQF-5) | P03, P06, P07, P09 |
| Categoria inválida | Selecione uma categoria válida. | Mensagem proposta (EQF-5) | P03 |
| Diária inválida | O valor da diária deve ser maior que R$ 0,00 e ter no máximo duas casas decimais. | Mensagem proposta (EQF-5) | P03 |
| Código duplicado (inclusive sem diferenciar maiúsculas, D11) | Já existe um equipamento com este código. | Mensagem proposta (EQF-5) | P03 |
| Código bloqueado após aluguel | — | Indefinida | P03 |
| CPF inválido (caracteres, tamanho, dígitos verificadores, dígitos repetidos — D12) | CPF inválido. | Mensagem proposta (EQF-5) | P06 |
| CPF duplicado | Já existe um cliente com este CPF. | Mensagem proposta (EQF-5) | P06 |
| CPF bloqueado após aluguel | — | Indefinida | P06 |
| Telefone inválido | Informe um telefone com DDD e 10 ou 11 dígitos. | Mensagem proposta (EQF-5) | P06 |
| E-mail inválido | E-mail inválido. | Mensagem proposta (EQF-5) | P06 |
| Equipamento indisponível | Este equipamento não está disponível para aluguel. | Mensagem proposta (EQF-5) | P07 (CT12) |
| Datas do aluguel inválidas | — | Indefinida | P07 |
| Aviso de ausência de cancelamento (exigido por D13) | — | Indefinida | P07 |
| Nenhum equipamento disponível ou nenhum cliente cadastrado | — | Indefinida | P07 |
| Exclusão bloqueada por histórico | Não é possível excluir: equipamento com histórico de locação. Utilize a inativação. | Mensagem proposta (EQF-5) | P04 |
| Exclusão ou inativação bloqueada por aluguel aberto | Não é possível excluir ou inativar: equipamento com aluguel ativo. | Mensagem proposta (EQF-5) | P04 |
| Reativação bloqueada | Não é possível reativar: corrija os dados cadastrais ou encerre o aluguel ativo. | Mensagem proposta (EQF-5) | P04 |
| Data de devolução fora do intervalo | — | Indefinida | P09 |
| Devolução já encerrada | Este aluguel já foi encerrado. | Mensagem proposta (EQF-5) | P09, P08 (CT14) |
| Indicação de atraso | — | Indefinida | P09, P08 |
| Sem resultados | Nenhum registro encontrado. | Mensagem proposta (EQF-5) | P02 (CT04), P05, P08 (CT16) |
| Sucesso: cadastro e edição de equipamento e cliente, exclusão, inativação, reativação, aluguel e devolução | — | Indefinida (não especificada no Jira) | P02, P05, P08 |

## 9. Contrato dos templates

### 9.1 Templates

Contexto global em todas as páginas: `user`, `messages`, `request` e `csrf_token`.

| Template | Página | Formulário | Estados | Conteúdo e ações |
|----------|--------|------------|---------|------------------|
| `base.html` | Todas | — | Autenticado; P10 sem menu | Blocos `title` e `content`; carrega Bootstrap local |
| `includes/navbar.html` | P01–P09 | Sair (POST) | — | Equipamentos, Clientes, Novo aluguel, Histórico; nome do funcionário; Sair |
| `includes/messages.html` | Todas | — | Sucesso, atenção, erro | Fechar alerta |
| `includes/form_errors.html` | P03, P06, P07, P09, P10 | — | Com ou sem `non_field_errors` | — |
| `registration/login.html` | P10 | `AuthenticationForm` | Inicial; redirecionado sem login; credenciais inválidas | Entrar |
| `inicio.html` | P01 | — | — | Menu das áreas; funcionário autenticado; Sair |
| `equipamentos/lista.html` | P02 | Pesquisa (GET `q`) | Com resultados; sem cadastro; pesquisa sem resultado (CT04) | Colunas: código, nome, categoria, diária, situação (Ativo/Inativo), disponibilidade; links Editar e Ações |
| `equipamentos/formulario.html` | P03 | `EquipamentoForm` | Cadastro; edição; código somente leitura; erro | Salvar; voltar a P02 |
| `equipamentos/acoes.html` | P04 | Excluir (com confirmação), inativar, reativar — POST | Sem histórico; com histórico; com aluguel aberto; inativo | Só as ações permitidas; explicação dos bloqueios; voltar a P02 |
| `clientes/lista.html` | P05 | — | Com clientes; sem clientes | Colunas: nome completo, CPF formatado, telefone formatado, e-mail; Editar |
| `clientes/formulario.html` | P06 | `ClienteForm` | Cadastro; edição; CPF somente leitura; erro | Salvar; voltar a P05 |
| `alugueis/formulario.html` | P07 | `AluguelForm` | Formulário; erro; nenhum equipamento disponível; nenhum cliente | Resumo informativo (diárias e valor); aviso de ausência de cancelamento; Registrar |
| `alugueis/historico.html` | P08 | — | Com registros; sem registros (CT16) | Colunas: cliente, equipamento (inclusive inativo), retirada, prevista, real, **quantidade de diárias**, diária contratada, valor contratado, situação; Registrar devolução só quando `pode_devolver` |
| `alugueis/devolver.html` | P09 | `DevolucaoForm` | Formulário; erro de data | Dados do aluguel em leitura; data real; Confirmar devolução; voltar a P08 |

### 9.2 Indicadores de contexto

Os seis primeiros nomes vêm do EQF-5. Os demais são **propostas técnicas** para conceitos que o Jira exige sem fixar nome. Todo indicador é **só de apresentação**: a mesma regra é **revalidada no backend** no momento da ação, mesmo que o botão esteja oculto ou desabilitado.

| Variável | Origem do nome | Página e template | Valor | Uso na apresentação | Revalidação no backend |
|----------|----------------|-------------------|-------|---------------------|------------------------|
| `pode_excluir` | EQF-5 | P04 `equipamentos/acoes.html` | Sem histórico | Mostrar Excluir com confirmação | Serviço revalida na transação; `PROTECT`; exige `confirmacao` |
| `pode_inativar` | EQF-5 | P04 `equipamentos/acoes.html` | Ativo e sem aluguel aberto, com ou sem histórico (D10) | Mostrar Inativar | Serviço revalida com bloqueio da linha |
| `pode_reativar` | EQF-5 | P04 `equipamentos/acoes.html` | Inativo, dados cadastrais válidos e sem aluguel aberto | Mostrar Reativar | Serviço revalida dados (RN002, D11) e aluguel |
| `codigo_editavel` | EQF-5 | P03 `equipamentos/formulario.html` (edição) | Nenhum aluguel associado | Código somente leitura e explicação | Formulário ignora o valor; serviço revalida |
| `cpf_editavel` | EQF-5 | P06 `clientes/formulario.html` (edição) | Nenhum aluguel associado | CPF somente leitura e explicação | Formulário ignora o valor; serviço revalida |
| `pode_devolver` | EQF-5 | P08 `alugueis/historico.html` (por aluguel); P09 `alugueis/devolver.html` | Aluguel aberto e `data_atual` igual ou posterior à retirada (I1) | Mostrar Registrar devolução | Atualização condicional (só grava se aberto) e validação de datas |
| `tem_historico`, `tem_aluguel_ativo` | Proposta técnica | P04 `equipamentos/acoes.html` | Fatos do equipamento | Explicar bloqueios | — |
| `disponivel` | Proposta técnica (conceito do EQF-5) | P02 `equipamentos/lista.html` (por equipamento) | Ativo e sem aluguel aberto | Disponível / Indisponível | Serviço de aluguel revalida |
| `situacao`, `situacao_codigo` | Proposta técnica (conceito do EQF-5) | P08 `alugueis/historico.html` (por aluguel) | Ativo, Atrasado, Encerrado, Encerrado com atraso | Texto e selo | Calculado no servidor |
| `data_atual` | Proposta técnica (conceito do EQF-5) | P07 `alugueis/formulario.html`; P09 `alugueis/devolver.html` | Data local em `America/Recife` | Valor inicial da retirada (P07) e data sugerida (P09) | O servidor usa sua própria data atual |
| `data_minima` | Proposta técnica (conceito do EQF-5) | P07 (igual a `data_atual`, para a retirada); P09 (data de retirada do aluguel) | Limite mínimo | Atributo `min` do campo | Retirada não anterior a hoje; devolução não anterior à retirada |
| `data_maxima` | Proposta técnica (conceito do EQF-5) | P09 (igual a `data_atual`) | Limite máximo | Atributo `max` do campo | Devolução não posterior a hoje |
| `diarias_equipamentos` | Proposta técnica (D13) | P07 `alugueis/formulario.html` | Diária de cada equipamento disponível, via `json_script` | Prévia de diárias e valor | Backend relê a diária e recalcula |
| `sem_equipamentos_disponiveis`, `sem_clientes` | Proposta técnica | P07 `alugueis/formulario.html` | Ausência de equipamento disponível ou de cliente | Aviso no lugar do envio | Serviço recusa |
| `query` | Proposta técnica | P02 `equipamentos/lista.html` | Termo pesquisado | Manter o termo no campo | — |
| `empty_message` | Proposta técnica (guia) | P02, P05, P08 | "Nenhum registro encontrado." | Estado vazio | — |

A devolução prevista mínima depende da retirada escolhida na própria tela; o ajuste em JavaScript é só informativo, e o backend valida "prevista igual ou posterior à retirada".

### 9.3 Atributos dos objetos

| Objeto | Atributos para exibição |
|--------|-------------------------|
| Equipamento (P02, P04) | `codigo`, `nome`, `get_categoria_display`, `valor_diaria`, `ativo`, `disponivel` |
| Cliente (P05) | `nome_completo`, `cpf_formatado`, `telefone_formatado`, `email` |
| Aluguel (P08, P09) | `cliente`, `equipamento`, `data_retirada`, `data_devolucao_prevista`, `data_devolucao_real`, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado`, `situacao`, `situacao_codigo`, `pode_devolver` |

### 9.4 Estados vazios e regras de apresentação

- **Estados vazios:** P02 sem cadastro ou sem resultado na pesquisa (CT04), P05 sem clientes e P08 sem aluguéis (CT16) mostram `empty_message` dentro de `{% empty %}`, **sem dados fictícios**. P07 sem equipamento disponível ou sem cliente mostra aviso (texto indefinido).
- Ações só aparecem com o indicador verdadeiro; bloqueios são explicados, não apenas escondidos (P04).
- Campos somente leitura (código, CPF) mostram o valor e a explicação do bloqueio.
- `situacao_codigo` serve só para o estilo do selo; o texto é `situacao`.
- Sem paginação na v1; nenhum `|safe` em dado digitado; links sempre com `{% url %}`.

## 10. Divisão de arquivos

Cada arquivo tem **um** responsável. Ninguém edita arquivo do outro.

| Responsável | Arquivos |
|-------------|----------|
| **Rickelme (backend)** | `manage.py`, `config/**`, `*/models.py`, `*/forms.py`, `*/views.py`, `*/urls.py`, `*/services.py`, `*/admin.py`, `*/apps.py`, `*/migrations/**`, `*/tests/**`, dependências, `.env.example`, `CLAUDE.md`, `.claude/**` |
| **Raphael (frontend)** | `templates/**/*.html`, `static/css/**`, `static/js/**` (inclusive a prévia de P07), `static/img/**`, `static/vendor/bootstrap/**` (pendente de validação) |
| **Ambos, via PR revisado pelos dois** | Este contrato e o guia de integração |

**Procedimento para pedir mudança em arquivo do outro:** descrever o pedido em comentário de PR ou mensagem (tela, rota, campo ou variável, exemplo e motivo); o responsável implementa na própria branch; se o contrato mudar, atualizar este documento numa branch `docs/*` com revisão dos dois; até lá, a tela não depende do pedido; editar arquivo do outro só com acordo explícito registrado no PR.

## 11. Regras aprovadas cobertas

| Regra | Onde aparece |
|-------|--------------|
| RF001–RF008 | Tabela final (seção 6) e páginas P01–P10 (seção 4) |
| RN001 (um aluguel aberto, disponibilidade derivada, revalidação) | 7.3; `disponivel`; modelagem |
| RN002 (validação no backend) | Seção 7; revalidação em 9.2 |
| RN003 (exclusão, inativação, reativação, clientes sem exclusão) | P04, P05, P06; D10 |
| RN004 (datas em Recife, diárias inclusivas, valor congelado, atraso sem multa) | 7.3, 7.4; `data_atual`, `data_minima`, `data_maxima` |
| I1 (retirada futura, sem cancelamento, sem devolução antes da retirada) | 7.3, 7.4; `pode_devolver` |
| I2 (sem edição de aluguel e devolução) | Nenhuma rota de edição |
| I3 (reativação validada; teste complementar) | `pode_reativar`; plano |
| I4 (prioridades do Jira preservadas) | Plano |
| I5 e D12 (CPF e telefone) | 7.2; `cpf_formatado`, `telefone_formatado` |
| D10 (inativação com ou sem histórico) | P04; `pode_inativar` |
| D11 (código sem espaços extremos, único sem diferenciar maiúsculas) | 7.1; modelagem |
| D13 (aluguel em uma etapa com resumo e aviso) | 7.3; P07 |
| D14 (clientes pela listagem, sem pesquisa e sem detalhe) | P05 |
| D15 (contas pelo Django Admin, Admin restrito, sem perfis novos) | Seção 3 |

## 12. Divergências

### 12.1 Jira (texto antigo do EQF-5) a alinhar depois

| Página | Texto antigo do EQF-5 | Decisão que prevalece |
|--------|-----------------------|-----------------------|
| P04 | Inativação prevista para equipamento com histórico | D10: todo equipamento ativo sem aluguel aberto pode ser inativado, com ou sem histórico |
| P05 | Pesquisa de clientes | D14: sem pesquisa nesta versão; consulta pela listagem |
| P07 | Valores exibidos após salvar | D13: resumo no próprio formulário, aviso de ausência de cancelamento e valores definitivos após salvar |

Também recomendável informar a equipe de Requisitos: D10, D11 e D12 detalham pontos que o Documento v1.1 descreve de forma mais geral (inativação "com histórico", "código único" e validação do CPF).

### 12.2 Guia de integração

| Guia (branch `docs/guia-integracao-raphael`) | Este contrato | Motivo |
|----------------------------------------------|---------------|--------|
| `<app_autenticacao>:login` e `<app_autenticacao>:logout` | `login` e `logout`, nativos, sem namespace | Sem app de autenticação (D15) |
| Não lista página inicial | `inicio` e `inicio.html` | P01 |
| `clientes:detalhe` e `clientes/detalhe.html` | Removidos | D14 |
| `equipamentos/confirmar_exclusao.html` | Confirmação dentro de `equipamentos/acoes.html` | P04 com ações condicionais, sem página extra |
| Variável `object_list`, `object`, `form`, `query`, `empty_message` | Mantidas | — |
| Bootstrap 5.3 local "dentro de `static/`" | `static/vendor/bootstrap/` | Separa biblioteca de terceiros do CSS próprio |

## 13. Pontos para validação de Rickelme e Raphael

**Validação conjunta (Rickelme e Raphael):**

1. Apps e namespaces (`equipamentos`, `clientes`, `alugueis`), página inicial em `config` e autenticação sem app própria.
2. Caminhos, nomes, views e redirecionamentos da tabela final (seção 6).
3. Os 14 templates, os blocos de `base.html` e os includes.
4. Nomes técnicos propostos para os indicadores sem nome no Jira (`data_atual`, `data_minima`, `data_maxima`, `disponivel`, `situacao` e demais da seção 9.2).
5. Forma da confirmação de exclusão dentro de P04 (modal ou bloco).
6. Classes do Bootstrap aplicadas pelos widgets do backend.
7. Local e responsável pelos arquivos do Bootstrap em `static/vendor/bootstrap/`.
8. **Uso de JavaScript para o resumo de P07** e o formato de `diarias_equipamentos` (D13).
9. Links de cada linha de P02 (Editar e Ações).

**Decisão de Rickelme:**

10. Textos das mensagens marcadas como **Indefinida** na seção 8, inclusive as de sucesso.
11. Alinhamento posterior do texto antigo do EQF-5 (P04, P05, P07) no Jira.
12. Verificação, em DEV-02, do login nativo e do login do Admin com `LoginRequiredMiddleware`.

## 14. Aceite

Este documento não vale como contrato até o aceite registrado dos dois.

- Rickelme — revisão e aprovação: **pendente**.
- Raphael — revisão e aprovação: **pendente**.
