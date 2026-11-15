"""Massa do controle negativo do CT16: histórico com um aluguel ativo.

Não é um cenário acadêmico. Serve só para comprovar que as verificações do CT16
falham quando o histórico não está vazio
(``scripts/robot/controles/Controle_CT16.robot``).
"""

from config.tests.fabricas import criar_cliente, criar_equipamento, dias, registrar


def preparar() -> None:
    cliente = criar_cliente(nome_completo="Cliente Fictício Controle")
    equipamento = criar_equipamento(codigo="CTRL-001", nome="Equipamento Controle")
    registrar(equipamento=equipamento, cliente=cliente, prevista=dias(2))
