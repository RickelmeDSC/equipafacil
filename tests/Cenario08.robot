*** Settings ***
Documentation     CT08 — Impedir exclusão de equipamento com histórico (RF004; Regression).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Acoes_Steps.robot
Test Setup        Iniciar Cenario    ct08
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT08 - Impedir exclusao de equipamento com historico
    [Tags]    CT08    RF004    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Acessar Acoes Do Equipamento    FUR-001
    Acoes Do Equipamento Deve Estar Aberto    FUR-001    Furadeira Impacto
    Indicador Do Equipamento Deve Ser    Histórico de locação    Possui
    Indicador Do Equipamento Deve Ser    Aluguel ativo    Não possui
    O Botao De Excluir Deve Estar Desabilitado Com O Motivo    Não é possível excluir: equipamento com histórico de locação. Utilize a inativação.
    O Botao De Inativar Deve Estar Habilitado
