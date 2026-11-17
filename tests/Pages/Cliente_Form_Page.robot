
*** Variables ***
${CLIENTE_FORM_TITULO}             //h1[normalize-space()='Novo cliente']

${CLIENTE_FORM_INPUT_NOME}         //input[@id='id_nome_completo']
${CLIENTE_FORM_INPUT_CPF}          //input[@id='id_cpf']
${CLIENTE_FORM_INPUT_TELEFONE}     //input[@id='id_telefone']
${CLIENTE_FORM_INPUT_EMAIL}        //input[@id='id_email']

${CLIENTE_FORM_BOTAO_SALVAR}       //form[@method='post']//button[@type='submit' and normalize-space()='Salvar']

${CLIENTE_FORM_ERRO_CPF}           //div[@id='id_cpf_error']
