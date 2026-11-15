*** Settings ***
Documentation     Controle negativo do CT16 (verificação técnica; não é cenário acadêmico).
...               Com um aluguel no histórico, cada verificação usada pelo CT16 precisa falhar.
...               O teste passa quando as três falhas esperadas acontecem.
...               Fica fora de tests/ para não entrar na suíte oficial. Execução:
...               python scripts/robot/executar.py scripts/robot/controles/Controle_CT16.robot
Resource          ../../../tests/Keywords/Common_Steps.robot
Resource          ../../../tests/Keywords/Login_Steps.robot
Resource          ../../../tests/Keywords/Home_Steps.robot
Resource          ../../../tests/Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    controle_ct16
Test Teardown     Encerrar Cenario

*** Test Cases ***
Controle negativo do CT16 - verificacoes detectam historico com aluguel
    [Tags]    controle
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Run Keyword And Expect Error    Element count*is '1'*should be '0'*
    ...    Historico Nao Deve Ter Linhas
    Run Keyword And Expect Error    *Timeout*waiting for locator*
    ...    Historico Deve Exibir Mensagem De Ausencia
    ...    Nenhum registro encontrado.
    ...    Registre o primeiro aluguel para ver o histórico aqui.
    Run Keyword And Expect Error    *should not contain 'R$'*
    ...    Historico Nao Deve Exibir Valores Nem Devolucao
