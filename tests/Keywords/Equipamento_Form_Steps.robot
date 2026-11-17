*** Settings ***
Library           Browser
Resource          ../Pages/Equipamento_Form_Page.robot

*** Keywords ***
Formulario De Novo Equipamento Deve Estar Aberto
    Wait For Elements State    ${EQUIPAMENTO_FORM_TITULO_NOVO}    visible

Formulario De Edicao De Equipamento Deve Estar Aberto
    Wait For Elements State    ${EQUIPAMENTO_FORM_TITULO_EDICAO}    visible

Preencher Formulario De Equipamento
    [Documentation]    Categoria (pelo nome exibido) e descrição são opcionais na chamada.
    [Arguments]    ${codigo}    ${nome}    ${diaria}    ${categoria}=${NONE}    ${descricao}=${NONE}
    Fill Text    ${EQUIPAMENTO_FORM_INPUT_CODIGO}    ${codigo}
    Fill Text    ${EQUIPAMENTO_FORM_INPUT_NOME}    ${nome}
    Fill Text    ${EQUIPAMENTO_FORM_INPUT_DIARIA}    ${diaria}
    IF    $categoria is not None
        Select Options By    ${EQUIPAMENTO_FORM_SELECT_CATEGORIA}    label    ${categoria}
    END
    IF    $descricao is not None
        Fill Text    ${EQUIPAMENTO_FORM_INPUT_DESCRICAO}    ${descricao}
    END

Informar Diaria Do Equipamento
    [Arguments]    ${diaria}
    Fill Text    ${EQUIPAMENTO_FORM_INPUT_DIARIA}    ${diaria}

Formulario De Equipamento Deve Exibir
    [Documentation]    Valores carregados na edição. A diária aparece com vírgula (ex.: 50,00).
    [Arguments]    ${codigo}    ${nome}    ${categoria}    ${diaria}    ${descricao}
    Get Property    ${EQUIPAMENTO_FORM_INPUT_CODIGO}    value    ==    ${codigo}
    Get Property    ${EQUIPAMENTO_FORM_INPUT_NOME}    value    ==    ${nome}
    Get Selected Options    ${EQUIPAMENTO_FORM_SELECT_CATEGORIA}    label    ==    ${categoria}
    Get Property    ${EQUIPAMENTO_FORM_INPUT_DIARIA}    value    ==    ${diaria}
    Get Property    ${EQUIPAMENTO_FORM_INPUT_DESCRICAO}    value    ==    ${descricao}

Salvar Equipamento
    Click    ${EQUIPAMENTO_FORM_BOTAO_SALVAR}

Mensagem De Erro Deve Ser
    [Documentation]    O formulário deve exibir um único erro de campo, com exatamente este texto.
    [Arguments]    ${texto}
    Wait For Elements State    ${EQUIPAMENTO_FORM_BOTAO_SALVAR}    visible
    Get Element Count    ${EQUIPAMENTO_FORM_ERROS_DE_CAMPO}    ==    1
    Get Text    ${EQUIPAMENTO_FORM_ERROS_DE_CAMPO}    ==    ${texto}
