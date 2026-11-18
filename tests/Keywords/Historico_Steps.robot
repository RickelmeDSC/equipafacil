*** Settings ***
Library           Browser
Library           String
Resource          ../Pages/Historico_Page.robot

*** Keywords ***
Historico Deve Estar Aberto
    Wait For Elements State    ${HISTORICO_TITULO}    visible

Historico Nao Deve Ter Linhas
    Get Element Count    ${HISTORICO_LINHAS}    ==    0

Historico Deve Exibir Mensagem De Ausencia
    [Arguments]    ${titulo}    ${texto}
    Get Text    ${HISTORICO_VAZIO_TITULO}    ==    ${titulo}
    Get Text    ${HISTORICO_VAZIO_TEXTO}    ==    ${texto}

Historico Nao Deve Exibir Valores Nem Devolucao
    Get Text    ${HISTORICO_PAINEL_DE_RESULTADOS}    not contains    R$
    Get Element Count    ${HISTORICO_LINKS_DE_DEVOLUCAO}    ==    0

Historico Deve Ter Quantidade De Linhas
    [Arguments]    ${quantidade}
    Get Element Count    ${HISTORICO_LINHAS}    ==    ${quantidade}

Historico Deve Exibir Aluguel
    [Documentation]    Confere a linha do equipamento, pelo código. Falha se houver mais de uma linha do mesmo código.
    [Arguments]    ${codigo}    ${cliente}    ${diarias}    ${diaria}    ${valor}    ${situacao}
    ${linha}=    Format String    ${HISTORICO_LINHA_DO_EQUIPAMENTO}    codigo=${codigo}
    Get Text    ${linha}${HISTORICO_COLUNA_CLIENTE}    ==    ${cliente}
    Get Text    ${linha}${HISTORICO_COLUNA_DIARIAS}    ==    ${diarias}
    Get Text    ${linha}${HISTORICO_COLUNA_DIARIA}    ==    ${diaria}
    Get Text    ${linha}${HISTORICO_COLUNA_VALOR}    ==    ${valor}
    Get Text    ${linha}${HISTORICO_COLUNA_SITUACAO}    ==    ${situacao}

Historico Deve Exibir Periodo Do Aluguel
    [Documentation]    Datas no formato dd/mm/aaaa.
    [Arguments]    ${codigo}    ${retirada}    ${prevista}
    ${linha}=    Format String    ${HISTORICO_LINHA_DO_EQUIPAMENTO}    codigo=${codigo}
    Get Text    ${linha}${HISTORICO_COLUNA_RETIRADA}    ==    ${retirada}
    Get Text    ${linha}${HISTORICO_COLUNA_PREVISTA}    ==    ${prevista}

Historico Deve Exibir Devolucao Do Aluguel
    [Documentation]    Data no formato dd/mm/aaaa; aluguel sem devolução exibe um travessão.
    [Arguments]    ${codigo}    ${devolucao}
    ${linha}=    Format String    ${HISTORICO_LINHA_DO_EQUIPAMENTO}    codigo=${codigo}
    Get Text    ${linha}${HISTORICO_COLUNA_DEVOLUCAO}    ==    ${devolucao}

Abrir Devolucao Do Aluguel
    [Arguments]    ${codigo}
    ${linha}=    Format String    ${HISTORICO_LINHA_DO_EQUIPAMENTO}    codigo=${codigo}
    Click    ${linha}${HISTORICO_LINKS_DE_DEVOLUCAO}

Aluguel Nao Deve Permitir Devolucao
    [Arguments]    ${codigo}
    ${linha}=    Format String    ${HISTORICO_LINHA_DO_EQUIPAMENTO}    codigo=${codigo}
    Get Element Count    ${linha}${HISTORICO_LINKS_DE_DEVOLUCAO}    ==    0

Abrir Historico Em Outra Aba
    [Documentation]    Segunda aba na mesma sessão; a primeira continua aberta como estava.
    New Page    ${BASE_URL}/alugueis/
    Historico Deve Estar Aberto

Data Em Relacao A Hoje
    [Documentation]    Data atual em America/Recife (a mesma referência do servidor) deslocada em dias
    ...    (negativo para o passado). Devolve a data em dd/mm/aaaa, como o histórico a exibe.
    [Arguments]    ${dias}
    ${data}=    Evaluate
    ...    (datetime.datetime.now(zoneinfo.ZoneInfo('America/Recife')) + datetime.timedelta(days=int($dias))).strftime('%d/%m/%Y')
    ...    modules=datetime,zoneinfo
    RETURN    ${data}
Filtrar Historico Por Situacao
    [Arguments]    ${situacao}
    Select Options By    ${HISTORICO_SELECT_SITUACAO}    label    ${situacao}
    Click    ${HISTORICO_BOTAO_FILTRAR}

Filtro Do Historico Deve Estar Em
    [Arguments]    ${situacao}
    Get Selected Options    ${HISTORICO_SELECT_SITUACAO}    label    ==    ${situacao}
Historico Todas As Linhas Devem Ter Situacao
    [Arguments]    ${situacao}
        ${celulas_diferentes}=    Catenate    SEPARATOR=    ${HISTORICO_LINHAS}    ${HISTORICO_COLUNA_SITUACAO}    [normalize-space() != '${situacao}']
    Get Element Count    ${celulas_diferentes}    ==    0