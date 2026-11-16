*** Settings ***
Documentation     CT06 — Impedir edição com diária de R$ 0,00 (RF003; Regression).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Form_Steps.robot
Test Setup        Iniciar Cenario    ct06
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT06 - Impedir edicao com diaria de R$ 0,00
    [Tags]    CT06    RF003    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Acessar Edicao Do Equipamento    FUR-001
    Preencher Formulario De Equipamento    FUR-001    Furadeira Impacto    0,00
    Salvar Equipamento
    Mensagem De Erro Deve Ser    O valor da diária deve ser maior que R$ 0,00 e ter no máximo duas casas decimais.
    A Lista Deve Exibir O Valor Da Diaria Do Equipamento    FUR-001    R$ 50,00