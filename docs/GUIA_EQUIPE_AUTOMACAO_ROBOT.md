# Guia da equipe — automação CT01–CT20 com Robot Framework

Este guia permite que cada integrante implemente os seus cenários sozinho, no
padrão do projeto. A referência técnica curta da infraestrutura continua em
[`docs/testes-robot.md`](testes-robot.md).

> **Antes de começar, confira o que já está na `main`.** Este guia cita Pages e
> Keywords que podem ainda estar em revisão, na branch de outro integrante. Não
> presuma que o guia inteiro ou todas as keywords já foram integrados.
>
> 1. Atualize a referência remota: `git fetch origin`.
> 2. Veja o que existe em `origin/main`:
>    `git ls-tree -r --name-only origin/main tests scripts/robot/massas`.
> 3. Crie a sua branch a partir de `origin/main` (seção 4).
> 4. Se o seu cenário depende de uma Page ou keyword que ainda não está na
>    `main`, combine com o responsável antes de editar qualquer arquivo
>    compartilhado (seção 12) e espere o merge dele.

## 1. Objetivo acadêmico

A disciplina de Qualidade de Software exige a automação dos 20 cenários do
**Documento de Casos de Teste v1.4** (CT01–CT20) com Robot Framework, seguindo o
documento do professor "Automação - Projeto". O documento v1.4 é a fonte de
verdade: o cenário automatizado deve provar o que o caso de teste descreve.

Normas obrigatórias do professor:

| Camada | Onde | O que pode conter |
|---|---|---|
| Pages | `tests/Pages/<Tela>_Page.robot` | Só `*** Variables ***`, com XPaths. Nenhuma keyword. Um arquivo por tela. |
| Keywords | `tests/Keywords/<Tela>_Steps.robot` | `*** Settings ***` (importa as Pages) e `*** Keywords ***` com ações reutilizáveis. |
| Cenários | `tests/CenarioNN.robot` | `*** Settings ***` e `*** Test Cases ***`. Nenhum seletor: só chamadas de keywords. |

- Nunca duplique um XPath. Se o elemento mudar, a correção é feita em um só lugar.
- Um arquivo de cenário para cada caso de teste (`Cenario01.robot` … `Cenario20.robot`).

## 2. Tecnologias e pré-requisitos

Versões verificadas na máquina em que a infraestrutura foi validada:

| Ferramenta | Versão | Observação |
|---|---|---|
| Python | 3.13 | O projeto usa só o Python do `.venv`. |
| Node.js | 24 (mínimo 20) | Exigido pela biblioteca Browser. |
| Django | 5.2 | Vem de `requirements.txt`. |
| Robot Framework | 7.5.1 | `requirements-robot.txt`. |
| robotframework-browser | 21.0.0 | Biblioteca **Browser** (Playwright), não SeleniumLibrary. |
| Chromium | baixado pelo `rfbrowser` | Cerca de 200 MB; não usa o Chrome instalado. |
| Ruff e Black | `requirements-dev.txt` | Só se aplicam aos arquivos `.py` (as massas). |

Atenção: o exemplo do professor usa nomes de keywords da SeleniumLibrary
(`Input Text`, `Click Button`). Na biblioteca Browser os equivalentes são
`Fill Text`, `Click`, `Get Text`, `Get Element Count`, `Select Options By` e
`Wait For Elements State`.

## 3. Preparação do repositório

No PowerShell, uma vez por máquina:

```powershell
git clone https://github.com/RickelmeDSC/equipafacil.git
cd equipafacil
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements-robot.txt
rfbrowser init chromium
```

Quem já tem o repositório só precisa atualizar e instalar as duas últimas dependências:

```powershell
git fetch origin
python -m pip install -r requirements-robot.txt
rfbrowser init chromium
```

Confirme o ambiente rodando o cenário que já está na `main`:

```powershell
python scripts/robot/executar.py tests/Cenario16.robot
```

O resultado esperado é `1 test, 1 passed, 0 failed`. Não é preciso criar `.env`
nem banco: o script cuida disso.

## 4. Como criar sua branch

Nunca desenvolva na `main`. Crie a sua branch a partir de `origin/main` atualizada:

```powershell
git fetch origin
git switch -c <nome-da-sua-branch> origin/main
```

O nome de cada branch está na seção 6. Para trazer o que entrou na `main` depois:

```powershell
git fetch origin
git merge origin/main
```

Não use `git reset --hard`, `git clean`, `git push --force` nem worktrees.

## 5. Organização das pastas

```
tests/
├── Pages/                  um arquivo por tela, só variáveis com XPaths
├── Keywords/               um _Steps.robot por tela, com as ações
└── CenarioNN.robot         um arquivo por caso de teste
scripts/robot/
├── executar.py             sobe o servidor isolado e roda o Robot
├── massa.py                zera o banco isolado e chama a massa do cenário
├── massas/ctNN.py          massa fictícia de cada cenário
├── controles/              verificações técnicas fora da suíte oficial
└── settings_robot.py       configuração do Django só para a automação
resultados-robot/           relatórios e banco isolado (fora do Git)
```

- **`tests/Pages/`** — variáveis globais; por isso todo nome leva o prefixo da
  tela (`EQUIPAMENTOS_...`, `CLIENTES_...`). Uma variável pode reutilizar outra
  (`${MENU_NAVEGACAO}//a[...]`). Para um seletor que depende de um dado do
  cenário, use um marcador entre chaves e a keyword `Format String`
  (veja `Historico_Page.robot` e `Historico_Steps.robot`).
- **`tests/Keywords/`** — as ações de cada tela. O cenário só enxerga keywords.
- **`tests/CenarioNN.robot`** — começa com `Test Setup    Iniciar Cenario    ctNN`
  e termina com `Test Teardown    Encerrar Cenario`.
- **`scripts/robot/massas/ctNN.py`** — função `preparar()`. O banco chega vazio,
  só com o usuário de teste; a massa é recriada a cada cenário, então um cenário
  nunca depende de outro.
- **`scripts/robot/executar.py`** — único jeito de rodar os testes.
- **`resultados-robot/`** — `report.html`, `log.html`, `output.xml`,
  `servidor.log` e o banco `robot.sqlite3`. Nada disso é versionado.

## 6. Divisão oficial

| Integrante | Cenários | Branch |
|---|---|---|
| Rickelme David | CT11, CT12, CT13 | `test/robot-ct11-ct13-rickelme` |
| Vinícius Soares | CT02, CT04, CT06, CT08 | `test/robot-ct02-ct08-vinicius` |
| Rafael Ferreira | CT01, CT03, CT05, CT07 | `test/robot-ct01-ct07-rafael` |
| Alexandre Abreu | CT09, CT10, CT17, CT18 | `test/robot-ct09-ct18-alexandre` |
| Raphael Eloi | CT14, CT15 e revisão do CT16 existente | `test/robot-ct14-ct16-raphael` |
| Ivisson Virginio | CT19, CT20 e apoio à integração | `test/robot-ct19-ct20-ivisson` |

## 7. Instruções individuais

Vale para todos:

- **Comando:** `python scripts/robot/executar.py tests/CenarioNN.robot`.
- **Critério de aprovação:** o cenário passa sozinho, com massa própria, prova o
  resultado esperado do documento v1.4 e não tem seletor no arquivo de cenário.
- **Reutilize:** `Common_Steps.robot` (`Iniciar Cenario`, `Encerrar Cenario`),
  `Login_Steps.robot` (`Entrar Como Funcionario`) e `Home_Steps.robot`
  (`Acessar Equipamentos`, `Acessar Clientes`, `Acessar Novo Aluguel`,
  `Acessar Historico` e, depois do merge da branch do Rickelme,
  `Mensagem De Sucesso Deve Ser`).
- **Seletores:** os XPaths abaixo são sugestões escritas a partir dos templates
  do Django (`templates/`). Os de Equipamentos, Clientes e do alerta de
  devolução **ainda não foram executados**: cada integrante valida os seus na
  tela, rodando o cenário, antes de considerar o seletor correto.
- **Nenhum XPath repetido entre Pages.** Telas diferentes têm elementos
  parecidos (tabela, mensagem de lista vazia, botão "Salvar", campo `id_q`). Por
  isso cada sugestão abaixo é ancorada em algo que só existe naquela tela — o
  endereço do formulário, o cabeçalho da tabela ou um campo do formulário. Não
  copie um XPath de outra Page, nem crie um igual ao de outra Page.
- Para a célula de uma linha, componha a variável a partir da variável da linha
  (`${EQUIPAMENTOS_LINHA_DO_CODIGO}/td[4]`), em vez de declarar `/td[4]` sozinho.
- **Textos esperados:** são os de `config/mensagens.py`. Compare com `==`, não
  com `contains`, sempre que possível.
- Os campos de formulário do Django têm `id="id_<campo>"`, e o erro de cada
  campo fica em `//div[@id='id_<campo>_error']`.

### 7.1 Rafael Ferreira — CT01, CT03, CT05, CT07

Rafael é o responsável pelas telas de **Equipamentos** e cria os arquivos-base
`Equipamentos_Page.robot` e `Equipamentos_Steps.robot`, que o Vinícius vai
reutilizar. Sugestão: uma Page e um Steps por tela — lista
(`Equipamentos_*`), formulário (`Equipamento_Form_*`) e ações
(`Equipamento_Acoes_*`).

Seletores sugeridos:

| Tela | Variável | XPath |
|---|---|---|
| Lista | `EQUIPAMENTOS_TITULO` | `//h1[normalize-space()='Equipamentos']` |
| Lista | `EQUIPAMENTOS_LINK_NOVO` | `//div[contains(@class,'eqf-cabecalho-da-pagina')]//a[normalize-space()='Novo equipamento']` |
| Lista | `EQUIPAMENTOS_FORM_PESQUISA` | `//form[@action='/equipamentos/']` |
| Lista | `EQUIPAMENTOS_INPUT_PESQUISA` | `${EQUIPAMENTOS_FORM_PESQUISA}//input[@name='q']` |
| Lista | `EQUIPAMENTOS_BOTAO_PESQUISAR` | `${EQUIPAMENTOS_FORM_PESQUISA}//button[@type='submit']` |
| Lista | `EQUIPAMENTOS_LINHAS` | `//table[thead//th[normalize-space()='Código']]/tbody/tr` |
| Lista | `EQUIPAMENTOS_LINHA_DO_CODIGO` | `${EQUIPAMENTOS_LINHAS}\[td[1][normalize-space()='{codigo}']]` |
| Lista | células da linha | `${EQUIPAMENTOS_LINHA_DO_CODIGO}/td[2]` nome, `/td[3]` categoria, `/td[4]` diária, `/td[5]` situação, `/td[6]` disponibilidade |
| Lista | links da linha | `${EQUIPAMENTOS_LINHA_DO_CODIGO}//a[normalize-space()='Editar']` e `${EQUIPAMENTOS_LINHA_DO_CODIGO}//a[normalize-space()='Ações']` |
| Lista | `EQUIPAMENTOS_VAZIO_TITULO` | `//div[contains(@class,'eqf-vazio')][a[contains(@href,'/equipamentos/')]]/p[contains(@class,'eqf-vazio-titulo')]` |
| Formulário | campos | `//input[@id='id_codigo']`, `//input[@id='id_nome']`, `//select[@id='id_categoria']`, `//input[@id='id_valor_diaria']`, `//textarea[@id='id_descricao']` |
| Formulário | `EQUIPAMENTO_FORM_BOTAO_SALVAR` | `//form[.//input[@id='id_codigo']]//button[@type='submit']` |
| Formulário | erros | `//div[@id='id_codigo_error']`, `//div[@id='id_valor_diaria_error']` |
| Ações | abrir confirmação | `//summary[normalize-space()='Excluir equipamento']` |
| Ações | confirmar | `//button[@type='submit' and normalize-space()='Confirmar exclusão']` |
| Ações | botão bloqueado | `//button[@disabled and normalize-space()='Excluir equipamento']` |
| Ações | motivo do bloqueio da exclusão | `//div[contains(@class,'eqf-acao-bloqueada')][button[normalize-space()='Excluir equipamento']]/p[contains(@class,'eqf-motivo-do-bloqueio')]` |
| Ações | inativação liberada | `//button[@type='submit' and normalize-space()='Inativar equipamento']` |

Observações sobre essas sugestões:

- A lista vazia tem dois links "Novo equipamento" (no cabeçalho e no quadro de
  vazio); por isso o link é ancorado no cabeçalho da página.
- A tela de Ações pode mostrar até três motivos de bloqueio (inativar, reativar
  e excluir); por isso o motivo é ancorado no botão "Excluir equipamento".
- O tipo do campo de descrição (`textarea`) e o endereço `/equipamentos/` do
  formulário de pesquisa foram deduzidos do código, não vistos em execução:
  confirme na tela.
- Na Page, o `[` logo depois de uma variável precisa de barra invertida
  (`${EQUIPAMENTOS_LINHAS}\[td...`), senão o Robot entende como índice de lista.

**CT01 — Cadastrar equipamento válido (RF001; Smoke, Regression)**
- Pré-condição: nenhum equipamento. Massa `ct01.py` com `preparar()` vazia.
- Passos: Equipamentos → Novo equipamento → nome "Furadeira Impacto", código
  "FUR-001", categoria "Ferramentas", diária "50,00", descrição "Furadeira
  profissional" → Salvar.
- Esperado: mensagem "Equipamento cadastrado com sucesso."; a lista mostra
  FUR-001 com situação "Ativo" e disponibilidade "Disponível".
- Arquivos: `Cenario01.robot`, `massas/ct01.py`, Pages e Steps de Equipamentos.

**CT03 — Consultar equipamento e verificar disponibilidade (RF002; Smoke, Regression)**
- Massa: FUR-001 "Furadeira Impacto" (Ferramentas, R$ 50,00) disponível. Para
  provar a disponibilidade calculada, vale incluir um segundo equipamento com
  aluguel ativo (`registrar(...)`), que deve aparecer como "Indisponível".
- Passos: pesquisar "FUR-001" e depois "Furadeira".
- Esperado: nas duas pesquisas a linha mostra nome, código, categoria,
  "R$ 50,00", "Ativo" e "Disponível".

**CT05 — Editar equipamento sem alterar aluguéis anteriores (RF003; Regression)**
- Massa: FUR-001 a R$ 50,00 com um aluguel de 3 diárias (R$ 150,00). Use
  `registrar(equipamento=..., cliente=..., prevista=dias(2))`; para o aluguel ser
  "anterior", encerre-o com `alugueis.services.registrar_devolucao`.
- Passos: Equipamentos → Editar FUR-001 → diária "60,00" → Salvar.
- Esperado: mensagem "Equipamento atualizado com sucesso."; a lista mostra
  "R$ 60,00"; no Histórico o aluguel continua com diária "R$ 50,00" e valor
  "R$ 150,00".
- Reutilize `Historico Deve Exibir Aluguel` (depois do merge da branch do Rickelme).

**CT07 — Excluir equipamento sem histórico (RF004; Regression)**
- Massa: um equipamento sem aluguel.
- Passos: Equipamentos → Ações → "Excluir equipamento" (abre a confirmação) →
  "Confirmar exclusão".
- Esperado: mensagem "Equipamento excluído com sucesso."; a pesquisa pelo código
  retorna "Nenhum registro encontrado.".
- Cuidado: "Excluir equipamento" é um `<summary>`; só depois de clicar nele o
  botão "Confirmar exclusão" fica visível.

Dependências: nenhuma para CT01, CT03 e CT07; o CT05 usa o Histórico.

### 7.2 Vinícius Soares — CT02, CT04, CT06, CT08

Vinícius reutiliza as Pages e Steps de Equipamentos criadas pelo Rafael. Comece
depois que o PR-base do Rafael (CT01 e CT03) entrar na `main`; enquanto isso,
adiante as massas `ct02.py`, `ct04.py`, `ct06.py` e `ct08.py`, que não conflitam.
Se precisar de um seletor ou keyword novo em arquivo do Rafael, peça a ele
(seção 12).

**CT02 — Impedir cadastro com código duplicado (RF001; Regression)**
- Massa: FUR-001 já cadastrado.
- Passos: Novo equipamento com o mesmo código "FUR-001" e os demais dados válidos → Salvar.
- Esperado: a tela continua no formulário, com "Já existe um equipamento com este
  código." em `id_codigo_error`; a lista continua com um único FUR-001.

**CT04 — Pesquisar equipamento inexistente (RF002; Regression)**
- Massa: pelo menos um equipamento, para o vazio ser efeito da pesquisa.
- Passos: pesquisar "EQUIPAMENTO_FANTASMA_999".
- Esperado: "Nenhum registro encontrado." e nenhuma linha na tabela.

**CT06 — Impedir edição com diária de R$ 0,00 (RF003; Regression)**
- Massa: FUR-001 a R$ 50,00.
- Passos: Editar → diária "0,00" → Salvar.
- Esperado: a tela continua no formulário, com "O valor da diária deve ser maior
  que R$ 0,00 e ter no máximo duas casas decimais." em `id_valor_diaria_error`; a
  lista continua mostrando "R$ 50,00".

**CT08 — Impedir exclusão de equipamento com histórico (RF004; Regression)**
- Massa: equipamento com um aluguel já encerrado (sem aluguel ativo).
- Passos: Equipamentos → Ações.
- Esperado: "Excluir equipamento" desabilitado, com o motivo "Não é possível
  excluir: equipamento com histórico de locação. Utilize a inativação."; o botão
  "Inativar equipamento" habilitado.
- Cuidado: a tela não deixa enviar a exclusão (o botão fica desabilitado). O
  cenário prova o bloqueio pela interface. Não substitua o teste por uma chamada
  direta ao servidor sem combinar com a equipe e registrar a decisão.

### 7.3 Alexandre Abreu — CT09, CT10, CT17, CT18

Alexandre é o responsável pelas telas de **Clientes** e cria
`Clientes_Page.robot`, `Clientes_Steps.robot` e os arquivos do formulário
(`Cliente_Form_*`). Não depende de ninguém.

Seletores sugeridos:

| Tela | Variável | XPath |
|---|---|---|
| Lista | `CLIENTES_TITULO` | `//h1[normalize-space()='Clientes']` |
| Lista | `CLIENTES_LINK_NOVO` | `//div[contains(@class,'eqf-cabecalho-da-pagina')]//a[normalize-space()='Novo cliente']` |
| Lista | `CLIENTES_FORM_PESQUISA` | `//form[@action='/clientes/']` |
| Lista | `CLIENTES_INPUT_PESQUISA` | `${CLIENTES_FORM_PESQUISA}//input[@name='q']` |
| Lista | `CLIENTES_BOTAO_PESQUISAR` | `${CLIENTES_FORM_PESQUISA}//button[@type='submit']` |
| Lista | `CLIENTES_LINHAS` | `//table[thead//th[normalize-space()='Nome completo']]/tbody/tr` |
| Lista | `CLIENTES_LINHA_DO_NOME` | `${CLIENTES_LINHAS}\[td[1][normalize-space()='{nome}']]` |
| Lista | células da linha | `${CLIENTES_LINHA_DO_NOME}/td[2]` CPF, `/td[3]` telefone, `/td[4]` e-mail |
| Lista | `CLIENTES_VAZIO_TITULO` | `//div[contains(@class,'eqf-vazio')][a[contains(@href,'/clientes/')]]/p[contains(@class,'eqf-vazio-titulo')]` |
| Formulário | campos | `//input[@id='id_nome_completo']`, `//input[@id='id_cpf']`, `//input[@id='id_telefone']`, `//input[@id='id_email']` |
| Formulário | `CLIENTE_FORM_BOTAO_SALVAR` | `//form[.//input[@id='id_nome_completo']]//button[@type='submit']` |
| Formulário | erro do CPF | `//div[@id='id_cpf_error']` |

O campo de pesquisa de Clientes e o de Equipamentos têm o mesmo `id="id_q"`. Por
isso os dois são ancorados no formulário da própria tela (`/clientes/` e
`/equipamentos/`), e não declarados pelo `id`. O endereço `/clientes/` foi
deduzido do código: confirme na tela.

**CT09 — Cadastrar cliente válido (RF005; Smoke, Sanity, Regression)**
- Massa: `ct09.py` com `preparar()` vazia.
- Passos: Clientes → Novo cliente → nome "João Silva", CPF "529.982.247-25",
  telefone e e-mail vazios → Salvar.
- Esperado: "Cliente cadastrado com sucesso."; a lista mostra "João Silva" com
  CPF "529.982.247-25" e "—" em telefone e e-mail.

**CT10 — Impedir cadastro de CPF duplicado (RF005; Regression)**
- Massa: `criar_cliente(nome_completo="João Silva", cpf="52998224725")`.
- Passos: Novo cliente com outro nome e o mesmo CPF "529.982.247-25" → Salvar.
- Esperado: a tela continua no formulário, com "Já existe um cliente com este
  CPF." em `id_cpf_error`; a lista continua com um único cliente.

**CT17 — Pesquisar cliente por nome (RF009; Sanity, Regression)**
- Massa: "Maria QA Pesquisa" (use `criar_cliente(nome_completo=...)`, que gera um
  CPF fictício válido) e "João Silva".
- Passos: Clientes → pesquisar "maria qa".
- Esperado: a linha de "Maria QA Pesquisa" aparece com o CPF no formato
  `000.000.000-00`; "João Silva" não aparece; o campo de pesquisa continua com
  "maria qa" (`Get Property    ${CLIENTES_INPUT_PESQUISA}    value`).

**CT18 — Pesquisar cliente inexistente (RF009; Sanity, Regression)**
- Massa: pelo menos um cliente.
- Passos: pesquisar "CLIENTE_FANTASMA_999".
- Esperado: "Nenhum registro encontrado." e nenhuma linha.

Cuidados: o CPF "529.982.247-25" é o exemplo fictício do documento; não use CPF
de pessoa real. Para outros clientes, deixe a fábrica gerar o CPF.

### 7.4 Raphael Eloi — CT14, CT15 e revisão do CT16

Raphael é o responsável pela tela de **Histórico** (`Historico_Page.robot` e
`Historico_Steps.robot`), com contribuição coordenada do Ivisson.

**Revisão do CT16.** O CT16 está na `main` e ainda não teve revisão pessoal.
Confira `tests/Cenario16.robot` contra o documento v1.4, rode
`python scripts/robot/executar.py tests/Cenario16.robot` e o controle negativo
`python scripts/robot/executar.py scripts/robot/controles/Controle_CT16.robot`,
e registre o seu parecer no PR ou em comentário próprio.

**CT15 — Consultar histórico de aluguéis (RF008; Smoke, Sanity, Regression)**
- Massa: um aluguel em cada situação, cada um com um equipamento de código
  diferente. Exemplo, usando `alugueis.services.registrar_aluguel` e
  `registrar_devolucao` com o parâmetro `hoje` para simular registros antigos:
  - Ativo: retirada hoje, prevista `dias(2)`.
  - Atrasado: registrado em `dias(-3)`, prevista `dias(-1)`, sem devolução.
  - Encerrado: registrado ontem, prevista hoje, devolvido ontem.
  - Encerrado com atraso: registrado em `dias(-5)`, prevista `dias(-3)`,
    devolvido em `dias(-1)`.
- Passos: Histórico.
- Esperado: quatro linhas, cada uma com cliente, equipamento, datas, diárias,
  diária contratada, valor contratado e a situação correta.
- Reutilize (depois do merge da branch do Rickelme):
  `Historico Deve Ter Quantidade De Linhas`, `Historico Deve Exibir Aluguel`,
  `Historico Deve Exibir Periodo Do Aluguel` e
  `Historico Deve Exibir Devolucao Do Aluguel`.
- Veja `scripts/robot/massas/ct13.py` como exemplo de aluguel registrado "ontem".

**CT14 — Impedir devolução de aluguel já encerrado (RF007; Regression)**
- Problema: um aluguel encerrado não tem o link "Registrar devolução" no
  Histórico, então a segunda devolução não pode ser enviada pelo caminho normal.
- **A estratégia abaixo é uma proposta: ainda não foi validada em execução.**
  Foi conferida só na leitura do código da view e do template.
- Estratégia proposta (a mesma do CT12): massa com um aluguel **ativo**; abrir
  a tela de devolução em uma aba; em outra aba, registrar a devolução do mesmo
  aluguel; voltar à primeira aba e confirmar. A segunda devolução chega ao
  backend e é recusada.
- Esperado: "Este aluguel já foi encerrado."; o Histórico continua com uma única
  linha, situação "Encerrado" e a data da primeira devolução.
- Reutilize `Devolucao_Steps.robot` e `Abrir Devolucao Do Aluguel`. As keywords
  de aba estão em `Aluguel_Form_Steps.robot` (`Voltar Para A Aba Inicial`).
- O alerta de recusa precisa de uma variável nova em `Devolucao_Page.robot`
  (sugestão, pelo template `alugueis/devolver.html`:
  `//div[@role='alert' and contains(@class,'alert-warning')]`, a confirmar na
  tela) e de uma keyword nova em `Devolucao_Steps.robot`. Esses arquivos são
  do Rickelme: combine o acréscimo com ele.
- Se o sistema não recusar, registre FAIL com a evidência. Não altere o Django.

Dependências: branch do Rickelme (CT11–CT13) integrada à `main`.

### 7.5 Ivisson Virginio — CT19, CT20 e integração

Ivisson acrescenta as keywords de **filtro** ao Histórico, combinando com o
Raphael. As variáveis `HISTORICO_SELECT_SITUACAO` e `HISTORICO_BOTAO_FILTRAR` já
existem em `Historico_Page.robot`.

Keywords a criar em `Historico_Steps.robot` (sugestão):

```robotframework
Filtrar Historico Por Situacao
    [Arguments]    ${situacao}
    Select Options By    ${HISTORICO_SELECT_SITUACAO}    label    ${situacao}
    Click    ${HISTORICO_BOTAO_FILTRAR}

Filtro Do Historico Deve Estar Em
    [Arguments]    ${situacao}
    Get Selected Options    ${HISTORICO_SELECT_SITUACAO}    label    ==    ${situacao}
```

Para conferir a situação de todas as linhas, reutilize as variáveis que já
existem — `${HISTORICO_LINHAS}${HISTORICO_COLUNA_SITUACAO}` —, sem declarar um
XPath novo para a coluna. Use `Get Elements` com um `FOR`, ou conte as células
cujo texto é diferente do esperado e exija zero. Essas keywords ainda não
existem: valide-as em execução.

**CT19 — Filtrar histórico por situação (RF010; Sanity, Regression)**
- Massa: pelo menos um aluguel "Ativo" e um "Encerrado", em equipamentos diferentes.
- Passos: Histórico → filtrar "Encerrado".
- Esperado: só linhas "Encerrado"; nenhuma "Ativo"; o filtro continua em "Encerrado".
- Cuidado: "Encerrado" e "Encerrado com atraso" são situações diferentes.
  Compare o texto com `==`, nunca com `contains`.

**CT20 — Filtrar situação sem registros (RF010; Sanity, Regression)**
- Massa: aluguéis só em "Ativo" e "Encerrado".
- Passos: com o filtro em "Todas", conferir que nenhuma linha está em "Encerrado
  com atraso"; filtrar "Encerrado com atraso".
- Esperado: "Nenhum registro encontrado.", o texto "Escolha outra situação ou
  limpe o filtro para ver todos os aluguéis." e nenhuma linha.
- Reutilize `Historico Deve Exibir Mensagem De Ausencia` e
  `Historico Nao Deve Ter Linhas`, que já estão na `main`.

**Integração.** Depois que os 20 cenários estiverem na `main`:
`python scripts/robot/executar.py` (suíte inteira) e as suítes por tag
(`--include=Smoke`, `--include=Sanity`, `--include=Regression`). Confira que as
tags de cada cenário batem com a seção 5 do documento v1.4. O Robot só entra no
CI depois dessa validação, em tarefa própria.

Dependências: CT15 do Raphael na `main`, para os dois não editarem
`Historico_Steps.robot` ao mesmo tempo.

## 8. Como implementar um cenário

Os exemplos abaixo são os arquivos reais do CT13 (branch do Rickelme).

**Page** — `tests/Pages/Devolucao_Page.robot`:

```robotframework
*** Variables ***
${DEVOLUCAO_TITULO}             //h1[normalize-space()='Registrar devolução']
${DEVOLUCAO_DADO_DO_ALUGUEL}    //dl/dt[normalize-space()='{rotulo}']/following-sibling::dd[1]
${DEVOLUCAO_INPUT_DATA}         //input[@id='id_data_devolucao_real']
${DEVOLUCAO_BOTAO_CONFIRMAR}    //button[@type='submit' and normalize-space()='Confirmar devolução']
```

**Steps** — `tests/Keywords/Devolucao_Steps.robot` (trecho):

```robotframework
*** Settings ***
Library           Browser
Library           String
Library           DateTime
Resource          ../Pages/Devolucao_Page.robot

*** Keywords ***
Devolucao Deve Estar Aberta
    Wait For Elements State    ${DEVOLUCAO_TITULO}    visible

Devolucao Deve Exibir Dado Do Aluguel
    [Arguments]    ${rotulo}    ${esperado}
    ${dado}=    Format String    ${DEVOLUCAO_DADO_DO_ALUGUEL}    rotulo=${rotulo}
    Get Text    ${dado}    ==    ${esperado}

Confirmar Devolucao
    Click    ${DEVOLUCAO_BOTAO_CONFIRMAR}
```

**Cenário** — `tests/Cenario13.robot` (trecho):

```robotframework
*** Settings ***
Documentation     CT13 — Registrar devolução e liberar equipamento (RF007; RN001, RN004).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Resource          Keywords/Devolucao_Steps.robot
Test Setup        Iniciar Cenario    ct13
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT13 - Registrar devolucao e liberar equipamento
    [Tags]    CT13    RF007    RN001    RN004    Smoke    Regression
    Entrar Como Funcionario
    Acessar Historico
    Abrir Devolucao Do Aluguel    FUR-001
    Devolucao Deve Estar Aberta
    ${devolucao}=    Informar Data De Devolucao Como Hoje
    Confirmar Devolucao
    Mensagem De Sucesso Deve Ser    Devolução registrada com sucesso.
```

**Massa** — `scripts/robot/massas/ct13.py`:

```python
from decimal import Decimal

from alugueis.services import registrar_aluguel
from config.tests.fabricas import criar_cliente, criar_equipamento, dias


def preparar() -> None:
    cliente = criar_cliente(nome_completo="João Silva", cpf="52998224725")
    equipamento = criar_equipamento(
        codigo="FUR-001", nome="Furadeira Impacto", valor_diaria=Decimal("50.00")
    )
    ontem = dias(-1)
    registrar_aluguel(
        cliente_id=cliente.pk,
        equipamento_id=equipamento.pk,
        data_retirada=ontem,
        data_devolucao_prevista=dias(1),
        hoje=ontem,
    )
```

Regras práticas:

- **Tags:** `CTNN`, o RF, as RNs e as suítes da seção 5 do documento v1.4.
- **Datas:** as datas fixas do documento já passaram, e o sistema recusa retirada
  no passado. Use datas relativas à execução (`dias(n)` na massa; na tela, leia a
  data do próprio campo, como em `Aluguel_Form_Steps.robot`) e registre a
  adaptação na `Documentation` do cenário.
- **Fábricas** (`config/tests/fabricas.py`): `criar_equipamento`, `criar_cliente`,
  `registrar`, `dias`, `hoje`. Não crie aluguel gravando direto no modelo: use os
  serviços, que aplicam as regras reais.
- **Negativos:** prove que a operação foi enviada e recusada, e que nada foi
  gravado (por exemplo, a quantidade de linhas não mudou).
- **Não altere o Django** para o teste passar. Se o comportamento real não
  atender ao documento, o resultado é FAIL, com evidência.

## 9. Segurança

- Rode só pelo `executar.py`, que usa `127.0.0.1` e o banco
  `resultados-robot/robot.sqlite3`. `Exigir Ambiente Local` recusa outro endereço
  e `massa.py` recusa apagar dados fora do banco isolado.
- Nunca aponte os testes para o Render nem para o Neon.
- Só dados fictícios; nenhum dado pessoal real.
- Nenhuma credencial no código: usuário e senha são gerados a cada execução.
- Não versione `resultados-robot/`, bancos, relatórios, `.env` nem capturas com
  dados sensíveis.
- Não use comandos destrutivos de Git (`reset --hard`, `clean`, `push --force`)
  e não apague branches dos colegas.

## 10. Execução dos testes

```powershell
python scripts/robot/executar.py tests/Cenario11.robot                          # um cenário
python scripts/robot/executar.py tests/Cenario11.robot tests/Cenario12.robot    # vários
python scripts/robot/executar.py                                                # suíte completa
python scripts/robot/executar.py --include=Smoke                                # por tag
python scripts/robot/executar.py --visivel tests/Cenario11.robot                # navegador na tela
```

- Opções do Robot que recebem valor precisam do sinal de igual
  (`--include=Smoke`). Com espaço (`--include Smoke`), o script entende `Smoke`
  como um arquivo de teste e a execução termina com erro.
- Não rode `robot` diretamente nem duas execuções ao mesmo tempo (elas dividiriam
  o mesmo banco). Se a porta 8765 estiver ocupada, use `--porta`.
- Resultados em `resultados-robot/`: abra `report.html` para o resumo e
  `log.html` para o passo a passo.

Diagnóstico de falhas:

| Sintoma | O que verificar |
|---|---|
| "Falha ao preparar a massa" | Erro no seu `ctNN.py`; a mensagem do Python aparece no `log.html`. |
| `Timeout ... waiting for locator` | O XPath não encontrou o elemento. Rode com `--visivel` e veja a captura de tela no `log.html`. |
| `strict mode violation` | O XPath encontrou mais de um elemento. Deixe o seletor mais específico. |
| Texto diferente do esperado | Compare com o texto de `config/mensagens.py` e com o template. |
| "O servidor de teste não iniciou" | Veja `resultados-robot/servidor.log`. |
| Opção de `<select>` não encontrada | Selecione pelo `value` da opção, como em `Aluguel_Form_Steps.robot`. |

## 11. Padrão de commits e PRs

Siga o `CLAUDE.md` do projeto.

1. Trabalhe só na sua branch (seção 6), com a sua própria conta do GitHub.
2. Antes de cada commit: `ruff check .` e `black --check .`.
3. Adicione só os arquivos previstos, um a um — nunca `git add .`:

   ```powershell
   git add tests/Cenario09.robot scripts/robot/massas/ct09.py tests/Pages/Clientes_Page.robot tests/Keywords/Clientes_Steps.robot
   git status
   ```

4. Commit semântico, em português: `test: automatiza o CT09`.
5. `git push -u origin <sua-branch>` (push normal).
6. Abra o PR contra a `main`.

A descrição do PR deve informar:

- cenários entregues e requisitos cobertos;
- arquivos criados e arquivos compartilhados alterados;
- adaptações em relação ao documento v1.4, com o motivo;
- comando executado e resultado (PASS ou FAIL real), com a data;
- evidência: trecho da saída do terminal ou captura do `report.html`;
- quem executou. Não atribua a outra pessoa uma execução ou revisão que ela não
  fez; se usou assistente de IA, diga o que foi gerado e o que você conferiu.

Ninguém faz merge do próprio PR sem autorização do responsável pelo projeto.

## 12. Arquivos compartilhados e conflitos

| Arquivos | Responsável principal | Contribuição coordenada |
|---|---|---|
| `Login_*`, `Home_*`, `Common_Steps.robot`, `scripts/robot/*.py` | Rickelme | — |
| Equipamentos | Rafael | Vinícius |
| Clientes | Alexandre | — |
| Aluguel (`Aluguel_Form_*`) | Rickelme | — |
| Devolução (`Devolucao_*`) | Rickelme | Raphael |
| Histórico (`Historico_*`) | Raphael | Ivisson |

Os arquivos `CenarioNN.robot` e `massas/ctNN.py` são de quem tem o cenário e
nunca conflitam.

Como pedir uma mudança em arquivo de outra pessoa:

1. Procure nas Pages e nos Steps se o seletor ou a keyword já existe.
2. Se não existir, avise o responsável no grupo: qual arquivo, qual variável ou
   keyword e para qual cenário.
3. O responsável faz o acréscimo, ou autoriza você a fazer em um PR pequeno, só
   com essa mudança.
4. Depois do merge, atualize a sua branch com `git merge origin/main`.

Regras para não conflitar:

- Só acrescente; não renomeie, reordene nem apague o que outros usam.
- Duas pessoas não editam o mesmo arquivo ao mesmo tempo: combinem a ordem.
- Não altere `Common_Steps.robot`, `executar.py`, `massa.py` nem
  `settings_robot.py` sem combinar com o Rickelme.

Ordem recomendada:

1. Rickelme (CT11–CT13), Rafael (CT01, CT03), Alexandre (CT09) e Raphael
   (revisão do CT16).
2. Vinícius (CT02, CT04), Rafael (CT05, CT07), Alexandre (CT10, CT17, CT18) e
   Raphael (CT15).
3. Vinícius (CT06, CT08), Raphael (CT14) e Ivisson (CT19, CT20).
4. Ivisson: integração da suíte completa.

## 13. Checklist de entrega individual

- [ ] Todos os meus cenários têm `CenarioNN.robot` e `massas/ctNN.py`.
- [ ] A massa é fictícia e criada só no banco isolado.
- [ ] As Pages têm só variáveis; os cenários não têm seletores; nenhum XPath repetido.
- [ ] Rodei cada cenário sozinho e todos os meus cenários juntos.
- [ ] Rodei o CT16 para confirmar que não quebrei a infraestrutura.
- [ ] Tenho a evidência do resultado real (PASS ou FAIL) de cada cenário.
- [ ] `ruff check .` e `black --check .` passaram.
- [ ] Não há senha, token, `.env`, banco ou relatório no commit.
- [ ] O commit tem só os arquivos previstos.
- [ ] O PR está aberto contra a `main`, com a descrição completa.
- [ ] Não fiz merge sem autorização.

## 14. Processo de auditoria final

Depois da entrega, cada PR é revisado antes do merge. A auditoria verifica:

- **Código:** legibilidade, reutilização e ausência de lógica repetida.
- **Regras do professor:** estrutura de pastas, Pages só com variáveis, cenários
  sem seletores, nenhum XPath duplicado.
- **Correspondência com o documento v1.4:** pré-condições, passos, resultado
  esperado e tags; adaptações registradas.
- **Execução real:** cada cenário é rodado de novo, sozinho e em conjunto.
- **Segurança:** ambiente local, banco isolado, nenhum segredo.
- **Conflitos:** mudanças em arquivos compartilhados combinadas com o responsável.
- **Regressões:** os cenários que já estavam na `main` continuam passando.
- **Integração:** a suíte completa roda de uma vez.

Um cenário não é considerado aprovado só porque o arquivo existe: ele precisa
passar em execução real, com evidência.
