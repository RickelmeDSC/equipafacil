*** Settings ***
Documentation     CT02 — Impedir cadastro com código duplicado (RF001; Regression).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Form_Steps.robot
Test Setup        Iniciar Cenario    ct02
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT02 - Impedir cadastro com codigo duplicado
    [Tags]    CT02    RF001    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Acessar Novo Equipamento
    Preencher Formulario De Equipamento    FUR-001    Outra Furadeira    50,00
    Salvar Equipamento
    Mensagem De Erro Deve Ser    Já existe um equipamento com este código.
    A Pesquisa Deve Retornar Apenas Um Equipamento    FUR-001