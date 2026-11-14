*** Settings ***
Library           Browser
Resource          ../Pages/Home_Page.robot

*** Keywords ***
Acessar Inicio
    Click    ${MENU_LINK_INICIO}

Acessar Equipamentos
    Click    ${MENU_LINK_EQUIPAMENTOS}

Acessar Clientes
    Click    ${MENU_LINK_CLIENTES}

Acessar Novo Aluguel
    Click    ${MENU_LINK_NOVO_ALUGUEL}

Acessar Historico
    Click    ${MENU_LINK_HISTORICO}
