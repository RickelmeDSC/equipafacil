# Contrato técnico frontend × backend — EquipaFácil

> **PROPOSTA PARA VALIDAÇÃO DE RICKELME E RAPHAEL**
>
> Versão 0.2 — 01/11/2026, reconciliada com o Documento de Requisitos v1.1 e com a auditoria do Jira de 01/11/2026 (escopo de DEV-01, DEV-02 e DEV-03). Continua sendo **proposta até o aceite conjunto** (seção 12).
>
> **Nada aqui está implementado**: não existe projeto Django, URL, view, formulário ou template no repositório. Raphael **não aprovou** nenhum nome de rota, campo, variável ou template deste documento.
>
> **Mensagens:** a tabela oficial de mensagens do épico EQF-5 ainda não foi conferida. **Todos os textos de mensagem abaixo são provisórios.**
>
> **Relação com o guia:** detalha a seção 5 do [guia de integração](https://github.com/RickelmeDSC/equipafacil/blob/docs/guia-integracao-raphael/docs/guia-integracao-frontend-backend.md) (branch `docs/guia-integracao-raphael`) e **não o substitui**. Diferenças na seção 10.

Documentos relacionados: [modelagem proposta](modelagem-proposta.md) e [plano backend DEV-01 a DEV-03](plano-backend-dev01-dev03.md).

## 1. Legenda de situação

| Marcação | Significado |
|----------|-------------|
| **Aprovado** | Consta do Documento de Requisitos v1.1, da especificação técnica v3 ou das decisões I1–I5 |
| **Proposta** | Sugestão técnica de Rickelme, ainda não validada |
| **Decisão conjunta** | Precisa do acordo de Rickelme e Raphael antes de implementar |
| **Interpretação pendente** | O requisito admite mais de uma leitura; não vira regra sem decisão registrada |
| **Depende de implementação** | Só será confirmado com o código (DEV-02 em diante) |

## 2. Arquitetura proposta (DEV-01)

Um único projeto Django, renderizado no servidor. Sem API REST, sem endpoints JSON e sem framework de frontend (**Aprovado**: Django Templates + Bootstrap).

| Parte | Nome proposto | Conteúdo | Situação |
|-------|---------------|----------|----------|
| Projeto | `config` | Configurações, URLs raiz, página inicial e rotas de login e logout | Proposta |
| Equipamentos | app e namespace `equipamentos` | RF001–RF004 | Proposta |
| Clientes | app e namespace `clientes` | RF005 | Proposta |
| Aluguéis | app e namespace `alugueis` | RF006–RF008 (aluguel, devolução e histórico) | Proposta |
| Autenticação | **sem app própria**: views nativas do `django.contrib.auth`, rotas `login` e `logout` | Requisito transversal (D1) | Proposta, sujeita à validação do contrato |
| Templates | diretório global `templates/` | Todas as páginas | Proposta (alinhada ao guia) |
| Estáticos | `static/css/`, `static/js/`, `static/vendor/bootstrap/` | CSS, JS e Bootstrap 5.3 local | Decisão conjunta |

**Justificativa:**

- **Três apps de domínio**, uma por grupo de requisitos, com nomes ASCII em português. Aluguel, devolução e histórico ficam juntos porque operam sobre o mesmo modelo (`Aluguel`).
- **Sem app de autenticação:** login e logout usam as views nativas do Django, sem código próprio, e as contas são criadas administrativamente (D1). Uma app só se justificaria com perfis ou telas próprias, que não estão previstos.
- **Sem app `core`:** a página inicial (P01) é uma `TemplateView` registrada em `config/urls.py`.
- **Regras de negócio em `services.py`** de cada app, com type hints; views apenas orquestram; templates apenas exibem.
- **Templates globais**, como sugere o guia, para que todo o frontend fique numa árvore só, sob responsabilidade de Raphael.

## 3. Autenticação (requisito transversal, D1)

| Item | Contrato proposto | Situação |
|------|-------------------|----------|
| Login de funcionários | `LoginView` nativa, formulário `AuthenticationForm`, template `registration/login.html` | Aprovado (D1); detalhes são proposta |
| Logout | `LogoutView` nativa, **somente POST com CSRF** (a documentação do Django descreve o logout apenas por POST); formulário na barra de navegação | Proposta |
| Redirecionamento após login | Para o parâmetro `next`, se houver; senão `inicio` (`LOGIN_REDIRECT_URL`) | Proposta |
| Redirecionamento após logout | `login` (`LOGOUT_REDIRECT_URL`) | Proposta |
| Proteção das rotas | `LoginRequiredMiddleware` depois de `AuthenticationMiddleware`; acesso sem login vai para `login` com `?next=` (v1.1: "o acesso sem autenticação é direcionado à tela de login") | Aprovado (regra); mecanismo é proposta |
| Isenção da tela de login | A view de login precisa aceitar acesso anônimo. A documentação do Django não confirma se `LoginView` já vem isenta; em DEV-02, verificar e, se preciso, aplicar `login_not_required` ao registrar a rota | Depende de implementação |
| Provisionamento de contas | Administrativo (D1): `createsuperuser` para o administrador e Django Admin restrito ao cadastro de usuários. `Equipamento`, `Cliente` e `Aluguel` **não** são registrados no Admin para edição livre, pois isso contornaria as regras | Proposta |
| Cadastro público e recuperação de senha | Não existem. O projeto **não** inclui `django.contrib.auth.urls`, que traria rotas de troca e recuperação de senha | Aprovado (fora do escopo, v1.1) |
| Perfis | Nenhum perfil adicional: todo funcionário autenticado tem o mesmo acesso | Aprovado (sem perfis previstos) |

**Compatibilidade:** `LoginRequiredMiddleware` e `login_not_required` existem desde o Django 5.1, segundo as notas de versão e a referência de middleware oficiais. As três séries candidatas (5.2 LTS, 6.0 e 6.1) são posteriores, logo compatíveis; a escolha final da versão é de DEV-02.

## 4. Convenções gerais

1. **GET** só lê dados. Toda alteração usa **POST** com `{% csrf_token %}`.
2. **POST bem-sucedido redireciona** (padrão POST/redirect/GET) com mensagem do framework `messages`.
3. **POST inválido** devolve a mesma página (HTTP 200) com o formulário preenchido e os erros.
4. Recurso inexistente retorna **404**; método não permitido retorna **405**.
5. Todo cálculo e toda validação ficam no backend. Flags e limites enviados ao template servem só para apresentação (seção 7.2).
6. Níveis de mensagem `success`, `warning` e `error`; o backend mapeia `error` para a classe `danger` do Bootstrap.
7. Datas exibidas como `dd/mm/aaaa` e valores como `R$ 1.500,00`, pela localização `pt-br`, sem cálculo no template.
8. Variáveis padrão do Django em inglês (`object_list`, `object`, `form`); atributos de domínio em português.

## 5. Tabela final do contrato

Todas as linhas são **Proposta** até o aceite conjunto. Todas as rotas exigem login, exceto `login`. São 16 rotas e 14 templates.

| Caminho | Nome da URL | Namespace | Método | View | Form | Template | Variáveis de contexto | Redirecionamento | Requisito |
|---------|-------------|-----------|--------|------|------|----------|-----------------------|------------------|-----------|
| `/login/` | `login` | — | GET, POST | `LoginView` (nativa) | `AuthenticationForm` | `registration/login.html` | `form`, `next` | `next` ou `inicio` | D1 |
| `/logout/` | `logout` | — | POST | `LogoutView` (nativa) | — | — | — | `login` | D1 |
| `/` | `inicio` | — | GET | `TemplateView` | — | `inicio.html` | `user` | — | D1 (P01) |
| `/equipamentos/` | `lista` | `equipamentos` | GET | `EquipamentoListView` | — (pesquisa `?q=`) | `equipamentos/lista.html` | `object_list`, `query`, `empty_message` | — | RF002 |
| `/equipamentos/novo/` | `criar` | `equipamentos` | GET, POST | `EquipamentoCreateView` | `EquipamentoForm` | `equipamentos/formulario.html` | `form` | `equipamentos:lista` | RF001 |
| `/equipamentos/<int:pk>/editar/` | `editar` | `equipamentos` | GET, POST | `EquipamentoUpdateView` | `EquipamentoForm` | `equipamentos/formulario.html` | `form`, `object`, `codigo_editavel` | `equipamentos:lista` | RF003 |
| `/equipamentos/<int:pk>/acoes/` | `acoes` | `equipamentos` | GET | `EquipamentoAcoesView` | — | `equipamentos/acoes.html` | `object`, `tem_historico`, `tem_aluguel_ativo`, `pode_excluir`, `pode_inativar`, `pode_reativar` | — | RF004 |
| `/equipamentos/<int:pk>/excluir/` | `excluir` | `equipamentos` | POST | `EquipamentoExcluirView` | Campo `confirmacao` | — | — | `equipamentos:lista`; recusa volta a `equipamentos:acoes` | RF004, RN003 |
| `/equipamentos/<int:pk>/inativar/` | `inativar` | `equipamentos` | POST | `EquipamentoInativarView` | — | — | — | `equipamentos:acoes` | RF004, RN003 |
| `/equipamentos/<int:pk>/reativar/` | `reativar` | `equipamentos` | POST | `EquipamentoReativarView` | — | — | — | `equipamentos:acoes` | RF004, RN003, I3 |
| `/clientes/` | `lista` | `clientes` | GET | `ClienteListView` | — | `clientes/lista.html` | `object_list`, `empty_message` | — | RF005 |
| `/clientes/novo/` | `criar` | `clientes` | GET, POST | `ClienteCreateView` | `ClienteForm` | `clientes/formulario.html` | `form` | `clientes:lista` | RF005 |
| `/clientes/<int:pk>/editar/` | `editar` | `clientes` | GET, POST | `ClienteUpdateView` | `ClienteForm` | `clientes/formulario.html` | `form`, `object`, `cpf_editavel` | `clientes:lista` | RF005 |
| `/alugueis/` | `historico` | `alugueis` | GET | `AluguelHistoricoView` | — | `alugueis/historico.html` | `object_list`, `empty_message` | — | RF008 |
| `/alugueis/novo/` | `criar` | `alugueis` | GET, POST | `AluguelCreateView` | `AluguelForm` | `alugueis/formulario.html` | `form`, `data_atual`, `data_minima_retirada`, `sem_equipamentos_disponiveis`, `sem_clientes` | `alugueis:historico` | RF006 |
| `/alugueis/<int:pk>/devolver/` | `devolver` | `alugueis` | GET, POST | `DevolucaoView` | `DevolucaoForm` | `alugueis/devolver.html` | `object`, `form`, `pode_devolver`, `data_atual`, `data_minima_devolucao`, `data_maxima_devolucao` | `alugueis:historico` | RF007 |

**Notas:**

- **Clientes:** a consulta é feita pela listagem (Jira e RF005); não há página de detalhe.
- **Equipamentos:** uma única interface (P04, `equipamentos:acoes`) mostra as ações condicionais de exclusão, inativação e reativação. As três ações são rotas POST internas distintas, justificadas por terem regras e mensagens diferentes; nenhuma exige página de apresentação própria. A **confirmação da exclusão** é preservada dentro dessa interface (por exemplo, modal do Bootstrap), e o backend exige o campo `confirmacao` no POST, para que a exclusão nunca ocorra sem confirmação explícita.
- **Fora do contrato:** exclusão de cliente, edição ou cancelamento de aluguel e devolução, cadastro público, recuperação de senha, endpoints JSON, pesquisa de clientes, multa, pagamento e reserva.
- **Admin:** se adotado para o provisionamento de contas (seção 3), `/admin/` usa os templates do próprio Django e não faz parte do frontend.

## 6. Contrato dos formulários

Os nomes da tarefa (EquipmentForm, ClientForm, RentalForm, ReturnForm, LoginForm) foram mapeados para nomes em português, seguindo a convenção de domínio do `CLAUDE.md` (**Proposta**). **Mensagens provisórias** até a conferência da tabela do EQF-5.

**Responsabilidades comuns:**

- **Backend:** validação, normalização, unicidade, imutabilidade, cálculo e gravação via serviço; recusa de parâmetros HTTP manipulados (RN001 b, RN002 e). Classes do Bootstrap 5.3 aplicadas pelos widgets (`form-control`, `form-select`, `is-invalid`), para que Raphael não precise editar `forms.py`.
- **Apresentação (Raphael):** layout, rótulos visíveis, máscaras apenas visuais, exibição de `form.non_field_errors` e dos erros de cada campo, acessibilidade.

### 6.1 `EquipamentoForm` (pedido: EquipmentForm) — RF001, RF003, RN002

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `nome` | Texto | Sim | Não vazio | "Informe o nome do equipamento." |
| `codigo` | Texto | Sim | Único; imutável após o primeiro aluguel | "Já existe um equipamento com este código." |
| `categoria` | Seleção (5 opções fixas) | Sim | Valor da lista | "Selecione uma categoria válida." |
| `descricao` | Texto longo | Não | — | — |
| `valor_diaria` | Decimal, 2 casas, aceita vírgula | Sim | Maior que R$ 0,00 | "A diária deve ser maior que R$ 0,00." |

- **Valores iniciais:** formulário vazio no cadastro; `ativo` não aparece, pois o equipamento nasce ativo (RF001).
- **Imutabilidade (RF003):** se `codigo_editavel` for falso, o campo vem desabilitado, o backend ignora o valor enviado e a tela mostra mensagem clara de bloqueio, por exemplo "O código não pode ser alterado porque o equipamento já possui aluguel."
- **Normalização do código** (remover espaços, ignorar maiúsculas): **Interpretação pendente**, não aplicada.

### 6.2 `ClienteForm` (pedido: ClientForm) — RF005, RN002, I5

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `nome_completo` | Texto | Sim | Não vazio | "Informe o nome completo do cliente." |
| `cpf` | Texto | Sim | Remove **apenas** pontos e hífen; qualquer outro caractere é recusado; exatamente 11 dígitos; dígitos verificadores; único; imutável após o primeiro aluguel | "CPF inválido." e "Já existe um cliente com este CPF." |
| `telefone` | Texto | Não | Brasileiro com DDD, 10 ou 11 dígitos, armazenado só com dígitos | "Informe um telefone com DDD (10 ou 11 dígitos)." |
| `email` | E-mail | Não | Formato válido quando informado | "Informe um e-mail válido." |

- **Valores iniciais:** na edição, CPF e telefone aparecem formatados.
- **Imutabilidade:** se `cpf_editavel` for falso, o campo vem desabilitado, o backend ignora o valor e a tela mostra mensagem clara de bloqueio.
- **Proposta:** quais caracteres do telefone são removidos na normalização (parênteses, espaços, hífen) e a recusa de CPF com todos os dígitos iguais não constam do v1.1 — ficam pendentes.

### 6.3 `AluguelForm` (pedido: RentalForm) — RF006, RN001, RN002, RN004, I1

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `cliente` | Seleção de cliente | Sim | Cliente existente | "Selecione um cliente." |
| `equipamento` | Seleção só de equipamentos disponíveis | Sim | Ativo e sem aluguel ativo, revalidado na transação, inclusive contra requisição simultânea ou manipulada | "Equipamento indisponível para aluguel." (CT12) |
| `data_retirada` | Data | Sim | Não anterior à data atual em `America/Recife` (retirada futura permitida, I1) | "A data de retirada não pode ser anterior à data atual." |
| `data_devolucao_prevista` | Data | Sim | Igual ou posterior à retirada (mínimo de 1 diária) | "A devolução prevista não pode ser anterior à retirada." |

- **Valores iniciais:** `data_retirada` = `data_atual`.
- **Calculado pelo backend, nunca recebido do formulário:** `valor_diaria_contratada`, `quantidade_diarias` e `valor_contratado`. A mensagem de sucesso informa os valores calculados, por exemplo "Aluguel registrado: 3 diárias, valor contratado R$ 150,00."
- **Etapa de revisão antes de gravar** (resumo calculado e aviso de que não há cancelamento): **Proposta opcional**, não obrigatória. O contrato base é um único envio.

### 6.4 `DevolucaoForm` (pedido: ReturnForm) — RF007, RN004, I1, I2

| Campo | Tipo | Obrigatório | Validação no backend | Mensagem provisória |
|-------|------|-------------|----------------------|---------------------|
| `data_devolucao_real` | Data | Sim | Não anterior à retirada e não posterior à data atual; aluguel ainda ativo; registrada uma única vez | "A data de devolução deve estar entre a retirada e a data atual." e "Este aluguel já foi encerrado." (CT14) |

- **Valores iniciais:** `data_atual` (v1.1: "sugerida com a data atual").
- **Antes da retirada** não há devolução possível (I1); **depois de gravada**, não há edição (I2).
- **Sucesso (provisório):** "Devolução registrada." ou, com atraso, "Devolução registrada com atraso." Nunca há multa.

### 6.5 Login (pedido: LoginForm) — D1

`AuthenticationForm` nativo do Django: `username` e `password`, mensagem de erro padrão traduzida. Sem "lembrar-me", sem "esqueci minha senha" e sem link de cadastro.

## 7. Contrato dos templates

### 7.1 Templates

Contexto global em todas as páginas: `user`, `messages`, `request` e `csrf_token`.

| Template | Rota | Formulário | Estados | Ações e conteúdo |
|----------|------|------------|---------|------------------|
| `base.html` | Todas | — | Autenticado; página de login sem menu | Blocos `title` e `content`; carrega Bootstrap local |
| `includes/navbar.html` | Todas autenticadas | Logout (POST) | — | Início, Equipamentos, Clientes, Novo aluguel, Histórico, Sair |
| `includes/messages.html` | Todas | — | Sucesso, atenção, erro | Fechar alerta |
| `includes/form_errors.html` | Páginas com formulário | — | Com ou sem `non_field_errors` | — |
| `registration/login.html` | `login` | `AuthenticationForm` | Inicial; credenciais inválidas | Entrar |
| `inicio.html` | `inicio` | — | — | Atalhos para as áreas (P01) |
| `equipamentos/lista.html` | `equipamentos:lista` | Pesquisa (GET `q`) | Com resultados; sem cadastro; pesquisa sem resultado (CT04) | Colunas: nome, código, categoria, diária, situação (Ativo/Inativo) e disponibilidade; links Editar e Ações |
| `equipamentos/formulario.html` | `equipamentos:criar`, `equipamentos:editar` | `EquipamentoForm` | Cadastro; edição; código bloqueado; erro | Salvar; voltar |
| `equipamentos/acoes.html` | `equipamentos:acoes` | Excluir (com confirmação), inativar, reativar — POST | Sem histórico; com histórico; com aluguel ativo; inativo | Só as ações permitidas; motivo quando a ação não está disponível |
| `clientes/lista.html` | `clientes:lista` | — | Com clientes; sem clientes | Colunas: nome completo, CPF formatado, telefone formatado, e-mail; link Editar |
| `clientes/formulario.html` | `clientes:criar`, `clientes:editar` | `ClienteForm` | Cadastro; edição; CPF bloqueado; erro | Salvar; voltar |
| `alugueis/formulario.html` | `alugueis:criar` | `AluguelForm` | Formulário; erro; nenhum equipamento disponível; nenhum cliente | Registrar; voltar |
| `alugueis/devolver.html` | `alugueis:devolver` | `DevolucaoForm` | Formulário; erro de data | Dados do aluguel; confirmar devolução; voltar |
| `alugueis/historico.html` | `alugueis:historico` | — | Com registros; sem registros (CT16) | Colunas: cliente, equipamento (inclusive inativo), retirada, devolução prevista, devolução real, **quantidade de diárias**, diária contratada, valor contratado e situação; link Registrar devolução quando `pode_devolver` |

### 7.2 Variáveis de contexto e onde aparecem

Cada flag é **indicador de apresentação**: decide o que mostrar. A **validação obrigatória** acontece de novo no backend, no momento da ação, independentemente do que a tela mostrou.

| Variável | Telas | Valor | Uso na apresentação | Validação obrigatória no backend |
|----------|-------|-------|---------------------|----------------------------------|
| `pode_excluir` | `equipamentos/acoes.html` | Sem histórico de aluguéis | Mostrar "Excluir" com confirmação | Serviço revalida "sem histórico" na transação; `PROTECT` no banco; exige `confirmacao` |
| `pode_inativar` | `equipamentos/acoes.html` | Ativo, com histórico e sem aluguel ativo (caso sem histórico: interpretação pendente) | Mostrar "Inativar" | Serviço revalida com bloqueio da linha do equipamento |
| `pode_reativar` | `equipamentos/acoes.html` | Inativo, dados cadastrais válidos e sem aluguel ativo (RN003 e) | Mostrar "Reativar" | Serviço revalida dados e ausência de aluguel ativo |
| `tem_historico`, `tem_aluguel_ativo` | `equipamentos/acoes.html` | Fatos do equipamento | Explicar por que uma ação não aparece | — |
| `codigo_editavel` | `equipamentos/formulario.html` (edição) | Nenhum aluguel associado | Campo desabilitado e mensagem de bloqueio | Formulário ignora o valor; serviço revalida na transação |
| `cpf_editavel` | `clientes/formulario.html` (edição) | Nenhum aluguel associado | Campo desabilitado e mensagem de bloqueio | Formulário ignora o valor; serviço revalida na transação |
| `pode_devolver` | `alugueis/historico.html` (por aluguel), `alugueis/devolver.html` | Aluguel ativo e `data_atual` igual ou posterior à retirada | Mostrar o link e o formulário de devolução | Atualização condicional (só grava se ainda ativo) e validação de datas |
| `data_atual` | `alugueis/formulario.html`, `alugueis/devolver.html` | `timezone.localdate()` em `America/Recife` | Valor sugerido e exibição | Toda comparação de data usa a data calculada no servidor |
| `data_minima_retirada` | `alugueis/formulario.html` | Igual a `data_atual` | Atributo `min` do campo de retirada | Retirada não anterior à data atual |
| `data_minima_devolucao` | `alugueis/devolver.html` | Data de retirada do aluguel | Atributo `min` | Devolução real não anterior à retirada |
| `data_maxima_devolucao` | `alugueis/devolver.html` | Igual a `data_atual` | Atributo `max` | Devolução real não posterior à data atual |
| `sem_equipamentos_disponiveis` | `alugueis/formulario.html` | Nenhum equipamento ativo sem aluguel aberto | Aviso no lugar do formulário ou envio desabilitado | Serviço recusa aluguel de equipamento indisponível (RN001) |
| `sem_clientes` | `alugueis/formulario.html` | Nenhum cliente cadastrado | Aviso com link para cadastrar cliente | Serviço exige cliente existente (RN002) |

A devolução prevista mínima depende da retirada escolhida na própria tela; qualquer ajuste dinâmico em JavaScript é só informativo, e o backend valida "prevista igual ou posterior à retirada".

### 7.3 Atributos dos objetos

| Objeto | Atributos para exibição |
|--------|-------------------------|
| Equipamento (lista) | `nome`, `codigo`, `get_categoria_display`, `valor_diaria`, `ativo`, `disponivel` |
| Cliente (lista) | `nome_completo`, `cpf_formatado`, `telefone_formatado`, `email` |
| Aluguel (histórico e devolução) | `cliente`, `equipamento`, `data_retirada`, `data_devolucao_prevista`, `data_devolucao_real`, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado`, `situacao`, `situacao_codigo`, `pode_devolver` |

**Regras de apresentação:** botões só aparecem com a flag verdadeira; `situacao_codigo` serve só para o estilo do selo (o texto é `situacao`); estados vazios usam `empty_message` dentro de `{% empty %}`, sem dados inventados (CT04, CT16); sem paginação na v1; nenhum `|safe` em dado digitado; links sempre com `{% url %}`.

## 8. Divisão de arquivos

Cada arquivo tem **um** responsável. Ninguém edita arquivo do outro.

| Responsável | Arquivos |
|-------------|----------|
| **Rickelme (backend)** | `manage.py`, `config/**`, `*/models.py`, `*/forms.py`, `*/views.py`, `*/urls.py`, `*/services.py`, `*/admin.py`, `*/apps.py`, `*/migrations/**`, `*/tests/**`, dependências, `.env.example`, `CLAUDE.md`, `.claude/**` |
| **Raphael (frontend)** | `templates/**/*.html`, `static/css/**`, `static/js/**`, `static/img/**`, `static/vendor/bootstrap/**` (decisão conjunta) |
| **Ambos, via PR revisado pelos dois** | Este contrato e o guia de integração |

**Procedimento para pedir mudança em arquivo do outro:**

1. Descrever o pedido em comentário de PR ou mensagem: tela, rota, campo ou variável, exemplo de uso e motivo.
2. O responsável avalia e implementa na **própria** branch.
3. Se o contrato mudar, atualizar este documento numa branch `docs/*`, com revisão dos dois.
4. Até lá, a tela não depende do pedido: dado fictício só em HTML estático, nunca em código integrado.
5. Exceção (editar arquivo do outro) só com acordo explícito registrado no PR.

## 9. Regras aprovadas cobertas

| Regra (v1.1) | Onde aparece |
|--------------|--------------|
| CPF: remove só pontos e hífen, 11 dígitos armazenados, exibido formatado, imutável após o primeiro aluguel (RF005, RN002, I5) | 6.2; `cpf_formatado`, `cpf_editavel` |
| Retirada futura permitida e indisponibilidade imediata (RF006, D2/D6, I1) | 6.3; restrição de aluguel aberto na modelagem |
| Sem cancelamento; sem devolução antes da retirada (I1) | Nenhuma rota de cancelamento; `pode_devolver` |
| Sem edição de aluguel ou devolução (I2) | Nenhuma rota de edição; 6.4 |
| Diária congelada e diárias inclusivas (RN004, D3) | 6.3; calculado na gravação |
| Atraso sem multa (RN004 g, D4) | 6.4; situações do histórico |
| Datas em `America/Recife` (RN004 a, TZ) | `data_atual` e limites (7.2) |
| Exclusão só sem histórico; inativação sem aluguel ativo (RF004, RN003, D5) | Rotas de equipamento; flags de 7.2 |
| Reativação com dados válidos e sem aluguel ativo (RN003 e, N4, I3) | `pode_reativar`; teste complementar no plano |
| Login obrigatório e contas administrativas (D1) | Seção 3 |
| Histórico com cliente, equipamento, datas, diárias, valores e situação (RF008) | `alugueis/historico.html` |

## 10. Diferenças em relação ao guia de integração

| Guia (branch `docs/guia-integracao-raphael`) | Esta proposta | Motivo |
|----------------------------------------------|---------------|--------|
| `<app_autenticacao>:login` e `<app_autenticacao>:logout` | `login` e `logout`, nativos, sem namespace | Sem app de autenticação (seção 3) |
| Não lista página inicial | `inicio` e `inicio.html` | Página P01 |
| `clientes:detalhe` e `clientes/detalhe.html` | Removidos | A consulta de clientes é feita pela listagem |
| `equipamentos/confirmar_exclusao.html` | Confirmação dentro de `equipamentos/acoes.html` | Uma interface com ações condicionais, sem página extra |
| Ações de equipamento sem página definida | `equipamentos:acoes` (P04) | Interface única das ações condicionais |
| Bootstrap 5.3 local "dentro de `static/`" | Sugere `static/vendor/bootstrap/` | Separa biblioteca de terceiros do CSS próprio |

## 11. Pontos para validação de Rickelme e Raphael

**Validação conjunta:**

1. Apps e namespaces (`equipamentos`, `clientes`, `alugueis`), página inicial em `config` e autenticação sem app própria.
2. Caminhos, nomes, views e redirecionamentos da tabela final (seção 5).
3. Lista dos 14 templates, blocos de `base.html` e includes.
4. Nomes das variáveis de contexto e dos atributos (seções 7.2 e 7.3).
5. Forma da confirmação de exclusão dentro de `equipamentos/acoes.html` (modal ou bloco de confirmação).
6. Classes do Bootstrap aplicadas pelos widgets do backend.
7. Local e responsável pelos arquivos do Bootstrap em `static/vendor/bootstrap/`.
8. Adoção ou não da etapa opcional de revisão no registro de aluguel.

**Decisão de Rickelme (requisitos e backend):**

9. Inativação de equipamento **sem** histórico: permitida ou apenas exclusão (RF004 e RN003 b citam a inativação "com histórico")?
10. Normalização e sensibilidade a maiúsculas do código do equipamento.
11. Caracteres removidos na normalização do telefone e recusa de CPF com todos os dígitos iguais.
12. Uso do Django Admin para o provisionamento de contas.
13. Conferência da tabela de mensagens do EQF-5 e substituição dos textos provisórios.

## 12. Aceite

Este documento não vale como contrato até o aceite registrado dos dois.

- Rickelme — revisão e aprovação: **pendente**.
- Raphael — revisão e aprovação: **pendente**.
