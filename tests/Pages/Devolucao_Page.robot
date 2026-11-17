*** Variables ***
${DEVOLUCAO_TITULO}             //h1[normalize-space()='Registrar devolução']
${DEVOLUCAO_DADO_DO_ALUGUEL}    //dl/dt[normalize-space()='{rotulo}']/following-sibling::dd[1]
${DEVOLUCAO_INPUT_DATA}         //input[@id='id_data_devolucao_real']
${DEVOLUCAO_BOTAO_CONFIRMAR}    //button[@type='submit' and normalize-space()='Confirmar devolução']
${DEVOLUCAO_ALERTA_DE_RECUSA}   //div[@role='alert' and contains(@class,'alert-warning')]
