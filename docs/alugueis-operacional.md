# Aluguéis, devoluções e histórico — DEV-06 (EQF-18)

> **Situação:** integrado à `main` em 02/11/2026 pelo PR #8 (merge commit `85b4d1a`, marco da `main` integrada), já com a confirmação explícita do registro (`f3ad6d8`). Desenvolvido na branch `feat/backend-eqf-18-alugueis`, sobre DEV-05, DEV-04, DEV-03 e DEV-02. Rotas, nomes de template e variáveis seguem o contrato técnico **proposto** no PR #2 (v0.4), ainda em rascunho e sem aceite de Raphael. As páginas HTML são **provisórias**.

Escopo: RF006 (registro), RF007 (devolução), RF008 (histórico) e, desde o EQF-43, RF010 (filtro do histórico por situação), com RN001–RN004, I1, I2 e D13. Fora do escopo: cancelamento, edição de aluguel ou de devolução, multa, pagamento, reserva, outros filtros e paginação do histórico.

> **RF010 (EQF-43, 10/11/2026):** aprovado tecnicamente por Rickelme no EQF-5 (comentário 10078). Validação documental da equipe de Requisitos e revisão do template por Raphael pendentes. Veja a seção [Filtro do histórico (RF010)](#filtro-do-histórico-rf010).

> **Atribuição no Jira:** a rastreabilidade associa CT15–CT16 (histórico) ao DEV-07 (EQF-19). Nesta tarefa, o RF008 foi implementado junto com o DEV-06, por instrução do responsável técnico. O Jira não foi alterado.

## Classificação das fontes

| Tipo | O que foi usado |
|------|-----------------|
| Regras aprovadas | RF006–RF008, RN001–RN004, I1 (retirada futura reserva o equipamento; sem devolução antes da retirada), I2 (aluguel e devolução não são corrigidos), D13 (formulário único com resumo e aviso de não cancelamento), fuso `America/Recife`, Decimal |
| Proposta técnica (PR #2, sem aceite) | Rotas `alugueis:historico`, `alugueis:criar`, `alugueis:devolver`; templates; variáveis `data_atual`, `data_minima`, `data_maxima`, `diarias_equipamentos`, `sem_equipamentos_disponiveis`, `sem_clientes`, `pode_devolver`, `situacao`, `situacao_codigo` |
| Decisões técnicas provisórias desta etapa | Prévia calculada no servidor e confirmação explícita (campo `acao` = `previa` ou `registrar`); variável `resumo`; CPF mascarado na seleção de clientes; ordem do histórico; textos indefinidos no EQF-5 |
| Mensagens | EQF-5 (`config/mensagens.py`), inclusive "A data de devolução não pode ser posterior à data atual."; internas provisórias: "Selecione um cliente cadastrado." |
| Pendências acadêmicas | CT11–CT16 com a equipe de Testes; auditoria QA-AUD-01 (não disponível nesta sessão); CT16 é obrigatório e está ausente do documento v1.1 da equipe de QA |

## Rotas

| Página | Rota (nome) | Método | Comportamento |
|--------|-------------|--------|---------------|
| P08 — histórico | `/alugueis/` (`alugueis:historico`) | GET | Todos os aluguéis, do mais recente (`-data_retirada`, `-pk`), inclusive de equipamentos inativos; com `?situacao=`, só os da situação escolhida, na mesma ordem (RF010). Sem paginação (contrato, 9.4). Vazio: "Nenhum registro encontrado." |
| P07 — novo aluguel | `/alugueis/novo/` (`alugueis:criar`) | GET, POST | Formulário único. POST com `acao=previa`: valida e mostra o resumo, **sem gravar**. POST com `acao=registrar`: registra e vai para P08. Sem `acao`, com outro valor ou com mais de um: **nada é gravado** e o formulário volta (200) com os dados e o erro geral "Escolha calcular o resumo ou registrar o aluguel." |
| P09 — devolução | `/alugueis/<pk>/devolver/` (`alugueis:devolver`) | GET, POST | Aluguel em leitura e a data real (inicial: data atual). Sucesso → P08 |

Sem rotas de cancelamento, edição, exclusão ou detalhe de aluguel, e sem endpoint JSON. Todas exigem login; outros métodos recebem 405; `pk` inexistente recebe 404. `Aluguel` não está no Django Admin.

## Formulários (`alugueis/forms.py`)

**`AluguelForm` (P07):** `cliente`, `equipamento`, `data_retirada`, `data_devolucao_prevista`. Nenhum campo financeiro: diária, diárias e valor enviados no POST são ignorados.

| Campo | Opções e validação |
|-------|--------------------|
| `cliente` | Todos os clientes, por nome e cadastro. Rótulo: nome e CPF mascarado (`Maria Fictícia — CPF ***.533.447-**`), para distinguir homônimos sem expor o CPF inteiro. `Cliente.__str__` não foi alterado |
| `equipamento` | Só disponíveis (ativos e sem aluguel aberto, inclusive de retirada futura), por nome e código, em uma consulta. Rótulo: `código — nome (R$ 50,00/dia)`. Escolha fora da lista: "Este equipamento não está disponível para aluguel." |
| `data_retirada` | `<input type="date">` com `min` = data atual; inicial = data atual; não anterior a hoje em America/Recife |
| `data_devolucao_prevista` | `<input type="date">` com `min` = data atual; igual ou posterior à retirada |

**`DevolucaoForm` (P09):** `data_devolucao_real`, com `min` = retirada, `max` = data atual e valor inicial = data atual. Os atributos `min`/`max` só orientam a tela: o serviço valida de novo.

## Variáveis de contexto

| Template | Variáveis |
|----------|-----------|
| `alugueis/formulario.html` (P07) | `form`, `resumo` (`quantidade_diarias`, `valor_diaria`, `valor_previsto`; só depois da prévia), `data_atual`, `data_minima`, `diarias_equipamentos` (dicionário `{pk: "50.00"}`, para `json_script`), `sem_equipamentos_disponiveis`, `sem_clientes` |
| `alugueis/historico.html` (P08) | `object_list` (com `cliente` e `equipamento` carregados), `situacao_selecionada` (`""` para Todas ou um código de situação), `opcoes_situacao` (pares valor/rótulo, começando por `("", "Todas")`), `empty_message`. Por aluguel: `data_retirada`, `data_devolucao_prevista`, `data_devolucao_real`, `quantidade_diarias`, `valor_diaria_contratada`, `valor_contratado`, `situacao`, `situacao_codigo`, `pode_devolver`, `aberto` |
| `alugueis/devolver.html` (P09) | `object`, `form`, `pode_devolver`, `data_atual`, `data_minima`, `data_maxima` |

`situacao`, `situacao_codigo` e `pode_devolver` são métodos do modelo, chamados sem argumentos no template (usam a data atual).

## Contrato dos botões de P07 (D13)

Desde a correção `fix/eqf-18-confirmacao-aluguel`, o registro exige confirmação explícita. Como não há cancelamento na v1, o registro **nunca** é o comportamento padrão de um POST.

| Botão | Atributos obrigatórios | Efeito |
|-------|------------------------|--------|
| Prévia | `type="submit" name="acao" value="previa"` | Valida e calcula o resumo no servidor; não grava |
| Confirmação | `type="submit" name="acao" value="registrar"` | Revalida tudo na transação, grava e redireciona para P08 |

- O valor é comparado exatamente (minúsculas, sem espaços) e deve vir uma única vez no POST.
- Enter dentro de um campo envia o **primeiro** botão de envio do formulário: mantenha a prévia antes da confirmação no HTML. Um envio sem botão (por exemplo, `form.submit()` em JavaScript) não grava nada.
- O backend continua sendo a fonte de verdade: diárias, diária e total são recalculados no registro, nunca lidos da tela.
- A página provisória só mostra o botão de confirmação depois de uma prévia válida. Mostrar a confirmação desde o início é decisão do frontend, desde que o resumo apareça antes do registro (D13).

## Prévia (D13)

- **Base sem JavaScript:** o botão `name="acao" value="previa"` envia o mesmo formulário; o backend valida datas, cliente e disponibilidade, calcula com as **mesmas funções do registro** (`calcular_resumo`) e devolve a página com `resumo`, sem gravar. Na página provisória, o botão Registrar só aparece depois da prévia.
- **JavaScript (proposta do contrato, arquivo de Raphael):** `diarias_equipamentos` já chega via `{{ diarias_equipamentos|json_script:"diarias-equipamentos" }}`, para um script em `static/js/` calcular a prévia ao vivo. Nenhum JavaScript foi criado nesta etapa, nem API nova.
- Em qualquer caso, o registro **relê a diária no banco e recalcula**; o valor definitivo aparece em P08.
- Aviso de ausência de cancelamento: sempre visível em P07. Texto **provisório** (indefinido no EQF-5): "depois de registrado, o aluguel não pode ser cancelado nem editado".

## Serviços (`alugueis/services.py`)

| Função | Regra |
|--------|-------|
| `validar_datas_do_aluguel` | Retirada ≥ data atual (America/Recife; futura permitida, I1); prevista ≥ retirada. Devolve os dois erros juntos |
| `calcular_resumo` | Diárias inclusivas `(prevista − retirada) + 1` e valor `Decimal` com duas casas, pelas funções do modelo |
| `simular_aluguel` | Prévia: mesmas validações, sem bloqueio e sem gravar |
| `registrar_aluguel` (DEV-03, ampliado) | Bloqueia equipamento → cliente; revalida disponibilidade; copia a diária atual; grava aberto. Cliente inexistente vira erro de campo (antes era exceção); `IntegrityError` do índice parcial vira "Este equipamento não está disponível para aluguel." |
| `registrar_devolucao` | Bloqueia equipamento → aluguel; recusa aluguel encerrado ("Este aluguel já foi encerrado."), data anterior à retirada e data futura; grava só `data_devolucao_real`, com gravação condicional (`WHERE data_devolucao_real IS NULL`) além do bloqueio |

### Cálculo financeiro e datas

- Diária contratada = diária do equipamento **no momento do registro**, lida dentro da transação. Mudanças posteriores da diária não afetam aluguéis registrados (CT05).
- Valor contratado = diárias × diária, em `Decimal`, gravado no registro e **nunca recalculado**, nem na devolução em atraso. Sem multa.
- O equipamento fica indisponível assim que o aluguel é registrado, mesmo com retirada futura (I1). Na devolução, volta a ficar disponível se estiver ativo; se estiver inativo, continua indisponível.
- Data atual = `timezone.localdate()` em America/Recife, nunca o dia UTC (testado com 01h30 UTC, que ainda é o dia anterior em Recife).

### Situação (RN004, calculada; sem coluna de status)

| Situação | Condição |
|----------|----------|
| Ativo | Aberto e prevista ≥ data atual |
| Atrasado | Aberto e prevista < data atual |
| Encerrado | Devolvido até a prevista |
| Encerrado com atraso | Devolvido depois da prevista |

`pode_devolver`: aberto e data atual ≥ retirada (I1). Retirada futura aparece como Ativo, sem o link de devolução.

## Concorrência

Protocolo de bloqueios, sempre com o equipamento primeiro:

| Operação | Ordem |
|----------|-------|
| Registro de aluguel | equipamento → cliente |
| Devolução | equipamento → aluguel |
| Edição, exclusão, inativação, reativação de equipamento | equipamento |
| Edição de cliente | cliente |

Ninguém espera por um equipamento segurando um cliente ou um aluguel: não há ciclo de espera.

| # | Cenário | Teste | Tipo |
|---|---------|-------|------|
| 1 | Dois registros do mesmo equipamento | `alugueis/tests/test_concorrencia.py` (DEV-03) | Concorrência real (bloqueio) |
| 1b | Duas gravações sem passar pelo serviço | `alugueis/tests/test_concorrencia.py` | Só restrição: o índice parcial barra o segundo aberto |
| 2 | Duas devoluções do mesmo aluguel | `alugueis/tests/test_concorrencia_devolucao.py` | Concorrência real: a segunda espera e recebe "Este aluguel já foi encerrado."; a data não é corrigida |
| 3, 4, 5 | Registro × inativação, exclusão e troca de código | `equipamentos/tests/test_concorrencia.py` (DEV-04) | Concorrência real, nas duas ordens |
| 6 | Devolução × novo aluguel, inativação e edição do equipamento | `alugueis/tests/test_concorrencia_devolucao.py` | Concorrência real: a operação seguinte espera a devolução e decide com o aluguel já encerrado |

Verificação de sensibilidade feita durante o desenvolvimento:

- **Sem os bloqueios da devolução:** os três testes do cenário 6 falham. As duas devoluções simultâneas continuam barradas pela gravação condicional.
- **Sem bloqueios e sem a gravação condicional:** o teste de duas devoluções também falha.

No SQLite, todos esses testes são pulados e não servem de evidência.

## Filtro do histórico (RF010)

`AluguelQuerySet.na_situacao(situacao, hoje)` (`alugueis/models.py`) filtra no banco com a mesma regra de `Aluguel.situacao_codigo` (RN004 g); a view passa `timezone.localdate()`, a data atual em America/Recife, calculada uma vez por requisição.

| Opção (`situacao`) | Aluguéis |
|--------------------|----------|
| Todas (`""`) | Todos, como no RF008 |
| `ativo` | Sem devolução e devolução prevista igual ou posterior à data atual (inclui retirada futura) |
| `atrasado` | Sem devolução e devolução prevista anterior à data atual |
| `encerrado` | Devolvidos até a devolução prevista |
| `encerrado_com_atraso` | Devolvidos depois da devolução prevista |

- Valor vazio, "todas", maiúsculas ("ATIVO") ou qualquer valor fora da lista valem "Todas"; o queryset recusa código desconhecido com `ValueError`, então o valor da URL nunca chega cru ao filtro.
- A ordem é a do histórico sem filtro (`-data_retirada`, `-pk`), conforme a decisão técnica do EQF-5 (comentário 10078).
- Filtro sem resultado: "Nenhum registro encontrado." e "Limpar filtro", sem linhas; sem filtro e sem aluguéis, o estado vazio do CT16 não muda.
- Só leitura (`@require_safe`), uma consulta para a lista, como sem filtro.
- O template recalcula a situação de cada linha com a própria data atual: na virada da meia-noite em Recife, uma linha pode aparecer com a situação do novo dia (mesmo comportamento já existente em `pode_devolver`).

## Segurança

Login obrigatório; POST com CSRF; GET não grava; 405 e 404 previsíveis. Nenhum campo financeiro, `id` ou vínculo extra enviado pelo navegador é usado. POST inválido não grava nada: o registro é uma transação única. A seleção de clientes não mostra o CPF completo. Mensagens não expõem dados internos.

## Integração visual (Raphael)

- Trocar os três templates provisórios mantendo nomes de campos, `{% csrf_token %}`, os dois botões de P07 com `name="acao"` (`previa` e `registrar`, ambos obrigatórios), `form.non_field_errors` em P07 e P09 e os links por `{% url %}`.
- Valores: `|floatformat:"2g"` produz `1.500,00` com a localização pt-br; datas com `|date:"d/m/Y"`.
- `situacao_codigo` (`ativo`, `atrasado`, `encerrado`, `encerrado_com_atraso`) serve para o estilo do selo; o texto é `situacao`.
- Filtro do RF010 em P08: formulário GET com `<select name="situacao">` montado de `opcoes_situacao`, opção marcada por `situacao_selecionada`, "Limpar" com filtro ativo e "Limpar filtro" no estado vazio filtrado. O formulário não pode conter "R$" nem "Registrar devolução" (teste do CT16). Revisado por Raphael em 11/11/2026 (EQF-43).
- Textos indefinidos no EQF-5 (provisórios nos templates): aviso de não cancelamento, "Nenhum cliente cadastrado.", "Nenhum equipamento disponível para aluguel." e a explicação da devolução antes da retirada.

## Testes

| Arquivo | Testes | Cobertura |
|---------|--------|-----------|
| `alugueis/tests/test_devolucao_e_previa.py` | 15 | Resumo e Decimal, prévia sem gravar, recusas, cliente inexistente, erros de data juntos, nova diária, devolução hoje e em atraso, datas fora do intervalo, retirada futura, segunda devolução, equipamento inativo, inexistente, campos preservados |
| `alugueis/tests/test_views.py` | 27 | P07 (contexto, seleção, prévia, registro, datas, indisponível, cliente inexistente, valores manipulados, corrida entre formulário e serviço, data atual em Recife), P08 (vazio, quatro situações, valores congelados, inativo, ordem, consultas), P09 (contexto, devolução, datas, segunda devolução, retirada futura, 404), segurança |
| `alugueis/tests/test_cenarios_ct.py` | 8 | CT11–CT16, CT19 e CT20 automatizados |
| `alugueis/tests/test_filtro_historico.py` | 16 | RF010: filtro igual a `situacao_codigo` nos limites e em outras datas, situações disjuntas, código inválido no queryset, cada situação na tela com a opção marcada, ordem, Todas/vazio/desconhecido, opções, devolução nos abertos, estados vazios com e sem filtro, data de Recife, só `SELECT`, 3 consultas, login e POST 405 |
| `alugueis/tests/test_concorrencia_devolucao.py` | 4 | Cenários 2 e 6 (só PostgreSQL) |
| `alugueis/tests/test_confirmacao.py` | 10 | Confirmação explícita: prévia não grava; só `acao=registrar` grava; sem ação, ação desconhecida, vazia ou repetida não gravam; valores manipulados; duplo clique; dados preservados nos erros; retirada futura |
| `alugueis/tests/test_concorrencia_confirmacao.py` | 1 | Duas confirmações simultâneas pela view: um único aluguel aberto, a segunda recebe erro de campo (só PostgreSQL) |

CT11–CT16 foram **automatizados**, não executados manualmente. As expectativas seguem `docs/rastreabilidade.md`: CT11, 3 diárias a R$ 50,00 = R$ 150,00; CT12, recusa de equipamento com aluguel ativo; CT13, devolução com a data atual libera o equipamento; CT14, segunda devolução recusada; CT15, histórico com dados e situação; CT16, histórico vazio com mensagem e sem dados inexistentes. A auditoria QA-AUD-01 não estava disponível; se ela corrigir alguma expectativa, os testes devem ser ajustados.

## Pendências

1. Aceite do contrato (PR #2): variável nova `resumo`, campo `acao` (`previa`/`registrar`), prévia no servidor × JavaScript, CPF mascarado na seleção.
2. Textos indefinidos no EQF-5: aviso de não cancelamento, ausência de opções, indicação de atraso, cliente inexistente e ação ausente ou inválida. As mensagens de sucesso do registro e da devolução ("Aluguel registrado com sucesso." e "Devolução registrada com sucesso.") seguem o padrão de implementação adotado em 04/11/2026, sem aprovação formal; a prévia não envia mensagem.
3. QA-AUD-01 e validação acadêmica de CT11–CT16, CT19 e CT20.
4. DEV-07 (EQF-19): registrar no Jira que o RF008 foi implementado aqui, e definir o que resta para a atividade.
5. RF010 (EQF-43): revisão do template P08 por Raphael; o texto do PR #2 não prevê parâmetro nem variáveis de filtro para P08 e precisa ser revisto em separado.
