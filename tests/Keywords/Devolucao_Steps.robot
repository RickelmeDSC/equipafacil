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

Informar Data De Devolucao Como Data Da Retirada
    [Documentation]    Usa a data de retirada do aluguel (limite mínimo do campo). Devolve a data em dd/mm/aaaa.
    ${retirada}=    Get Attribute    ${DEVOLUCAO_INPUT_DATA}    min
    Fill Text    ${DEVOLUCAO_INPUT_DATA}    ${retirada}
    ${retirada_br}=    Convert Date    ${retirada}    result_format=%d/%m/%Y    date_format=%Y-%m-%d
    RETURN    ${retirada_br}

Devolucao Deve Ser Recusada
    [Documentation]    A tela continua na devolução, com o aviso do backend e sem o botão de confirmar.
    [Arguments]    ${mensagem}
    Devolucao Deve Estar Aberta
    Get Text    ${DEVOLUCAO_ALERTA_DE_RECUSA}    ==    ${mensagem}
    Get Element Count    ${DEVOLUCAO_BOTAO_CONFIRMAR}    ==    0
