# Gestão operacional de clientes — DEV-05 (EQF-17)

> **Situação em 02/11/2026: implementação local, não publicada.** Branch `feat/backend-eqf-17-clientes`, criada a partir de `feat/backend-eqf-16-equipamentos` (`657627a`), que está sobre DEV-03 (`ba0493a`) e DEV-02 (`87d23fb`). **O PR de Clientes depende da integração das bases anteriores (DEV-02, DEV-03 e DEV-04)**; abri-lo antes misturaria entregas. Rotas, nomes de template e variáveis seguem o contrato técnico **proposto** no PR #2 (v0.4), ainda sem aceite de Raphael. As páginas HTML são **provisórias**.

Escopo: RF005 (cadastrar, listar, consultar pela lista e editar), com RN002, RN003, I5, D12 e D14. Fora do escopo: exclusão de cliente (RN003), pesquisa e página de detalhe (D14), endereço, registro de aluguel e devolução (DEV-06).

## Classificação das fontes

| Tipo | O que foi usado |
|------|-----------------|
| Regras aprovadas | RF005, RN002, RN003, I5 (CPF com 11 dígitos), D12 (CPF e telefone), D14 (sem pesquisa e sem detalhe) |
| Proposta técnica (PR #2, sem aceite) | Rotas `clientes:lista`, `clientes:criar`, `clientes:editar`; templates `clientes/lista.html` e `clientes/formulario.html`; variáveis `object_list`, `empty_message`, `form`, `object`, `cpf_editavel`; colunas de P05; CPF e telefone formatados na edição |
| Mensagens | Textos propostos no EQF-5 (`config/mensagens.py`); sucesso "Indefinida" |
| Aguardam validação acadêmica | Documento v1.1 (inclusive se D12 exige atualização) e cenários CT09–CT10 (equipe de Testes) |

## Campos e regras

| Campo | Obrigatório | Regra no backend |
|-------|-------------|------------------|
| `nome_completo` | Sim | Espaços das extremidades removidos; não vazio; até 150 caracteres |
| `cpf` | Sim | Remove só pontos e hífen (em qualquer posição) e recusa qualquer outro caractere, inclusive espaço, vírgula, barra e letra; exatamente 11 dígitos; dígitos verificadores válidos; recusa os 11 dígitos iguais; único (índice `cliente_cpf_unico`); persiste só os dígitos (I5); imutável após o primeiro aluguel, aberto ou encerrado |
| `telefone` | Não | Remove parênteses, espaços e hífen (interpretação técnica de D12 para a "máscara usual"); recusa outros caracteres (inclusive `+` e ponto); 10 ou 11 dígitos, com DDD; persiste só os dígitos. Não há validação de DDD além do tamanho (não especificada) |
| `email` | Não | Formato válido quando informado; sem unicidade (não prevista); nenhum e-mail é enviado |

A normalização e a validação ficam no modelo (`clientes/validadores.py` e `Cliente.normalizar()`), já existentes desde o DEV-03; o formulário não duplica essas regras. Ele só limita o tamanho bruto da entrada a 20 caracteres (CPF e telefone), antes da normalização. O campo `cpf` do formulário não remove espaços das extremidades (`strip=False`): pela letra de D12, só pontos e hífen são removidos.

## Rotas e fluxos

| Página | Rota (nome) | Método | Comportamento |
|--------|-------------|--------|---------------|
| P05 — lista | `/clientes/` (`clientes:lista`) | GET | Todos os clientes, por `nome_completo` e, no empate, pela ordem de cadastro (`pk`). Colunas: nome completo, CPF formatado, telefone formatado, e-mail, Editar. Sem clientes: "Nenhum registro encontrado." Sem pesquisa: `?q=` é ignorado. Sem paginação (não prevista) |
| P06 — cadastro | `/clientes/novo/` (`clientes:criar`) | GET, POST | Sucesso → P05 (POST/redirect/GET); erro → mesma página (200) com erros por campo |
| P06 — edição | `/clientes/<pk>/editar/` (`clientes:editar`) | GET, POST | CPF e telefone aparecem formatados. Com aluguel registrado, o CPF fica somente leitura, com a explicação |

Não existem `clientes:detalhe`, `clientes/detalhe.html`, rota de exclusão nem endpoint JSON. Todas as rotas exigem login; GET nunca grava; outros métodos recebem 405; `pk` inexistente recebe 404 (GET e POST). Clientes não são registrados no Django Admin (D15).

## Formulário (`clientes/forms.py`)

`ClienteForm` (ModelForm) com apenas `nome_completo`, `cpf`, `telefone` e `email`. `id`, `pk` e qualquer outro campo enviado são ignorados. Erros usam os textos do EQF-5: "Preencha os campos obrigatórios.", "CPF inválido.", "Já existe um cliente com este CPF.", "Informe um telefone com DDD e 10 ou 11 dígitos.", "E-mail inválido." e "O CPF não pode ser alterado porque o cliente já possui aluguel registrado.".

Com `cpf_editavel=False`, o campo `cpf` fica `disabled`: o Django usa o valor gravado e descarta o enviado. **Não é a única barreira**: o serviço de edição revalida o histórico sob bloqueio e recusa a troca.

## Serviços (`clientes/services.py`)

| Função | Regra |
|--------|-------|
| `cadastrar_cliente(dados)` | Grava só os campos editáveis, com validação completa. Se dois cadastros simultâneos passarem juntos pela validação, o índice único decide e o perdedor recebe "Já existe um cliente com este CPF." como erro de campo (nunca 500). A conferência depois do `IntegrityError` refaz a consulta, em vez de interpretar o texto do erro, que muda entre bancos |
| `editar_cliente(pk, dados)` | Bloqueia a linha do cliente (`select_for_update`), revalida o histórico e recusa a troca de CPF se houver qualquer aluguel. Nome, telefone e e-mail continuam editáveis com histórico |

### Comportamento da edição do CPF

| Situação | Resultado |
|----------|-----------|
| Mesmo CPF reenviado sem alteração | Aceito (não é alteração) |
| Mesmo CPF com outra pontuação (com máscara `000.000.000-00` ou só dígitos) | Aceito; comparação feita depois da normalização |
| Outro CPF válido, cliente sem aluguel | Aceito, se não pertencer a outro cliente |
| Outro CPF válido, cliente com aluguel aberto ou encerrado | Pela tela: campo somente leitura, valor enviado ignorado, demais campos gravados. Pelo serviço: recusado com a mensagem de CPF bloqueado |
| CPF de outro cliente | Recusado: "Já existe um cliente com este CPF." |
| Dados inválidos | Nada é gravado; erros por campo (200) |
| Cliente inexistente | 404 |

## Concorrência

Protocolo de bloqueios: `registrar_aluguel` bloqueia **equipamento → cliente**; a edição de equipamento bloqueia só o equipamento (DEV-04); a edição de cliente bloqueia **só o cliente** e nenhuma linha de equipamento. Nenhuma operação espera por um equipamento enquanto segura um cliente, então não há ciclo de espera (impasse).

| Cenário (primeira → segunda) | Resultado verificado |
|------------------------------|----------------------|
| A — troca de CPF → primeiro aluguel | O aluguel espera o bloqueio do cliente; os dois gravam (ordem serial edição → aluguel); a partir daí o CPF está congelado |
| B — primeiro aluguel → troca de CPF | A edição espera, encontra o histórico e é recusada; CPF original mantido |
| C — dois cadastros com o mesmo CPF (com e sem pontuação) | A segunda gravação espera no índice único; um cliente gravado, o outro recebe erro de campo; banco segue utilizável |
| Duas edições para o mesmo CPF | Só a primeira grava; a segunda recebe erro de campo |

`clientes/tests/test_concorrencia.py` executa esses quatro casos com threads e conexões separadas no PostgreSQL e confirma que a segunda operação fica parada enquanto a primeira transação está aberta. Verificação de sensibilidade feita durante o desenvolvimento: sem o `select_for_update()` da edição, o cenário B falha (o CPF é trocado depois do aluguel). No SQLite esses testes são pulados e não servem de evidência de bloqueio.

## Privacidade

- CPF, telefone e e-mail são `sensitive_post_parameters` nas views de cadastro e edição: relatórios de erro do Django mascaram esses campos.
- Nenhum código novo registra CPF em log. Um teste captura os logs de cadastro válido, duplicado e inválido, de 404 e de 405 e confirma que nenhum CPF aparece.
- Testes usam CPFs fictícios gerados com dígitos verificadores válidos (`config/tests/fabricas.py`).
- `Cliente.__str__` (DEV-03) inclui o CPF formatado; nenhuma tela ou log desta etapa o usa.

## Integração com o frontend (Raphael)

- `clientes/lista.html`: `object_list` (atributos `nome_completo`, `cpf_formatado`, `telefone_formatado`, `email`, `pk`) e `empty_message`, dentro de `{% empty %}`.
- `clientes/formulario.html`: `form`; na edição, também `object` e `cpf_editavel`. Manter `method="post"`, `{% csrf_token %}`, os nomes dos campos e a exibição de `form.non_field_errors` e dos erros de cada campo.
- Máscaras de CPF e telefone podem ser só visuais: o backend aceita a entrada com ou sem máscara e normaliza.
- Os templates provisórios não têm Bootstrap nem herança de `base.html`; podem ser substituídos sem alterar serviços, formulário ou views.

## Testes

| Arquivo | Testes | Cobertura |
|---------|--------|-----------|
| `clientes/tests/test_servicos.py` | 8 | Cadastro normalizado, campos extras, CPF inválido, corrida de CPF duplicado, edição com e sem histórico, CPF de outro cliente, cliente inexistente |
| `clientes/tests/test_views.py` | 34 | Itens 1–30 da tarefa 11C (cadastro, listagem, edição), `IntegrityError` sem 500, consultas da lista, login, CSRF, métodos, ausência de exclusão, logs sem CPF, mascaramento em relatórios de erro, Admin |
| `clientes/tests/test_cenarios_ct.py` | 2 | CT09 e CT10 automatizados |
| `clientes/tests/test_concorrencia.py` | 4 | Cenários A, B e C e edições simultâneas (só PostgreSQL) |

CT09 e CT10 foram **automatizados**, não executados manualmente: CT09 cadastra cliente com nome e CPF válidos, sem contatos, e o encontra na lista; CT10 recusa CPF já cadastrado, com e sem pontuação. As correções recomendadas na auditoria QA-AUD-01 **não estavam disponíveis** nesta sessão (nem no repositório); os testes seguem a descrição dos cenários em `docs/rastreabilidade.md`.

O executor de corridas passou a ser comum (`config/tests/concorrencia.py`) e é usado também pelos testes de concorrência de equipamentos. O utilitário que leva erros de serviço ao formulário também foi extraído (`config/formularios.py`) e é usado por equipamentos e clientes.

## Divergências e pendências

1. **Contrato, seção 7:** classes do Bootstrap 5.3 nos widgets. Resolvido na preparação do DEV-07: todos os formulários aplicam `form-control`/`form-select` e `is-invalid` nos campos com erro (`config/formularios.py`; veja [`integracao-frontend-dev07.md`](integracao-frontend-dev07.md)).
2. **Contrato, seção 5, item 2:** sucesso com mensagem do framework `messages`, mas o EQF-5 não define o texto ("Indefinida"); nenhuma mensagem de sucesso é enviada, como no DEV-04.
3. **Espaços nas extremidades do CPF:** recusados (leitura literal de D12). Se a equipe preferir aceitá-los, a mudança é só `strip=True` no formulário; registrar para a equipe de Requisitos.
4. **Ordenação de P05:** por nome e, no empate, pela ordem de cadastro. A comparação de maiúsculas e acentos segue a collation do banco (PostgreSQL e SQLite diferem).
5. Aceite do contrato (PR #2) por Raphael; validação acadêmica de D12, CT09 e CT10; QA-AUD-01.
6. DEV-06: registro de aluguel pela interface (seleção de cliente, que pode usar `Cliente.__str__`) e devolução.
