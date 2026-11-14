*** Settings ***
Documentation     CT16 — Consultar histórico sem registros e apresentar mensagem adequada (RF008; RN004).
...               Massa controlada: banco isolado sem nenhum aluguel (scripts/robot/massas/ct16.py).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct16
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT16 - Consultar historico sem registros e apresentar mensagem adequada
    [Tags]    CT16    RF008    RN004    Sanity    Regression
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Nao Deve Ter Linhas
    Historico Deve Exibir Mensagem De Ausencia
    ...    Nenhum registro encontrado.
    ...    Registre o primeiro aluguel para ver o histórico aqui.
    Historico Nao Deve Exibir Valores Nem Devolucao
