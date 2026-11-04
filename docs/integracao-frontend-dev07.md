# Integração do frontend — DEV-07 (guia curto)

> **Situação:** backend de RF001–RF008 integrado à `main`, com os 10 templates **provisórios**. Este guia é o roteiro objetivo para a troca pelos templates definitivos (Raphael). O detalhe de cada tela está em [`equipamentos-operacional.md`](equipamentos-operacional.md), [`clientes-operacional.md`](clientes-operacional.md) e [`alugueis-operacional.md`](alugueis-operacional.md). O contrato técnico (PR #2) continua **proposta**, sem aceite.

## 1. Telas, rotas e contexto

| Página | Rota (nome) | Template | Contexto enviado pelo backend |
|--------|-------------|----------|-------------------------------|
| P10 Login | `login` (GET, POST) | `registration/login.html` | `form` (usuário e senha), `next` |
| P01 Início | `inicio` | `inicio.html` | `user` |
| Sair | `logout` (só POST) | — | — |
| P02 Equipamentos | `equipamentos:lista` (`?q=`) | `equipamentos/lista.html` | `object_list` (`codigo`, `nome`, `get_categoria_display`, `valor_diaria`, `ativo`, `disponivel`, `acoes`), `query`, `empty_message` |
| P03 Formulário de equipamento | `equipamentos:criar`, `equipamentos:editar` | `equipamentos/formulario.html` | `form`; na edição, `object` e `codigo_editavel` |
| P04 Ações do equipamento | `equipamentos:acoes` (GET) e `excluir`, `inativar`, `reativar` (POST) | `equipamentos/acoes.html` | `object`, `acoes` (`motivo_exclusao`, `motivo_inativacao`, `motivo_reativacao`), `tem_historico`, `tem_aluguel_ativo`, `pode_excluir`, `pode_inativar`, `pode_reativar` |
| P05 Clientes | `clientes:lista` | `clientes/lista.html` | `object_list` (`nome_completo`, `cpf_formatado`, `telefone_formatado`, `email`), `empty_message` |
| P06 Formulário de cliente | `clientes:criar`, `clientes:editar` | `clientes/formulario.html` | `form`; na edição, `object` e `cpf_editavel` |
| P07 Novo aluguel | `alugueis:criar` | `alugueis/formulario.html` | `form`, `resumo` (depois da prévia), `data_atual`, `data_minima`, `diarias_equipamentos` (para `json_script`), `sem_equipamentos_disponiveis`, `sem_clientes` |
| P08 Histórico | `alugueis:historico` | `alugueis/historico.html` | `object_list` (`cliente`, `equipamento`, datas, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado`, `situacao`, `situacao_codigo`, `pode_devolver`), `empty_message` |
| P09 Devolução | `alugueis:devolver` | `alugueis/devolver.html` | `object`, `form`, `pode_devolver`, `data_atual`, `data_minima`, `data_maxima` |

Não existem, de propósito: pesquisa e detalhe de cliente (D14), exclusão de cliente, edição ou cancelamento de aluguel, cadastro público, recuperação de senha e API JSON.

## 2. Componentes compartilhados (frontend)

| Arquivo | Conteúdo esperado |
|---------|-------------------|
| `templates/base.html` | Blocos `title` e `content`; Bootstrap 5.3 servido localmente de `static/` (WhiteNoise) |
| `templates/includes/navbar.html` | Equipamentos, Clientes, Novo aluguel, Histórico; nome do funcionário; Sair por formulário POST com `{% csrf_token %}` |
| `templates/includes/messages.html` | `{% for message in messages %}`; use `alert-{{ message.tags }}`: o backend já envia `danger` para erros (`success`, `warning` e `info` coincidem com o Bootstrap) |
| `templates/includes/form_errors.html` | `form.non_field_errors` em um alerta; erros de campo em `invalid-feedback` |

## 3. Formulários

- **Classes já aplicadas pelo backend** (`config/formularios.py`): `form-control`, `form-select` e `is-invalid` nos campos com erro; o Django acrescenta `aria-invalid="true"`. Renderize com `{{ form.campo }}` e `{{ form.campo.errors }}`; não é preciso editar `forms.py`.
- **Somente leitura:** com `codigo_editavel` (P03) ou `cpf_editavel` (P06) falso, o campo chega `disabled`; mostre a explicação ("O código/CPF não pode ser alterado porque … já possui aluguel registrado.").
- **Datas:** `<input type="date">` com `min`/`max` já definidos (P07, P09). O backend valida de novo.
- **Diária (P03):** aceita vírgula (`35,50`).
- **Botões obrigatórios:**
  - P07: dois botões `type="submit" name="acao"`, com `value="previa"` antes de `value="registrar"` no HTML (o Enter dispara o primeiro). Sem `acao`, nada é gravado.
  - P04: a exclusão envia `confirmacao=sim` (por exemplo, de um modal Bootstrap).
  - P09: envio simples.
- **JavaScript progressivo:** a página precisa funcionar sem JS. A prévia ao vivo de P07 pode usar `diarias_equipamentos`, mas o valor final vem sempre do backend.

## 4. Mensagens, estados vazios e formatação

- Os textos do EQF-5 chegam prontos em `form.errors`, `non_field_errors`, `messages` e `empty_message`: não os reescreva no template.
- Toda operação bem-sucedida redireciona e envia uma mensagem `success` (RF001, CT01), exibida por `includes/messages.html` na página de destino. Os textos são provisórios até o EQF-5 defini-los.
- Estados vazios: `empty_message` dentro de `{% empty %}` (P02, P05, P08), sem dados fictícios.
- Formatação: datas com `|date:"d/m/Y"`; valores com `|floatformat:"2g"` (gera `1.500,00`). Nenhum `|safe` em dado digitado; links sempre com `{% url %}`.

## 5. Testes do backend que leem o HTML

A CI roda a suíte inteira em cada PR. A maior parte dos testes confere o **contrato** (mensagens do EQF-5, valores formatados, links, `csrf`, `name="acao"`, `min`/`max`, escape de HTML) e precisa continuar passando com os templates novos. Alguns conferem **texto ou marcação provisórios**. Se o layout mudar, ajuste esses testes no mesmo PR, com revisão do backend:

| Teste | Depende de |
|-------|------------|
| `alugueis/tests/test_views.py` (`test_get_contexto_do_contrato`) | Frase "não pode ser cancelado" do aviso de P07 |
| `alugueis/tests/test_views.py` (`test_previa_calcula_no_servidor_e_nao_grava`) | Rótulo "Total previsto: R$ 150,00" |
| `alugueis/tests/test_views.py` (`test_quatro_situacoes_e_devolucao_so_quando_permitida`) e `alugueis/tests/test_cenarios_ct.py` (CT15) | Situação dentro de `<td>` (`>Ativo</td>`) e célula `código — nome` |
| `alugueis/tests/test_views.py` (`test_campos_valores_congelados_e_equipamento_inativo`) | Sufixo "(inativo)" na célula do equipamento |
| `clientes/tests/test_views.py` (`test_26_27_...`) | Explicação do CPF bloqueado com o texto do EQF-5 |
| `equipamentos/tests/test_views.py` e CT03 | Palavras "Ativo"/"Inativo" e "Disponível"/"Indisponível" |

## 6. Decisões de interface pendentes

1. P07: prévia só pelo botão (servidor) ou também ao vivo (JS); o botão de registro aparece desde o início ou só depois da prévia (D13 exige o resumo antes do registro).
2. P04: forma da confirmação de exclusão (modal).
3. Textos indefinidos no EQF-5: aviso de não cancelamento, ausência de clientes ou de equipamentos, devolução antes da retirada, ação inválida em P07 e o texto definitivo das mensagens de sucesso (hoje provisórios).
4. Cores dos selos de situação por `situacao_codigo` (`ativo`, `atrasado`, `encerrado`, `encerrado_com_atraso`).

## 7. Checklist do DEV-07

- [ ] Branch `feat/frontend-eqf-NN-<descricao>` a partir da `main` atualizada, na pasta única (sem worktree).
- [ ] `base.html` e `includes/` criados; Bootstrap 5.3 local em `static/`.
- [ ] Os 10 templates provisórios substituídos, mantendo nomes de rota, campos, variáveis, botões e `{% csrf_token %}`.
- [ ] Página funcional sem JavaScript; nenhum valor financeiro calculado só no navegador.
- [ ] `python manage.py test` local e CI verde no PR; testes da seção 5 ajustados com revisão do backend, se necessário.
- [ ] Revisão cruzada (Rickelme e Raphael) e homologação visual pela equipe de Testes antes do merge.
