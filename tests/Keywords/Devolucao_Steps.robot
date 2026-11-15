*** Settings ***
Library           Browser
Library           String
Library           DateTime
Resource          ../Pages/Devolucao_Page.robot

*** Keywords ***
Devolucao Deve Estar Aberta
    Wait For Elements State    ${DEVOLUCAO_TITULO}    visible

Devolucao Deve Exibir Dado Do Aluguel
    [Documentation]    Confere um item do quadro "Aluguel" pelo rótulo (ex.: Equipamento, Valor contratado, Situação).
    [Arguments]    ${rotulo}    ${esperado}
    ${dado}=    Format String    ${DEVOLUCAO_DADO_DO_ALUGUEL}    rotulo=${rotulo}
    Get Text    ${dado}    ==    ${esperado}

Informar Data De Devolucao Como Hoje
    [Documentation]    Usa a data atual do servidor (limite máximo do campo). Devolve a data em dd/mm/aaaa.
    ${hoje}=    Get Attribute    ${DEVOLUCAO_INPUT_DATA}    max
    Fill Text    ${DEVOLUCAO_INPUT_DATA}    ${hoje}
    ${hoje_br}=    Convert Date    ${hoje}    result_format=%d/%m/%Y    date_format=%Y-%m-%d
    RETURN    ${hoje_br}

Confirmar Devolucao
    Click    ${DEVOLUCAO_BOTAO_CONFIRMAR}
