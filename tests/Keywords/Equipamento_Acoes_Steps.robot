*** Settings ***
Library           Browser
Library           String
Resource          ../Pages/Equipamento_Acoes_Page.robot

*** Keywords ***
Acoes Do Equipamento Deve Estar Aberto
    [Arguments]    ${codigo}    ${nome}
    ${titulo}=    Format String    ${EQUIPAMENTO_ACOES_TITULO}    codigo=${codigo}    nome=${nome}
    Wait For Elements State    ${titulo}    visible

Indicador Do Equipamento Deve Ser
    [Documentation]    Rótulos da tela: "Histórico de locação" e "Aluguel ativo" ("Possui" ou "Não possui").
    [Arguments]    ${rotulo}    ${valor}
    ${indicador}=    Format String    ${EQUIPAMENTO_ACOES_INDICADOR}    rotulo=${rotulo}
    Get Text    ${indicador}    ==    ${valor}

Solicitar Exclusao Do Equipamento
    [Documentation]    Abre a confirmação; o botão de confirmar só fica visível depois disso.
    [Arguments]    ${pergunta}
    Click    ${EQUIPAMENTO_ACOES_ABRIR_EXCLUSAO}
    Wait For Elements State    ${EQUIPAMENTO_ACOES_CONFIRMAR_EXCLUSAO}    visible
    Get Text    ${EQUIPAMENTO_ACOES_PERGUNTA_DE_EXCLUSAO}    ==    ${pergunta}

Confirmar Exclusao Do Equipamento
    Click    ${EQUIPAMENTO_ACOES_CONFIRMAR_EXCLUSAO}
