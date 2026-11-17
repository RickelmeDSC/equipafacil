
*** Settings ***
Documentation     CT09 - Cadastrar cliente com dados válidos.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Clientes_Steps.robot
Resource          Keywords/Cliente_Form_Steps.robot
Test Setup        Iniciar Cenario    ct09
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT09 - Cadastrar cliente com dados validos
    [Tags]    CT09    Clientes    Regression
    Entrar Como Funcionario
    Acessar Clientes
    Clientes Deve Estar Aberto
    Acessar Novo Cliente
    Formulario De Cliente Deve Estar Aberto
    Preencher Formulario De Cliente
    ...    Maria QA Cadastro
    ...    52998224725
    ...    81999998888
    ...    maria.qa@example.com
    Salvar Cliente
    Clientes Deve Estar Aberto
    Cliente Deve Aparecer Na Lista    Maria QA Cadastro
    Clientes Deve Ter Quantidade De Linhas    1
