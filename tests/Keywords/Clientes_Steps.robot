
*** Settings ***
Library           Browser
Library           String
Resource          ../Pages/Clientes_Page.robot

*** Keywords ***
Clientes Deve Estar Aberto
    Wait For Elements State    ${CLIENTES_TITULO}    visible

Acessar Novo Cliente
    Click    ${CLIENTES_LINK_NOVO}

Pesquisar Clientes
    [Arguments]    ${termo}
    Fill Text    ${CLIENTES_INPUT_PESQUISA}    ${termo}
    Click    ${CLIENTES_BOTAO_PESQUISAR}
    Clientes Deve Estar Aberto

Cliente Deve Aparecer Na Lista
    [Arguments]    ${nome}
    ${linha}=    Format String    ${CLIENTES_LINHA_DO_NOME}    nome=${nome}
    Wait For Elements State    ${linha}    visible
    Get Element Count    ${linha}    ==    1

Clientes Deve Ter Quantidade De Linhas
    [Arguments]    ${quantidade}
    Get Element Count    ${CLIENTES_LINHAS}    ==    ${quantidade}

Pesquisa Deve Exibir Mensagem De Ausencia
    [Arguments]    ${mensagem}
    Wait For Elements State    ${CLIENTES_VAZIO_TITULO}    visible
    Get Text    ${CLIENTES_VAZIO_TITULO}    ==    ${mensagem}
    Get Element Count    ${CLIENTES_LINHAS}    ==    0
