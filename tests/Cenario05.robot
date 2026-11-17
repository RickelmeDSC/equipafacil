*** Settings ***
Documentation     CT05 — Editar equipamento sem alterar valores de aluguéis anteriores (RF003; RN002, RN003, RN004).
...               Massa: "FUR-001" a R$ 50,00/dia com um aluguel encerrado de 3 diárias e R$ 150,00 (scripts/robot/massas/ct05.py).
...               As datas do aluguel anterior são relativas à execução; os valores são os do documento v1.4.
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Form_Steps.robot
Resource          Keywords/Historico_Steps.robot
Test Setup        Iniciar Cenario    ct05
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT05 - Editar equipamento sem alterar valores de alugueis anteriores
    [Tags]    CT05    RF003    RN002    RN003    RN004    Regression
    Entrar Como Funcionario
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Encerrado
    Acessar Equipamentos
    Equipamentos Deve Estar Aberto
    Equipamento Deve Aparecer Na Lista    FUR-001    Furadeira Impacto    Ferramentas    R$ 50,00    Ativo    Disponível
    Acessar Edicao Do Equipamento    FUR-001
    Formulario De Edicao De Equipamento Deve Estar Aberto
    Formulario De Equipamento Deve Exibir    FUR-001    Furadeira Impacto    Ferramentas    50,00    Furadeira profissional
    Informar Diaria Do Equipamento    60,00
    Salvar Equipamento
    Equipamentos Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Equipamento atualizado com sucesso.
    Equipamentos Deve Ter Quantidade De Linhas    1
    Equipamento Deve Aparecer Na Lista    FUR-001    Furadeira Impacto    Ferramentas    R$ 60,00    Ativo    Disponível
    Acessar Historico
    Historico Deve Estar Aberto
    Historico Deve Ter Quantidade De Linhas    1
    Historico Deve Exibir Aluguel    FUR-001    João Silva    3    R$ 50,00    R$ 150,00    Encerrado
