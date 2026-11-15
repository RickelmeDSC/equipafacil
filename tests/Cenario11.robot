*** Settings ***
Documentation     CT11 — Registrar aluguel e calcular corretamente o valor (RF006; RN001, RN002, RN003, RN004).
...               Massa: cliente "João Silva" e equipamento "FUR-001" (R$ 50,00/dia) disponíveis (scripts/robot/massas/ct11.py).
...               Adaptação: o documento v1.4 usa 03/11/2026 a 05/11/2026, datas já passadas, que o sistema recusa.
...               O cenário usa a data da execução e dois dias depois: as mesmas 3 diárias inclusivas e R$ 150,00.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Aluguel_Form_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct11
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT11 - Registrar aluguel e calcular corretamente o valor
    [Tags]    CT11    RF006    RN001    RN002    RN003    RN004    Smoke    Regression
    Entrar Como Funcionario
    Acessar Novo Aluguel
    Formulario De Aluguel Deve Estar Aberto
    Selecionar Cliente Do Aluguel    João Silva
    Selecionar Equipamento Do Aluguel    FUR-001
    ${retirada}    ${prevista}=    Informar Periodo Do Aluguel A Partir De Hoje    2
    Calcular Resumo Do Aluguel
    Resumo Do Aluguel Deve Exibir    3    R$ 50,00    R$ 150,00
    Confirmar Registro Do Aluguel
    Historico Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Aluguel registrado com sucesso.
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Ativo
    Historico Deve Exibir Periodo Do Aluguel    FUR-001    ${retirada}    ${prevista}
    Acessar Novo Aluguel
    Nao Deve Haver Equipamento Disponivel Para Aluguel
