*** Settings ***
Documentation     CT13 — Registrar devolução e liberar equipamento (RF007; RN001, RN004).
...               Massa: aluguel ativo do "FUR-001", 3 diárias, R$ 150,00 (scripts/robot/massas/ct13.py).
...               Adaptação: o documento v1.4 usa retirada em 01/11/2026 e devolução em 02/11/2026, datas já passadas.
...               O cenário usa retirada no dia anterior à execução e devolução na data da execução.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Aluguel_Form_Steps.robot
Resource          Keywords/Historico_Steps.robot
Resource          Keywords/Devolucao_Steps.robot
Test Setup        Iniciar Cenario    ct13
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT13 - Registrar devolucao e liberar equipamento
    [Tags]    CT13    RF007    RN001    RN004    Smoke    Regression
    Entrar Como Funcionario
    Acessar Novo Aluguel
    Nao Deve Haver Equipamento Disponivel Para Aluguel
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Ativo
    Historico Deve Exibir Devolucao Do Aluguel    FUR-001    —
    Abrir Devolucao Do Aluguel    FUR-001
    Devolucao Deve Estar Aberta
    Devolucao Deve Exibir Dado Do Aluguel    Equipamento    FUR-001 — Furadeira Impacto
    Devolucao Deve Exibir Dado Do Aluguel    Valor contratado    R$ 150,00
    Devolucao Deve Exibir Dado Do Aluguel    Situação    Ativo
    ${devolucao}=    Informar Data De Devolucao Como Hoje
    Confirmar Devolucao
    Historico Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Devolução registrada com sucesso.
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Encerrado
    Historico Deve Exibir Devolucao Do Aluguel    FUR-001    ${devolucao}
    Aluguel Nao Deve Permitir Devolucao    FUR-001
    Acessar Novo Aluguel
    Equipamento Deve Estar Disponivel Para Aluguel    FUR-001
