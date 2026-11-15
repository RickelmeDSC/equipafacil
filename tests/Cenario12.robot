*** Settings ***
Documentation     CT12 — Impedir aluguel de equipamento indisponível (RF006; RN001, RN002, RN003, RN004).
...               Massa: dois clientes e os equipamentos "FUR-001" e "BET-001" (scripts/robot/massas/ct12.py).
...               A tela não oferece equipamento ocupado. Para a segunda tentativa chegar ao backend,
...               a primeira aba deixa o aluguel pronto para registrar; a segunda aba registra o aluguel
...               do mesmo equipamento; a primeira aba então envia o registro e o backend recusa.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Aluguel_Form_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct12
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT12 - Impedir aluguel de equipamento indisponivel
    [Tags]    CT12    RF006    RN001    RN002    RN003    RN004    Regression
    Entrar Como Funcionario
    Acessar Novo Aluguel
    Formulario De Aluguel Deve Estar Aberto
    Selecionar Cliente Do Aluguel    Maria Souza
    Selecionar Equipamento Do Aluguel    FUR-001
    Informar Periodo Do Aluguel A Partir De Hoje    2
    Calcular Resumo Do Aluguel
    Abrir Formulario De Aluguel Em Outra Aba
    Registrar Aluguel A Partir De Hoje    João Silva    FUR-001    2
    Historico Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Aluguel registrado com sucesso.
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Ativo
    Voltar Para A Aba Inicial
    Confirmar Registro Do Aluguel
    Aluguel Deve Ser Recusado Por Indisponibilidade    Este equipamento não está disponível para aluguel.
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Ativo
