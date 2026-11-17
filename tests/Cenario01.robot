*** Settings ***
Documentation     CT01 — Cadastrar equipamento válido (RF001; RN002).
...               Massa: nenhum equipamento cadastrado (scripts/robot/massas/ct01.py).
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Form_Steps.robot
Test Setup        Iniciar Cenario    ct01
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT01 - Cadastrar equipamento valido
    [Tags]    CT01    RF001    RN002    Smoke    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Equipamentos Deve Estar Aberto
    Equipamentos Deve Ter Quantidade De Linhas    0
    Acessar Novo Equipamento
    Formulario De Novo Equipamento Deve Estar Aberto
    Preencher Formulario De Equipamento    FUR-001    Furadeira Impacto    50,00    Ferramentas    Furadeira profissional
    Salvar Equipamento
    Equipamentos Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Equipamento cadastrado com sucesso.
    Equipamentos Deve Ter Quantidade De Linhas    1
    Equipamento Deve Aparecer Na Lista    FUR-001    Furadeira Impacto    Ferramentas    R$ 50,00    Ativo    Disponível
    Acessar Edicao Do Equipamento    FUR-001
    Formulario De Edicao De Equipamento Deve Estar Aberto
    Formulario De Equipamento Deve Exibir    FUR-001    Furadeira Impacto    Ferramentas    50,00    Furadeira profissional
