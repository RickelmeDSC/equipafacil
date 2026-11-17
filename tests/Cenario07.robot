*** Settings ***
Documentation     CT07 — Excluir equipamento sem histórico (RF004; RN002, RN003).
...               Massa: "FUR-001" e "BET-001", ambos sem aluguel (scripts/robot/massas/ct07.py).
...               A remoção é comprovada pela interface: a lista, que também mostra equipamentos inativos,
...               deixa de exibir o "FUR-001" e mantém o "BET-001".
Resource          Keywords/Common_Steps.robot
Resource          Keywords/Login_Steps.robot
Resource          Keywords/Home_Steps.robot
Resource          Keywords/Equipamentos_Steps.robot
Resource          Keywords/Equipamento_Acoes_Steps.robot
Test Setup        Iniciar Cenario    ct07
Test Teardown     Encerrar Cenario

*** Test Cases ***
CT07 - Excluir equipamento sem historico
    [Tags]    CT07    RF004    RN002    RN003    Regression
    Entrar Como Funcionario
    Acessar Equipamentos
    Equipamentos Deve Estar Aberto
    Equipamentos Deve Ter Quantidade De Linhas    2
    Acessar Acoes Do Equipamento    FUR-001
    Acoes Do Equipamento Deve Estar Aberto    FUR-001    Furadeira Impacto
    Indicador Do Equipamento Deve Ser    Histórico de locação    Não possui
    Solicitar Exclusao Do Equipamento    Confirmar a exclusão de FUR-001 — Furadeira Impacto?
    Confirmar Exclusao Do Equipamento
    Equipamentos Deve Estar Aberto
    Mensagem De Sucesso Deve Ser    Equipamento excluído com sucesso.
    Equipamentos Deve Ter Quantidade De Linhas    1
    Equipamento Nao Deve Aparecer Na Lista    FUR-001
    Equipamento Deve Aparecer Na Lista    BET-001    Betoneira 150 L    Construção Civil    R$ 80,00    Ativo    Disponível
    Pesquisar Equipamento    FUR-001
    Lista De Equipamentos Deve Exibir Mensagem De Ausencia    Nenhum registro encontrado.
