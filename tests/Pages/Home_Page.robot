*** Variables ***
${MENU_NAVEGACAO}           //nav[@aria-label='Navegação principal']
${MENU_LINK_INICIO}         ${MENU_NAVEGACAO}//a[normalize-space()='Início']
${MENU_LINK_EQUIPAMENTOS}   ${MENU_NAVEGACAO}//a[normalize-space()='Equipamentos']
${MENU_LINK_CLIENTES}       ${MENU_NAVEGACAO}//a[normalize-space()='Clientes']
${MENU_LINK_NOVO_ALUGUEL}   ${MENU_NAVEGACAO}//a[normalize-space()='Novo aluguel']
${MENU_LINK_HISTORICO}      ${MENU_NAVEGACAO}//a[normalize-space()='Histórico']
${MENU_USUARIO_LOGADO}      ${MENU_NAVEGACAO}//span[contains(@class,'eqf-identificacao')]
${MENU_BOTAO_SAIR}          ${MENU_NAVEGACAO}//button[normalize-space()='Sair']
