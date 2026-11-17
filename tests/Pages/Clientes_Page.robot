
*** Variables ***
${CLIENTES_TITULO}                //h1[normalize-space()='Clientes']
${CLIENTES_LINK_NOVO}             //div[contains(@class,'eqf-cabecalho-da-pagina')]//a[normalize-space()='Novo cliente']

${CLIENTES_INPUT_PESQUISA}        //input[@id='id_q']
${CLIENTES_BOTAO_PESQUISAR}       //button[@type='submit' and normalize-space()='Pesquisar']

${CLIENTES_TABELA}                //table[contains(@class,'eqf-tabela')]
${CLIENTES_LINHAS}                ${CLIENTES_TABELA}//tbody/tr
${CLIENTES_LINHA_DO_NOME}         //table[contains(@class,'eqf-tabela')]/tbody/tr[td[1][normalize-space()='{nome}']]

${CLIENTES_VAZIO}                 //div[contains(@class,'eqf-vazio')]
${CLIENTES_VAZIO_TITULO}          //p[contains(@class,'eqf-vazio-titulo')]
