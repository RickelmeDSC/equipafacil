*** Variables ***
${HISTORICO_TITULO}                  //h1[normalize-space()='Histórico de aluguéis']
${HISTORICO_SELECT_SITUACAO}         //select[@id='id_situacao']
${HISTORICO_BOTAO_FILTRAR}           //button[@type='submit' and normalize-space()='Filtrar']
${HISTORICO_PAINEL_DE_RESULTADOS}    //div[contains(@class,'eqf-painel') and not(contains(@class,'eqf-painel-corpo'))]
${HISTORICO_LINHAS}                  //table[contains(@class,'eqf-tabela')]/tbody/tr
${HISTORICO_VAZIO_TITULO}            //div[contains(@class,'eqf-vazio')]/p[contains(@class,'eqf-vazio-titulo')]
${HISTORICO_VAZIO_TEXTO}             //div[contains(@class,'eqf-vazio')]/p[contains(@class,'eqf-vazio-texto')]
${HISTORICO_LINKS_DE_DEVOLUCAO}      //a[normalize-space()='Registrar devolução']
