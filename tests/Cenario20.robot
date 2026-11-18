*** Settings ***
Documentation     CT20 - Filtrar situação sem registros (RF010; RN004).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct20
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT20 - Filtrar situacao sem registros
    [Tags]    CT20    RF010    RN004    Sanity    Regression
    [Documentation]    Verifica a mensagem de ausência ao filtrar aluguéis encerrados com atraso.
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Filtro Do Historico Deve Estar Em    Todas
    Historico Deve Ter Quantidade De Linhas    2
    Historico Deve Exibir Aluguel    CT20-001    Cliente CT20 Ativo    1    R$ 50,00    R$ 50,00    Ativo
    Historico Deve Exibir Aluguel    CT20-002    Cliente CT20 Encerrado    1    R$ 50,00    R$ 50,00    Encerrado
    Historico Nao Deve Ter Linhas Na Situacao    Encerrado com atraso
    Filtrar Historico Por Situacao    Encerrado com atraso
    Historico Deve Exibir Mensagem De Ausencia    Nenhum registro encontrado.    Escolha outra situação ou limpe o filtro para ver todos os aluguéis.
    Historico Nao Deve Ter Linhas
    Filtro Do Historico Deve Estar Em    Encerrado com atraso
