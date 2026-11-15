*** Settings ***
Documentation     Passos comuns a todos os cenários: ambiente, massa e navegador.
...               BASE_URL e HEADLESS são informadas por scripts/robot/executar.py.
Library           Browser
Library           Process
Library           OperatingSystem

*** Keywords ***
Iniciar Cenario
    [Documentation]    Confere o ambiente, prepara a massa do cenário e abre a tela de login.
    [Arguments]    ${massa}
    Exigir Ambiente Local
    Preparar Massa    ${massa}
    New Browser    chromium    headless=${HEADLESS}
    New Context    locale=pt-BR    timezoneId=America/Recife    viewport={'width': 1366, 'height': 900}
    New Page    ${BASE_URL}/login/

Encerrar Cenario
    Close Browser

Exigir Ambiente Local
    [Documentation]    Recusa qualquer endereço que não seja o servidor local de teste.
    Variable Should Exist    ${BASE_URL}    Rode os testes por scripts/robot/executar.py.
    Should Match Regexp    ${BASE_URL}    ^http://(127\\.0\\.0\\.1|localhost):\\d+$
    ...    msg=Os testes só rodam contra o servidor local isolado.    values=False
    Environment Variable Should Be Set    EQF_ROBOT_PYTHON    Rode os testes por scripts/robot/executar.py.

Preparar Massa
    [Documentation]    Zera o banco isolado e cria a massa de scripts/robot/massas/<massa>.py.
    [Arguments]    ${massa}
    ${resultado}=    Run Process    %{EQF_ROBOT_PYTHON}    ${CURDIR}/../../scripts/robot/massa.py    ${massa}
    Should Be Equal As Integers    ${resultado.rc}    0    msg=Falha ao preparar a massa: ${resultado.stderr}    values=False
