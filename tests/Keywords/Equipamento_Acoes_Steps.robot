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

O Botao De Excluir Deve Estar Desabilitado Com O Motivo
    [Documentation]    A tela não oferece a confirmação de exclusão: só o botão desabilitado e o motivo.
    [Arguments]    ${motivo}
    Wait For Elements State    ${EQUIPAMENTO_ACOES_EXCLUSAO_BLOQUEADA}    visible
    Get Element States    ${EQUIPAMENTO_ACOES_EXCLUSAO_BLOQUEADA}    contains    disabled
    Get Text    ${EQUIPAMENTO_ACOES_MOTIVO_DA_EXCLUSAO}    ==    ${motivo}
    Get Element Count    ${EQUIPAMENTO_ACOES_ABRIR_EXCLUSAO}    ==    0
    Get Element Count    ${EQUIPAMENTO_ACOES_CONFIRMAR_EXCLUSAO}    ==    0

O Botao De Inativar Deve Estar Habilitado
    Get Element Count    ${EQUIPAMENTO_ACOES_BOTAO_INATIVAR}    ==    1
    Get Element States    ${EQUIPAMENTO_ACOES_BOTAO_INATIVAR}    contains    visible    enabled
