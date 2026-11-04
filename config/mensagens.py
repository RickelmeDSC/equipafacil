"""Mensagens de validação do domínio.

Os textos são as mensagens propostas na tabela do épico EQF-5 (Jira), transcritas
literalmente. São referências de interface ainda não aprovadas como texto
definitivo: se o EQF-5 mudar, ajuste aqui. Mensagens sem texto no EQF-5 ficam
marcadas como internas, com texto provisório; chegam a uma tela só a confirmação
de exclusão ausente (P04), o cliente inexistente e a ação ausente ou inválida
(P07), todas em POST manipulado ou fora dos botões da página.
"""

CAMPO_OBRIGATORIO = "Preencha os campos obrigatórios."
CATEGORIA_INVALIDA = "Selecione uma categoria válida."
DIARIA_INVALIDA = (
    "O valor da diária deve ser maior que R$ 0,00 e ter no máximo duas casas decimais."
)
CODIGO_DUPLICADO = "Já existe um equipamento com este código."
CODIGO_BLOQUEADO = (
    "O código não pode ser alterado porque o equipamento já possui aluguel registrado."
)
CPF_INVALIDO = "CPF inválido."
CPF_DUPLICADO = "Já existe um cliente com este CPF."
CPF_BLOQUEADO = (
    "O CPF não pode ser alterado porque o cliente já possui aluguel registrado."
)
TELEFONE_INVALIDO = "Informe um telefone com DDD e 10 ou 11 dígitos."
EMAIL_INVALIDO = "E-mail inválido."
EQUIPAMENTO_INDISPONIVEL = "Este equipamento não está disponível para aluguel."
RETIRADA_NO_PASSADO = "A data de retirada não pode ser anterior à data atual."
PREVISTA_ANTES_DA_RETIRADA = "A devolução prevista não pode ser anterior à retirada."
DEVOLUCAO_ANTES_DA_RETIRADA = (
    "A data de devolução não pode ser anterior à data de retirada."
)
DEVOLUCAO_FUTURA = "A data de devolução não pode ser posterior à data atual."
ALUGUEL_ENCERRADO = "Este aluguel já foi encerrado."
EXCLUSAO_COM_HISTORICO = (
    "Não é possível excluir: equipamento com histórico de locação. "
    "Utilize a inativação."
)
ALUGUEL_ATIVO_IMPEDE = (
    "Não é possível excluir ou inativar: equipamento com aluguel ativo."
)
REATIVACAO_BLOQUEADA = (
    "Não é possível reativar: corrija os dados cadastrais ou encerre o aluguel ativo."
)
NENHUM_REGISTRO = "Nenhum registro encontrado."

# Sucesso: o RF001 (Documento de Requisitos v1.2) e o CT01 exigem mensagem de
# sucesso, mas o EQF-5 não define os textos ("Indefinida"). PROVISÓRIOS até a
# definição; trocar aqui não exige mudar views nem templates.
EQUIPAMENTO_CADASTRADO = "Equipamento cadastrado com sucesso."
EQUIPAMENTO_ATUALIZADO = "Equipamento atualizado com sucesso."
EQUIPAMENTO_EXCLUIDO = "Equipamento excluído com sucesso."
EQUIPAMENTO_INATIVADO = "Equipamento inativado com sucesso."
EQUIPAMENTO_REATIVADO = "Equipamento reativado com sucesso."
CLIENTE_CADASTRADO = "Cliente cadastrado com sucesso."
CLIENTE_ATUALIZADO = "Cliente atualizado com sucesso."
ALUGUEL_REGISTRADO = "Aluguel registrado com sucesso."
DEVOLUCAO_REGISTRADA = "Devolução registrada com sucesso."

# Internas: sem texto no EQF-5; texto provisório até definição.
CONFIRMACAO_DE_EXCLUSAO_AUSENTE = "Confirme a exclusão para continuar."
CLIENTE_INEXISTENTE = "Selecione um cliente cadastrado."
ACAO_DO_ALUGUEL_INVALIDA = "Escolha calcular o resumo ou registrar o aluguel."
ALUGUEL_INALTERAVEL = "Aluguel registrado não pode ser alterado."
VALORES_DO_ALUGUEL_INCONSISTENTES = (
    "Diárias e valor contratado não correspondem às datas e à diária contratada."
)
