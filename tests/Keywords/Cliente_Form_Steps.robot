
*** Settings ***
Library           Browser
Resource          ../Pages/Cliente_Form_Page.robot

*** Keywords ***
Formulario De Cliente Deve Estar Aberto
    Wait For Elements State    ${CLIENTE_FORM_TITULO}    visible

Preencher Formulario De Cliente
    [Arguments]    ${nome}    ${cpf}    ${telefone}    ${email}
    Fill Text    ${CLIENTE_FORM_INPUT_NOME}    ${nome}
    Fill Text    ${CLIENTE_FORM_INPUT_CPF}    ${cpf}
    Fill Text    ${CLIENTE_FORM_INPUT_TELEFONE}    ${telefone}
    Fill Text    ${CLIENTE_FORM_INPUT_EMAIL}    ${email}

Salvar Cliente
    Click    ${CLIENTE_FORM_BOTAO_SALVAR}

Cliente Deve Ser Recusado Por CPF Duplicado
    [Arguments]    ${mensagem}
    Wait For Elements State    ${CLIENTE_FORM_ERRO_CPF}    visible
    Get Text    ${CLIENTE_FORM_ERRO_CPF}    ==    ${mensagem}
