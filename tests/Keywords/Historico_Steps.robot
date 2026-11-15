*** Settings ***
Library           Browser
Resource          ../Pages/Historico_Page.robot

*** Keywords ***
Historico Deve Estar Aberto
    Wait For Elements State    ${HISTORICO_TITULO}    visible

Historico Nao Deve Ter Linhas
    Get Element Count    ${HISTORICO_LINHAS}    ==    0

Historico Deve Exibir Mensagem De Ausencia
    [Arguments]    ${titulo}    ${texto}
    Get Text    ${HISTORICO_VAZIO_TITULO}    ==    ${titulo}
    Get Text    ${HISTORICO_VAZIO_TEXTO}    ==    ${texto}

Historico Nao Deve Exibir Valores Nem Devolucao
    Get Text    ${HISTORICO_PAINEL_DE_RESULTADOS}    not contains    R$
    Get Element Count    ${HISTORICO_LINKS_DE_DEVOLUCAO}    ==    0
