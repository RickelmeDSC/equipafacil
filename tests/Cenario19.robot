*** Settings ***
Documentation     CT19 - Filtrar histórico por situação (RF010; RN004).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct19
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT19 - Filtrar historico por situacao
    [Tags]    CT19    RF010    RN004    Sanity    Regression
    [Documentation]    Verifica se o filtro exibe somente alugueis encerrados.
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    2
    Historico Deve Exibir Aluguel    CT19-001    Cliente CT19 Ativo    1    R$ 50,00    R$ 50,00    Ativo
    Historico Deve Exibir Aluguel    CT19-002    Cliente CT19 Encerrado    1    R$ 50,00    R$ 50,00    Encerrado
    Filtrar Historico Por Situacao    Encerrado
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    CT19-002    Cliente CT19 Encerrado    1    R$ 50,00    R$ 50,00    Encerrado
    Historico Todas As Linhas Devem Ter Situacao    Encerrado
    Historico Nao Deve Ter Linhas Na Situacao    Ativo
    Filtro Do Historico Deve Estar Em    Encerrado
