*** Settings ***
Library           Browser
Library           String
Resource          ../Pages/Equipamentos_Page.robot

*** Keywords ***
Equipamentos Deve Estar Aberto
    Wait For Elements State    ${EQUIPAMENTOS_TITULO}    visible

Acessar Novo Equipamento
    Click    ${EQUIPAMENTOS_LINK_NOVO}

Pesquisar Equipamento
    [Documentation]    Pesquisa por código ou nome e espera a lista recarregar com o termo no endereço.
    [Arguments]    ${termo}
    Fill Text    ${EQUIPAMENTOS_INPUT_PESQUISA}    ${termo}
    Click    ${EQUIPAMENTOS_BOTAO_PESQUISAR}
    Wait For Condition    Url    contains    q=
    Equipamentos Deve Estar Aberto
    Get Property    ${EQUIPAMENTOS_INPUT_PESQUISA}    value    ==    ${termo}

Equipamentos Deve Ter Quantidade De Linhas
    [Arguments]    ${quantidade}
    Get Element Count    ${EQUIPAMENTOS_LINHAS}    ==    ${quantidade}

Equipamento Deve Aparecer Na Lista
    [Documentation]    Confere a linha do código (exatamente uma) e todas as colunas de dados.
    [Arguments]    ${codigo}    ${nome}    ${categoria}    ${diaria}    ${situacao}    ${disponibilidade}
    ${linha}=    Format String    ${EQUIPAMENTOS_LINHA_DO_CODIGO}    codigo=${codigo}
    Get Element Count    ${linha}    ==    1
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_NOME}    ${codigo}    ${nome}
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_CATEGORIA}    ${codigo}    ${categoria}
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_DIARIA}    ${codigo}    ${diaria}
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_SITUACAO}    ${codigo}    ${situacao}
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_DISPONIBILIDADE}    ${codigo}    ${disponibilidade}

Celula Do Equipamento Deve Ser
    [Documentation]    Compara o texto de uma célula da linha do código informado.
    [Arguments]    ${celula}    ${codigo}    ${texto}
    ${seletor}=    Format String    ${celula}    codigo=${codigo}
    Get Text    ${seletor}    ==    ${texto}

Equipamento Nao Deve Aparecer Na Lista
    [Arguments]    ${codigo}
    ${linha}=    Format String    ${EQUIPAMENTOS_LINHA_DO_CODIGO}    codigo=${codigo}
    Get Element Count    ${linha}    ==    0

Lista De Equipamentos Deve Exibir Mensagem De Ausencia
    [Arguments]    ${mensagem}
    Get Text    ${EQUIPAMENTOS_VAZIO_TITULO}    ==    ${mensagem}
    Get Element Count    ${EQUIPAMENTOS_LINHAS}    ==    0

Acessar Edicao Do Equipamento
    [Arguments]    ${codigo}
    ${linha}=    Format String    ${EQUIPAMENTOS_LINHA_DO_CODIGO}    codigo=${codigo}
    Click    ${linha}${EQUIPAMENTOS_LINK_EDITAR_DA_LINHA}

Acessar Acoes Do Equipamento
    [Arguments]    ${codigo}
    ${linha}=    Format String    ${EQUIPAMENTOS_LINHA_DO_CODIGO}    codigo=${codigo}
    Click    ${linha}${EQUIPAMENTOS_LINK_ACOES_DA_LINHA}

A Pesquisa Deve Retornar Apenas Um Equipamento
    [Documentation]    Pesquisa pelo código, a partir da lista, e exige uma única linha, com esse código.
    [Arguments]    ${codigo}
    Pesquisar Equipamento    ${codigo}
    Equipamentos Deve Ter Quantidade De Linhas    1
    ${linha}=    Format String    ${EQUIPAMENTOS_LINHA_DO_CODIGO}    codigo=${codigo}
    Get Element Count    ${linha}    ==    1

A Lista Deve Estar Vazia
    [Arguments]    ${mensagem}=Nenhum registro encontrado.
    Lista De Equipamentos Deve Exibir Mensagem De Ausencia    ${mensagem}

A Lista Deve Exibir O Valor Da Diaria Do Equipamento
    [Arguments]    ${codigo}    ${valor}
    Equipamentos Deve Estar Aberto
    Celula Do Equipamento Deve Ser    ${EQUIPAMENTOS_CELULA_DIARIA}    ${codigo}    ${valor}
