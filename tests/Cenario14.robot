*** Settings ***
Documentation     CT14 — Impedir devolução de aluguel já encerrado (RF007).
...               Massa: aluguel ativo do "FUR-001", retirado no dia anterior à execução (scripts/robot/massas/ct14.py).
...               A tela não oferece devolução para aluguel encerrado. Para a segunda devolução chegar ao backend,
...               a primeira aba deixa a devolução pronta para confirmar; a segunda aba registra a devolução
...               do mesmo aluguel; a primeira aba então confirma e o backend recusa.
...               As duas tentativas usam datas diferentes (a recusada usa a data da retirada; a que vale, a data
...               da execução), para provar que a devolução gravada continua sendo a primeira.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Aluguel_Form_Steps.robot
Resource          Keywords/Historico_Steps.robot
Resource          Keywords/Devolucao_Steps.robot
Test Setup        Iniciar Cenario    ct14
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT14 - Impedir devolucao de aluguel ja encerrado
    [Tags]    CT14    RF007    Regression
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Abrir Devolucao Do Aluguel    FUR-001
    Devolucao Deve Estar Aberta
    Informar Data De Devolucao Como Data Da Retirada
    Abrir Historico Em Outra Aba
    Abrir Devolucao Do Aluguel    FUR-001
    Devolucao Deve Estar Aberta
    ${primeira_devolucao}=    Informar Data De Devolucao Como Hoje
    Confirmar Devolucao
    Historico Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Devolução registrada com sucesso.
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Encerrado
    Historico Deve Exibir Devolucao Do Aluguel    FUR-001    ${primeira_devolucao}
    Voltar Para A Aba Inicial
    Confirmar Devolucao
    Devolucao Deve Ser Recusada    Este aluguel já foi encerrado.
    Devolucao Deve Exibir Dado Do Aluguel    Situação    Encerrado
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Encerrado
    Historico Deve Exibir Devolucao Do Aluguel    FUR-001    ${primeira_devolucao}
    Aluguel Nao Deve Permitir Devolucao    FUR-001
