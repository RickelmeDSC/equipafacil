
*** Settings ***
Documentation     CT17 - Pesquisar cliente pelo nome.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Clientes_Steps.robot
Test Setup        Iniciar Cenario    ct17
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT17 - Pesquisar cliente pelo nome
    [Tags]    CT17    Clientes    Regression
    Entrar Como Funcionario
    Acessar Clientes
    Clientes Deve Estar Aberto
    Pesquisar Clientes    Maria QA Pesquisa
    Cliente Deve Aparecer Na Lista    Maria QA Pesquisa
    Clientes Deve Ter Quantidade De Linhas    1
