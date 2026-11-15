*** Variables ***
${ALUGUEL_FORM_TITULO}                    //h1[normalize-space()='Novo aluguel']
${ALUGUEL_FORM_SELECT_CLIENTE}            //select[@id='id_cliente']
${ALUGUEL_FORM_SELECT_EQUIPAMENTO}        //select[@id='id_equipamento']
${ALUGUEL_FORM_OPCAO_DE_CLIENTE}          ${ALUGUEL_FORM_SELECT_CLIENTE}/option[starts-with(normalize-space(),'{nome} —')]
${ALUGUEL_FORM_OPCAO_DE_EQUIPAMENTO}      ${ALUGUEL_FORM_SELECT_EQUIPAMENTO}/option[starts-with(normalize-space(),'{codigo} —')]
${ALUGUEL_FORM_INPUT_RETIRADA}            //input[@id='id_data_retirada']
${ALUGUEL_FORM_INPUT_PREVISTA}            //input[@id='id_data_devolucao_prevista']
${ALUGUEL_FORM_BOTAO_CALCULAR_RESUMO}     //button[@name='acao' and @value='previa']
${ALUGUEL_FORM_BOTAO_REGISTRAR}           //button[@name='acao' and @value='registrar']
${ALUGUEL_FORM_RESUMO_DIARIAS}            //div[contains(@class,'eqf-resumo-linha')][dt[normalize-space()='Quantidade de diárias']]/dd
${ALUGUEL_FORM_RESUMO_DIARIA}             //div[contains(@class,'eqf-resumo-linha')][dt[normalize-space()='Diária do equipamento']]/dd
${ALUGUEL_FORM_RESUMO_TOTAL}              //p[contains(@class,'eqf-resumo-total')]
${ALUGUEL_FORM_ERRO_DO_EQUIPAMENTO}       //div[@id='id_equipamento_error']
${ALUGUEL_FORM_AVISO_SEM_EQUIPAMENTOS}    //p[normalize-space()='Nenhum equipamento disponível para aluguel.']
