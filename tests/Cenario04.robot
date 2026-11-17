*** Settings ***
Documentation     CT04 — Pesquisar equipamento inexistente (RF002; Regression).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Test Setup        Iniciar Cenario    ct04
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT04 - Pesquisar equipamento inexistente
    [Tags]    CT04    RF002    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Equipamentos Deve Ter Quantidade De Linhas    1
    Pesquisar Equipamento    EQUIPAMENTO_FANTASMA_999
    A Lista Deve Estar Vazia
