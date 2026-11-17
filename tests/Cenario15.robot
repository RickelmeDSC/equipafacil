*** Settings ***
Documentation     CT15 — Consultar histórico de aluguéis (RF008; RN004).
...               Massa: quatro aluguéis, um em cada situação, cada um com o próprio equipamento
...               (scripts/robot/massas/ct15.py).
...               Adaptação: as datas são relativas à data da execução, porque a situação é calculada
...               com a data atual (um aluguel "Ativo" com datas fixas viraria "Atrasado" com o tempo).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct15
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT15 - Consultar historico de alugueis
    [Tags]    CT15    RF008    RN004    Smoke    Sanity    Regression
    ${hoje}=    Data Em Relacao A Hoje    0
    ${ontem}=    Data Em Relacao A Hoje    -1
    ${em_dois_dias}=    Data Em Relacao A Hoje    2
    ${ha_tres_dias}=    Data Em Relacao A Hoje    -3
    ${ha_cinco_dias}=    Data Em Relacao A Hoje    -5
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    4
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Ativo
    Historico Deve Exibir Periodo Do Aluguel    FUR-001    ${hoje}    ${em_dois_dias}
    Historico Deve Exibir Devolucao Do Aluguel    FUR-001    —
    Historico Deve Exibir Aluguel    BET-001    João Silva    3    R$ 80,00    R$ 240,00    Atrasado
    Historico Deve Exibir Periodo Do Aluguel    BET-001    ${ha_tres_dias}    ${ontem}
    Historico Deve Exibir Devolucao Do Aluguel    BET-001    —
    Historico Deve Exibir Aluguel    AND-001    Maria Souza    2    R$ 30,00    R$ 60,00    Encerrado
    Historico Deve Exibir Periodo Do Aluguel    AND-001    ${ontem}    ${hoje}
    Historico Deve Exibir Devolucao Do Aluguel    AND-001    ${ontem}
    Historico Deve Exibir Aluguel    PRJ-001    Maria Souza    3    R$ 100,00    R$ 300,00    Encerrado com atraso
    Historico Deve Exibir Periodo Do Aluguel    PRJ-001    ${ha_cinco_dias}    ${ha_tres_dias}
    Historico Deve Exibir Devolucao Do Aluguel    PRJ-001    ${ontem}
