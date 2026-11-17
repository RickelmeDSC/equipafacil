*** Settings ***
Documentation     CT03 — Consultar equipamento e verificar disponibilidade (RF002; RN001, RN003).
...               Massa: "FUR-001" disponível, "BET-001" com aluguel ativo e "SER-001" inativo (scripts/robot/massas/ct03.py).
...               Os dois últimos comprovam a disponibilidade calculada e que a pesquisa filtra a lista.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Test Setup        Iniciar Cenario    ct03
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT03 - Consultar equipamento e verificar disponibilidade
    [Tags]    CT03    RF002    RN001    RN003    Smoke    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Equipamentos Deve Estar Aberto
    Equipamentos Deve Ter Quantidade De Linhas    3
    Equipamento Deve Aparecer Na Lista    BET-001    Betoneira 150 L    Construção Civil    R$ 80,00    Ativo    Indisponível
    Equipamento Deve Aparecer Na Lista    SER-001    Serra Circular    Ferramentas    R$ 40,00    Inativo    Indisponível
    Pesquisar Equipamento    FUR-001
    Equipamentos Deve Ter Quantidade De Linhas    1
    Equipamento Deve Aparecer Na Lista    FUR-001    Furadeira Impacto    Ferramentas    R$ 50,00    Ativo    Disponível
    Pesquisar Equipamento    Furadeira
    Equipamentos Deve Ter Quantidade De Linhas    1
    Equipamento Deve Aparecer Na Lista    FUR-001    Furadeira Impacto    Ferramentas    R$ 50,00    Ativo    Disponível
