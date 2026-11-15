*** Settings ***
Library           Browser
Library           String
Library           DateTime
Resource          ../Pages/Aluguel_Form_Page.robot

*** Keywords ***
Formulario De Aluguel Deve Estar Aberto
    Wait For Elements State    ${ALUGUEL_FORM_TITULO}    visible

Selecionar Cliente Do Aluguel
    [Documentation]    Escolhe pelo nome completo; a opção da tela é "nome — CPF mascarado".
    [Arguments]    ${nome}
    ${opcao}=    Format String    ${ALUGUEL_FORM_OPCAO_DE_CLIENTE}    nome=${nome}
    ${valor}=    Get Attribute    ${opcao}    value
    Select Options By    ${ALUGUEL_FORM_SELECT_CLIENTE}    value    ${valor}

Selecionar Equipamento Do Aluguel
    [Documentation]    Escolhe pelo código; a opção da tela é "código — nome (diária/dia)".
    [Arguments]    ${codigo}
    ${opcao}=    Format String    ${ALUGUEL_FORM_OPCAO_DE_EQUIPAMENTO}    codigo=${codigo}
    ${valor}=    Get Attribute    ${opcao}    value
    Select Options By    ${ALUGUEL_FORM_SELECT_EQUIPAMENTO}    value    ${valor}

Informar Periodo Do Aluguel A Partir De Hoje
    [Documentation]    Retirada na data atual do servidor (valor inicial do campo) e devolução
    ...    prevista alguns dias depois. Devolve as duas datas em dd/mm/aaaa.
    [Arguments]    ${dias_depois}
    ${retirada}=    Get Property    ${ALUGUEL_FORM_INPUT_RETIRADA}    value
    ${prevista}=    Add Time To Date    ${retirada}    ${dias_depois} days
    ...    result_format=%Y-%m-%d    date_format=%Y-%m-%d
    Fill Text    ${ALUGUEL_FORM_INPUT_RETIRADA}    ${retirada}
    Fill Text    ${ALUGUEL_FORM_INPUT_PREVISTA}    ${prevista}
    ${retirada_br}=    Convert Date    ${retirada}    result_format=%d/%m/%Y    date_format=%Y-%m-%d
    ${prevista_br}=    Convert Date    ${prevista}    result_format=%d/%m/%Y    date_format=%Y-%m-%d
    RETURN    ${retirada_br}    ${prevista_br}

Calcular Resumo Do Aluguel
    [Documentation]    O botão de registrar só aparece depois de um resumo válido.
    Click    ${ALUGUEL_FORM_BOTAO_CALCULAR_RESUMO}
    Wait For Elements State    ${ALUGUEL_FORM_BOTAO_REGISTRAR}    visible

Resumo Do Aluguel Deve Exibir
    [Arguments]    ${diarias}    ${diaria}    ${total}
    Get Text    ${ALUGUEL_FORM_RESUMO_DIARIAS}    ==    ${diarias}
    Get Text    ${ALUGUEL_FORM_RESUMO_DIARIA}    ==    ${diaria}
    Get Text    ${ALUGUEL_FORM_RESUMO_TOTAL}    ==    Total previsto: ${total}

Confirmar Registro Do Aluguel
    Click    ${ALUGUEL_FORM_BOTAO_REGISTRAR}

Registrar Aluguel A Partir De Hoje
    [Documentation]    Fluxo completo na aba atual: escolhe, calcula o resumo e registra.
    [Arguments]    ${cliente}    ${codigo}    ${dias_depois}
    Formulario De Aluguel Deve Estar Aberto
    Selecionar Cliente Do Aluguel    ${cliente}
    Selecionar Equipamento Do Aluguel    ${codigo}
    Informar Periodo Do Aluguel A Partir De Hoje    ${dias_depois}
    Calcular Resumo Do Aluguel
    Confirmar Registro Do Aluguel

Abrir Formulario De Aluguel Em Outra Aba
    [Documentation]    Segunda aba na mesma sessão; a primeira continua aberta como estava.
    New Page    ${BASE_URL}/alugueis/novo/
    Formulario De Aluguel Deve Estar Aberto

Voltar Para A Aba Inicial
    ${abas}=    Get Page Ids
    Switch Page    ${abas}[0]

Aluguel Deve Ser Recusado Por Indisponibilidade
    [Documentation]    A tela continua no formulário, com o erro do backend no campo do equipamento.
    [Arguments]    ${mensagem}
    Formulario De Aluguel Deve Estar Aberto
    Get Text    ${ALUGUEL_FORM_ERRO_DO_EQUIPAMENTO}    ==    ${mensagem}

Equipamento Deve Estar Disponivel Para Aluguel
    [Arguments]    ${codigo}
    Formulario De Aluguel Deve Estar Aberto
    ${opcao}=    Format String    ${ALUGUEL_FORM_OPCAO_DE_EQUIPAMENTO}    codigo=${codigo}
    Get Element Count    ${opcao}    ==    1

Nao Deve Haver Equipamento Disponivel Para Aluguel
    [Documentation]    Vale quando a massa tem um único equipamento: a tela troca o formulário por um aviso.
    Formulario De Aluguel Deve Estar Aberto
    Wait For Elements State    ${ALUGUEL_FORM_AVISO_SEM_EQUIPAMENTOS}    visible
    Get Element Count    ${ALUGUEL_FORM_SELECT_EQUIPAMENTO}    ==    0
