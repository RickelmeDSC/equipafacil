*** Settings ***
Library           Browser
Resource          ../Pages/Login_Page.robot
Resource          ../Pages/Home_Page.robot

*** Keywords ***
Preencher Credenciais De Acesso
    [Documentation]    Usa o usuário fictício da execução; a senha vem do ambiente e não aparece no log.
    Fill Text    ${LOGIN_INPUT_USUARIO}    %{EQF_ROBOT_USUARIO}
    Fill Secret    ${LOGIN_INPUT_SENHA}    %EQF_ROBOT_SENHA

Submeter Formulario De Login
    Click    ${LOGIN_BOTAO_ENTRAR}

Entrar Como Funcionario
    Wait For Elements State    ${LOGIN_TITULO}    visible
    Preencher Credenciais De Acesso
    Submeter Formulario De Login
    Wait For Elements State    ${MENU_NAVEGACAO}    visible
    Get Text    ${MENU_USUARIO_LOGADO}    ==    %{EQF_ROBOT_USUARIO}
