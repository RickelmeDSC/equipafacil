*** Settings ***
Documentation     CT20 - Verificar ausência de aluguéis com atraso (RF010).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct20
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT20 - Filtrar historico sem alugueis com atraso
    [Tags]    CT20    RF010    Sanity    Regression
    [Documentation]    Verifica a mensagem de ausência ao filtrar aluguéis encerrados com atraso.
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    
    Filtrar Historico Por Situacao    Encerrado com atraso
    Historico Deve Exibir Mensagem De Ausencia    Nenhum registro encontrado.    Escolha outra situação ou limpe o filtro para ver todos os aluguéis.
    Historico Nao Deve Ter Linhas