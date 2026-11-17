
*** Settings ***
Documentation     CT18 - Pesquisar cliente inexistente.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Clientes_Steps.robot
Test Setup        Iniciar Cenario    ct18
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT18 - Pesquisar cliente inexistente
    [Tags]    CT18    Clientes    Regression
    Entrar Como Funcionario
    Acessar Clientes
    Clientes Deve Estar Aberto
    Pesquisar Clientes    Cliente Inexistente
    Pesquisa Deve Exibir Mensagem De Ausencia
    ...    Nenhum registro encontrado.
