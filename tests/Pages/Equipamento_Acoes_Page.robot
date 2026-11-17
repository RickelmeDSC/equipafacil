*** Variables ***
${EQUIPAMENTO_ACOES_TITULO}                 //h1[normalize-space()='{codigo} — {nome}']
${EQUIPAMENTO_ACOES_INDICADOR}              //div[div[contains(@class,'eqf-subtitulo') and normalize-space()='{rotulo}']]/strong
${EQUIPAMENTO_ACOES_ABRIR_EXCLUSAO}         //summary[normalize-space()='Excluir equipamento']
${EQUIPAMENTO_ACOES_PERGUNTA_DE_EXCLUSAO}   //details[contains(@class,'eqf-confirmacao')]//p[contains(@class,'fw-semibold')]
${EQUIPAMENTO_ACOES_CONFIRMAR_EXCLUSAO}     //button[@type='submit' and normalize-space()='Confirmar exclusão']
