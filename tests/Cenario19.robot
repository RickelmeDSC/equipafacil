
*** Settings ***
Documentation     CT19 - Filtrar histórico por situação (RF010).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct19
Test Teardown     Encerrar Cenario
*** Test Cases ***
CT19 - Filtrar historico por situacao
    [Tags]    CT19    RF010    Sanity    Regression
    [Documentation]    Verifica se o filtro exibe somente alugueis encerrados.
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Filtrar Historico Por Situacao    Encerrado
    Historico Todas As Linhas Devem Ter Situacao    Encerrado
    Filtro Do Historico Deve Estar Em    Encerrado
