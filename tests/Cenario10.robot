
*** Settings ***
Documentation     CT10 - Impedir cadastro de cliente com CPF duplicado.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Clientes_Steps.robot
Resource          Keywords/Cliente_Form_Steps.robot
Test Setup        Iniciar Cenario    ct10
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT10 - Impedir cadastro com CPF duplicado
    [Tags]    CT10    Clientes    Regression
    Entrar Como Funcionario
    Acessar Clientes
    Clientes Deve Estar Aberto
    Acessar Novo Cliente
    Formulario De Cliente Deve Estar Aberto
    Preencher Formulario De Cliente
    ...    Maria QA Duplicada
    ...    52998224725
    ...    81999998888
    ...    maria.duplicada@example.com
    Salvar Cliente
    Cliente Deve Ser Recusado Por CPF Duplicado
    ...    Já existe um cliente com este CPF.
