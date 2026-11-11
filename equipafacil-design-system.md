# EquipaFácil — Design System

Sistema web administrativo de aluguel de equipamentos. Projeto acadêmico ADS/UNIBRA.
Stack: Django Templates + Bootstrap 5.3 · Tokens v1 · Gerado em 02/11/2026.

> Nota para o Claude Code: este arquivo é a conversão do PDF do design system. Na implementação deste repositório, o Bootstrap fica **local** em `static/vendor/bootstrap/` (o contrato do projeto proíbe CDN). Onde o guia da seção 5 mostra CDN, use os arquivos locais.

## Sumário

1. Visão geral
2. Tokens
3. Componentes
4. Mapa de telas (P01–P10)
5. Guia de implementação (Django + Bootstrap 5.3)
6. Limitações e decisões provisórias

---

## 1. Visão geral

Quem usa: funcionários autenticados que cadastram equipamentos e clientes e registram aluguéis e devoluções. A interface deve parecer um sistema de trabalho real: clara, previsível e rápida de operar no balcão.

Protótipo navegável (P01–P10): login de demonstração `funcionario` / `demo123`.

Status: proposta visual para validação com Rickelme (backend) e Raphael (frontend). Paleta, tipografia e textos de mensagem são sugestões, não identidade aprovada.

### Princípios

- **A tarefa primeiro.** Cada tela tem uma ação principal (um único `btn-primary`), sempre no mesmo lugar: canto direito do cabeçalho nas listagens, fim do formulário nos cadastros.
- **Estado visível.** Disponibilidade, situação do cadastro e situação do aluguel aparecem sempre como badge com texto. Nada depende só da cor.
- **Regra explicada, não escondida.** Quando ação ou campo está bloqueado por regra de negócio, a interface diz o motivo ao lado (código com histórico, CPF após primeiro aluguel, exclusão com histórico).
- **Números de balcão.** Valores em reais com `tabular-nums`, datas `dd/mm/aaaa`, códigos e CPF em fonte mono.

### Voz e textos

- Português do Brasil, frases curtas, voz ativa.
- Botão diz o que acontece: "Registrar aluguel", "Confirmar devolução", "Excluir definitivamente".
- Erro diz o que corrigir: "Informe o telefone com DDD: 10 ou 11 dígitos." Sem "Ops", sem pedir desculpas.
- Sucesso confirma o objeto: "Equipamento Furadeira Bosch cadastrado com sucesso."
- Termos do domínio: diária, diária contratada, devolução prevista, data real de devolução, em aberto, inativo.

### Ícones

- Traço de 1.75px, 24×24, cantos arredondados, cor herdada (`currentColor`).
- Recomendação: Bootstrap Icons (`bi-house`, `bi-box-seam`, `bi-people`, `bi-plus-lg`, `bi-clock-history`, `bi-pencil`, `bi-three-dots`, `bi-arrow-return-left`, `bi-pause-circle`, `bi-play-circle`, `bi-trash`, `bi-box-arrow-right`).
- Ícones sempre ao lado de texto e com `aria-hidden="true"`.
- Sem logotipo aprovado: a marca é o nome "EquipaFácil" em Plex Sans 700 com monograma "E" provisório.

### Responsividade

| Faixa | Comportamento |
|---|---|
| ≥ 992px | barra lateral fixa + conteúdo; formulários em 2 colunas; resumo do aluguel ao lado |
| 768–991px | barra lateral vira gaveta (offcanvas); resumo vai para baixo do formulário |
| < 768px | formulário em 1 coluna; botões 100% de largura; tabelas viram cartões empilhados; alvos de toque ≥ 40px |

### Acessibilidade

Labels em todos os campos, foco visível (`focus-ring`), navegação completa por teclado, `aria-invalid` + `aria-describedby` nos erros, `aria-current="page"` no menu, badges com texto, modais que fecham com Esc e devolvem o foco.

---

## 2. Tokens

Tema claro é o principal; escuro é opcional (proposta). Use sempre os tokens, nunca o hex direto.

### Cores

| Token | Claro | Escuro | Uso |
|---|---|---|---|
| primary | #2563eb | #4f86f7 | Ação principal (btn-primary), links, item ativo, foco. Texto branco sobre ele |
| primary-hover | #1d4ed8 | #6b9af8 | Hover/pressed de btn-primary |
| primary-dark | #1e3a8a | #1b2f6b | Fundo da barra lateral e blocos de identidade |
| primary-soft | #eff4ff | #16254a | Fundo de badge "Ativo", alerta informativo, ícones de atalho |
| on-primary | #ffffff | #ffffff | Texto/ícones sobre primary, primary-dark, success e danger |
| success | #16a34a | #22c55e | Preenchimento de btn-success (Reativar) e ponto de status. Para texto use success-text |
| success-text | #15803d | #4ade80 | Texto de sucesso sobre success-soft ou surface (4.5:1) |
| success-soft | #ecfdf3 | #0f2a1b | Fundo de badge "Disponível"/"Encerrado" e alerta de sucesso |
| warning | #d97706 | #f59e0b | Preenchimento de btn-warning (Inativar), com texto escuro |
| warning-text | #b45309 | #fbbf24 | Texto de atenção: "Alugado", "Encerrado com atraso", motivo de ação bloqueada |
| warning-soft | #fff7e8 | #2e2210 | Fundo de badge de atenção e do aviso "não poderá ser cancelado" |
| danger | #dc2626 | #ef4444 | Borda de campo inválido, btn-danger (Excluir). Para texto use danger-text |
| danger-text | #b91c1c | #f87171 | Mensagem de erro de validação e badge "Atrasado" |
| danger-soft | #fef1f1 | #2e1517 | Fundo de alerta de erro e badge "Atrasado" |
| bg | #f8fafc | #0b1120 | Fundo da página |
| surface | #ffffff | #111a2e | Cards, tabelas, modais, campos, cabeçalho |
| surface-2 | #f1f5f9 | #16213a | Cabeçalho de tabela, campo somente leitura, input-group-text, ícone de estado vazio |
| text | #0f172a | #e6ecf7 | Texto principal |
| muted | #526077 | #9aa8c0 | Texto secundário, ajuda de campo, rótulos de tabela (4.5:1) |
| border | #e2e8f0 | #22304d | Divisórias de card e linhas de tabela (decorativas) |
| border-strong | #94a3b8 | #4a5b80 | Borda de campos e btn-outline-secondary (3:1) |
| sidebar-text | #dce6ff | #c9d6f5 | Texto dos itens da barra lateral sobre primary-dark |
| sidebar-active | #2b4ba8 | #1e3270 | Fundo do item de menu ativo na barra lateral |
| focus-ring | rgba(37,99,235,0.35) | rgba(79,134,247,0.45) | Halo de foco (box-shadow 0 0 0 4px) |

Contraste: texto colorido usa a variante `-text` (4.5:1 sobre o fundo `-soft` e sobre `surface`). As cores de preenchimento (success, warning, danger) são para botões e pontos de status.

### Tipografia

```
sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif
mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace
```

Pesos: 400 texto, 500 rótulos e botões, 600 títulos, 700 apenas o valor total do aluguel.

| Estilo | Especificação | Uso |
|---|---|---|
| display | 24px/32px, peso 600 | Boas-vindas da página inicial (P01) |
| page-title | 20px/28px, peso 600 (17px no mobile) | Título da página (h1) |
| section-title | 16px/24px, peso 600 | Título de card, modal e estado vazio |
| body | 15px/22px, peso 400 | Texto corrido e valores de campo |
| table | 14px/20px, peso 400 | Células de tabela e alertas |
| label | 14px/20px, peso 500 | Rótulos de formulário e botões |
| help | 13px/18px, peso 400 | Texto de ajuda e erros de campo |
| overline | 12px/16px, peso 600, maiúsculas | Cabeçalho de tabela e rótulos de seção da barra lateral |
| code | 14px/20px, peso 400, mono | Código do equipamento, CPF e identificadores (P01–P10) |

### Espaçamento (escala de 4px)

| Token | Valor | Uso |
|---|---|---|
| space-1 | 4px | Espaço entre ícone e texto pequeno |
| space-2 | 8px | Gap entre botões lado a lado; badge e ícone |
| space-3 | 12px | Padding vertical de células de tabela; gap de ações |
| space-4 | 16px | Gutter mínimo no mobile; padding de card no mobile; gap de grid de atalhos |
| space-5 | 20px | Padding de card e modal no desktop; gap entre campos |
| space-6 | 24px | Gutter lateral do conteúdo no desktop |
| space-8 | 32px | Separação entre blocos maiores |
| space-12 | 48px | Padding do estado vazio |

### Raios

| Token | Valor | Uso |
|---|---|---|
| radius-sm | 6px | Chips de identificador e elementos pequenos |
| radius-md | 8px | Botões, campos, alertas, itens de menu |
| radius-lg | 12px | Cards, tabelas e modais |
| radius-pill | 999px | Badges de situação |

### Sombras

| Token | Valor | Uso |
|---|---|---|
| shadow-sm | 0 1px 2px rgba(15,23,42,0.06) | Cards em repouso |
| shadow-md | 0 8px 24px rgba(15,23,42,0.10) | Modais, toasts e hover de cartões de atalho |

---

## 3. Componentes

Todos usam classes do Bootstrap 5.3, então a mesma marcação funciona no Django.

### Button

- **Um único `btn-primary` por tela**: a ação que conclui a tarefa (Salvar, Registrar aluguel, Confirmar devolução, Entrar).
- `btn-outline-secondary` para Voltar, Editar, Ações e Cancelar.
- `btn-outline-primary` para "Registrar devolução" em aluguel Ativo; vira `btn-primary` quando o aluguel está Atrasado.
- `btn-warning` = Inativar, `btn-success` = Reativar, `btn-danger` = Excluir. Só aparecem no painel de ações (P04).
- Ação bloqueada: `disabled` + motivo visível ao lado (nunca só o botão cinza).
- Rótulo = verbo do que acontece. Ícone opcional à esquerda, 16px, `aria-hidden`.
- Altura mínima 40px (34px no `btn-sm`); no mobile os botões de formulário ocupam 100% da largura e o primário fica em cima.

### FormField

Ordem: `form-label` → `form-control`/`form-select` → `form-text` → `invalid-feedback`.

- Todo controle tem `<label for>`. Obrigatório: asterisco `.req` e a legenda "* Campo obrigatório" no fim do formulário.
- Opcional: "(opcional)" em `text-muted` ao lado do rótulo.
- Erro: classe `is-invalid`, `aria-invalid="true"`, mensagem em `invalid-feedback` ligada por `aria-describedby`. A mensagem diz o que corrigir.
- Ao enviar com erros: alerta-resumo no topo e foco no primeiro campo inválido.
- Campo bloqueado por regra (código com histórico, CPF após primeiro aluguel): `readonly` + `form-text` explicando o motivo. A view também deve ignorar o valor enviado.
- Código e CPF em fonte mono; valores e datas com `tabular-nums`.
- Desktop: 2 colunas (`row g-3` + `col-md-6`); mobile: 1 coluna.

Exemplos de texto: "CPF inválido. Confira os 11 dígitos." / "O código não pode ser alterado porque este equipamento já possui histórico de aluguel."

### Badge

Pílulas de estado; a cor sempre vem acompanhada de texto.

| Contexto | Texto | Classe |
|---|---|---|
| Disponibilidade do equipamento | Disponível | badge-success |
| | Alugado | badge-warning |
| | Indisponível (inativo) | badge-neutral |
| Situação do cadastro | Ativo | badge-outline |
| | Inativo | badge-neutral |
| Situação do aluguel | Ativo | badge-primary |
| | Atrasado | badge-danger |
| | Encerrado | badge-success |
| | Encerrado com atraso | badge-warning |

A disponibilidade é calculada (ativo e sem aluguel em aberto); não é campo editável. A situação do aluguel também é derivada das datas: o template só exibe o valor que a view entregar.

### Table

- Tabela de listagem dentro de um `card`, cabeçalho em overline sobre `surface-2`.
- Valores monetários e quantidades à direita com `tabular-nums`; código e CPF em mono.
- Coluna de ações por último, à direita, com `btn-sm`. Linha de equipamento inativo fica em `muted`.
- Abaixo de 768px a tabela vira lista de cartões: `thead` oculto e cada `td` mostra o rótulo via `data-label`. Alternativa aceita: `table-responsive` com rolagem horizontal só na tabela.
- Toolbar acima da tabela: pesquisa em Equipamentos (RF002) e em Clientes (RF009, D16, que revisa a D14); filtro por situação no Histórico (RF010).
- Sem resultados ou sem registros: substituir a tabela inteira por EmptyState. Nunca mostrar linhas fictícias.

Exemplo de colunas: CÓDIGO · NOME · DIÁRIA · DISPONIBILIDADE · ações.

### Alert

Mapeiam para `django.contrib.messages` (`success`, `error`, `warning`, `info`).

- Sucesso após salvar: alerta no topo da listagem de destino (Post/Redirect/Get) e, opcionalmente, toast.
- Erro de formulário: um alerta-resumo + erro por campo.
- Atenção: aviso fixo do Novo aluguel e atraso na devolução.
- Informação: login obrigatório, aluguel já encerrado.
- Sempre ícone + texto; `role="alert"` só para erro.

Textos sugeridos (não homologados):
- "Equipamento Furadeira Bosch cadastrado com sucesso."
- "Corrija os 2 campos destacados para salvar."
- "Atenção: o aluguel não poderá ser cancelado nesta versão do sistema."
- "Faça login para acessar o sistema."

### EmptyState

Substitui a tabela quando não há linhas: ícone, título que diz o que falta, uma frase e uma ação.

- Lista vazia: "Nenhum equipamento cadastrado" / "Cadastre o primeiro equipamento para começar a registrar aluguéis." / botão "Novo equipamento".
- Pesquisa sem resultado: "Nenhum resultado para “termo”" / "Pesquise pelo nome ou pelo código do equipamento." / link "Limpar pesquisa" (URL sem `?q=`).
- Histórico vazio: "Nenhum aluguel registrado" + "Novo aluguel".
- No Django: bloco `{% empty %}` do `{% for %}` ou `{% if not object_list %}`.

### Modal

Diálogo do Bootstrap (`modal`, `modal-dialog`, `modal-content`) para confirmação.

- Exclusão exige confirmação explícita. Proposta visual: `btn-danger` desabilitado até digitar o código (uma confirmação simples também atende).
- Cancelar à esquerda, ação destrutiva à direita.
- Fecha com Esc e Cancelar; o foco volta ao botão que abriu.
- A ação real é sempre um `POST` com `{% csrf_token %}`; o modal só envolve o `<form>`.
- Exemplo: título "Excluir equipamento?", alerta "Caixa de som (CXS-005) será removido. Esta ação não pode ser desfeita.", campo "Para confirmar, digite o código CXS-005", botões "Cancelar" e "Excluir definitivamente".

> Decisão tomada neste repositório (P04): confirmação por bloco inline com `<details>`, que funciona sem JavaScript, enviando `confirmacao=sim`.

### ActionPanel (P04)

Interface única para Excluir, Inativar e Reativar, aberta pelo botão "Ações" da listagem. As três ações sempre aparecem; a que não se aplica fica desabilitada com o motivo em `warning-text`.

| Ação | Permitida quando | Motivo exibido quando bloqueada |
|---|---|---|
| Excluir | sem histórico e sem aluguel aberto | "possui histórico de aluguel. Use Inativar." / "Há um aluguel em aberto…" |
| Inativar | ativo e sem aluguel aberto (com ou sem histórico) | "já está inativo" / "Há um aluguel em aberto…" |
| Reativar | inativo, cadastro válido e sem aluguel aberto | "já está ativo" / "O cadastro tem campos inválidos…" |

A view calcula `pode_excluir`, `pode_inativar`, `pode_reativar` e os motivos; o template só exibe. Cada botão é um `<form method="post">` próprio.

Descrições: Inativar = "Deixa de aparecer para novos aluguéis. O histórico é mantido."

### AppShell

Estrutura de todas as telas autenticadas: barra lateral fixa de 248px em `primary-dark`, cabeçalho branco com título (h1) e a ação principal à direita.

- Menu: Início · Cadastros (Equipamentos, Clientes) · Aluguéis (Novo aluguel, Histórico). Item ativo com `aria-current="page"`.
- Rodapé da barra: nome do funcionário (`request.user`), botão Sair (POST para `logout`) e, só no protótipo, a etiqueta "Protótipo demonstrativo — sem integração com backend".
- Abaixo de 992px a barra vira `offcanvas` aberto por botão de menu no cabeçalho.
- O chip `P02` etc. é só para validação do protótipo; remova no sistema final ou deixe atrás de `DEBUG`.

### QuickCard

Cartão de atalho da página inicial; o card inteiro é o link.

- Quatro atalhos: Novo aluguel (destacado em `primary`), Equipamentos, Clientes, Histórico.
- Frase de apoio pode citar contagem simples (ex.: "3 disponíveis para aluguel agora.", "2 aluguéis em aberto."). Opcional; não é indicador financeiro.
- Grade: 4 colunas ≥1100px, 2 em tablet, 1 no mobile.

### RentalSummary (P07)

Painel de prévia ao lado do formulário de Novo aluguel (à direita no desktop, abaixo no mobile).

- Mostra equipamento, cliente, período, quantidade de diárias (inclusiva: retirada e devolução contam), valor da diária e valor total previsto.
- Atualiza a cada mudança de campo com JavaScript simples. Campo vazio mostra "—".
- É apenas prévia: a view recalcula diárias, valores e disponibilidade ao salvar. O valor da diária é congelado no aluguel ("diária contratada").
- Fica dentro do mesmo `<form>`; sem etapa de confirmação adicional.

---

## 4. Mapa de telas

Cada página do protótipo mostra seu identificador (P01–P10) ao lado do título. A rota é sugerida para o `urls.py`.

| Tela | Nome visível | Rota sugerida | Ações | Requisitos e estados |
|---|---|---|---|---|
| P10 | Entrar | `/login/` | Entrar | Usuário e senha obrigatórios; erro de credenciais; aviso "Faça login para acessar o sistema" ao abrir rota protegida; confirmação ao sair. Sem cadastro público, recuperação de senha, login social ou MFA |
| P01 | Início | `/` | Novo aluguel · Equipamentos · Clientes · Histórico · Sair | Boas-vindas com nome do funcionário; atalhos em cartões. Sem gráficos ou indicadores financeiros |
| P02 | Equipamentos | `/equipamentos/` | Pesquisar (nome ou código) · Novo equipamento · Editar · Ações | Colunas: código, nome, categoria, diária, situação, disponibilidade. Estados: lista preenchida, vazia, pesquisa sem resultado |
| P03 | Novo / Editar equipamento | `/equipamentos/novo/` · `/equipamentos/<id>/editar/` | Salvar · Voltar | Código, nome, categoria e diária obrigatórios; descrição opcional; diária > 0 com até 2 casas. Código bloqueado com aviso quando há histórico. Erros por campo + resumo |
| P04 | Ações do equipamento (modal) | POST `/equipamentos/<id>/excluir/` · `/inativar/` · `/reativar/` | Inativar · Reativar · Excluir (com confirmação) | Ações sempre listadas; as não permitidas ficam desabilitadas com motivo. Exclusão pede confirmação |
| P05 | Clientes | `/clientes/` | Novo cliente · Editar | Nome, CPF formatado, telefone formatado, e-mail. Pesquisa por nome ou CPF (RF009, D16), sem página de detalhes (D14). Estado vazio e estado sem resultado |
| P06 | Novo / Editar cliente | `/clientes/novo/` · `/clientes/<id>/editar/` | Salvar · Voltar | Nome completo e CPF obrigatórios; telefone (com DDD) e e-mail opcionais. CPF inválido, duplicado, bloqueado após o primeiro aluguel. Sem excluir |
| P07 | Novo aluguel | `/alugueis/novo/` | Registrar aluguel · Voltar | Cliente, equipamento disponível, retirada ≥ hoje (Recife), devolução prevista ≥ retirada. Painel de resumo (diárias inclusivas, diária, total previsto). Aviso de que o aluguel não pode ser cancelado. Um único formulário |
| P08 | Histórico de aluguéis | `/alugueis/` | Novo aluguel · Registrar devolução (só em aberto) | Colunas: cliente, equipamento, retirada, prevista, devolução real, diárias, diária, valor, situação. Situações: Ativo, Atrasado, Encerrado, Encerrado com atraso. Filtro por situação (RF010): Todas e as quatro situações. Estado vazio sem linhas fictícias |
| P09 | Registrar devolução | `/alugueis/<id>/devolucao/` | Confirmar devolução · Voltar | Dados do aluguel + data real (padrão: hoje). Limites: ≥ retirada e ≤ hoje. Mostra atraso em dias, sem multa. Aluguel encerrado mostra aviso e não permite nova devolução. Após confirmar: situação atualizada e equipamento disponível de novo |

### Fluxo principal

```
P10 Entrar → P01 Início → P02 Equipamentos → P03 Form. equipamento
                                           → P04 Ações
                        → P05 Clientes     → P06 Form. cliente
                        → P07 Novo aluguel
                        → P08 Histórico    → P09 Devolução
```

### Dados demonstrativos do protótipo

- **Equipamentos:** FUR-001 Furadeira Bosch (disponível, com histórico) · PRJ-002 Projetor Epson (alugado) · NTB-003 Notebook Dell (alugado, atrasado) · BET-004 Betoneira (inativo, com histórico) · CXS-005 Caixa de som (disponível, sem histórico, único excluível).
- **Clientes:** Ana Souza, Carlos Oliveira, Mariana Costa, Pedro Almeida (com aluguel: CPF bloqueado) e Lucas Ferreira (sem aluguel: CPF editável). CPFs fictícios da série 123.000.00x-xx.
- **Aluguéis:** Ana/Projetor ativo (3 × R$ 80,00 = R$ 240,00) · Carlos/Notebook atrasado · Mariana/Furadeira encerrado · Pedro/Betoneira encerrado com atraso.

---

## 5. Guia de implementação (Django + Bootstrap 5.3)

O protótipo usa CSS próprio só porque roda sem servidor. As classes foram escolhidas para coincidir com as do Bootstrap.

### 5.1 Base: Bootstrap e tema

Em `templates/base.html` (o PDF usa CDN; neste projeto use os arquivos locais em `static/vendor/bootstrap/`):

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="{% static 'css/equipafacil.css' %}" rel="stylesheet">
...
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="{% static 'js/equipafacil.js' %}"></script>
```

Em `static/css/equipafacil.css`, sobrescreva as variáveis do Bootstrap com os tokens:

```css
:root{
  --bs-primary:#2563EB; --bs-primary-rgb:37,99,235;
  --bs-success:#16A34A; --bs-warning:#D97706; --bs-danger:#DC2626;
  --bs-body-bg:#F8FAFC; --bs-body-color:#0F172A; --bs-secondary-color:#526077;
  --bs-border-color:#E2E8F0; --bs-border-radius:8px; --bs-border-radius-lg:12px;
  --bs-body-font-family:"IBM Plex Sans",system-ui,sans-serif; --bs-body-font-size:.9375rem;
  --ef-sidebar:#1E3A8A;
}
.btn-primary{--bs-btn-bg:#2563EB;--bs-btn-border-color:#2563EB;--bs-btn-hover-bg:#1D4ED8;--bs-btn-hover-border-color:#1D4ED8}
.form-control,.form-select{border-color:#94A3B8;min-height:42px}
.mono{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.badge-status{border-radius:999px;font-weight:500;padding:.3em .8em}
```

Badges: use `text-bg-*` do Bootstrap ou as classes suaves `bg-success-subtle text-success-emphasis`, `bg-warning-subtle text-warning-emphasis`, `bg-danger-subtle text-danger-emphasis`, `bg-primary-subtle text-primary-emphasis`.

### 5.2 Estrutura de templates

```
templates/
  base.html                 # <head>, mensagens, scripts
  base_app.html             # estende base: sidebar + topbar + {% block content %}
  includes/
    _sidebar.html           # menu com item ativo
    _messages.html          # {% for m in messages %} → alert alert-{{ m.tags }}
    _field.html             # label + campo + ajuda + erro
    _empty_state.html       # ícone, título, texto, ação
    _badge_situacao.html    # mapeia situação → classe
  registration/login.html   # P10 (estende base, não base_app)
  core/inicio.html          # P01
  equipamentos/lista.html   # P02 (+ P04)
  equipamentos/form.html    # P03 (novo e editar)
  clientes/lista.html       # P05
  clientes/form.html        # P06
  alugueis/novo.html        # P07
  alugueis/historico.html   # P08
  alugueis/devolucao.html   # P09
```

- Item ativo do menu: passe `menu_ativo` no contexto (ou compare `request.resolver_match.url_name`) e use `class="nav-link {% if menu_ativo == 'equipamentos' %}active{% endif %}"` com `aria-current="page"`.
- Barra lateral responsiva: `<aside class="offcanvas-lg offcanvas-start">`, fixa a partir de `lg` (992px), gaveta abaixo disso, com botão `data-bs-toggle="offcanvas"` no cabeçalho.

### 5.3 Componentes → Bootstrap

| Componente | Bootstrap 5.3 |
|---|---|
| Button | `btn btn-primary`, `btn-outline-secondary`, `btn-outline-primary`, `btn-warning`, `btn-success`, `btn-danger`, `btn-sm` |
| FormField | `form-label`, `form-control`, `form-select`, `form-text`, `is-invalid` + `invalid-feedback`, `input-group` |
| Table | `card > table-responsive > table align-middle mb-0`; `text-end` nos valores |
| Alert | `alert alert-success\|danger\|warning\|info d-flex gap-2` |
| Modal / ActionPanel | `modal fade` + `modal-dialog modal-dialog-centered` |
| AppShell | `offcanvas-lg`, `nav flex-column`, navbar simples no topo |
| QuickCard | `row row-cols-1 row-cols-md-2 row-cols-xl-4 g-3` + `card h-100` com `stretched-link` |
| RentalSummary | `col-lg-4` com `card position-sticky` ao lado de `col-lg-8` |

### 5.4 Formulários com erros do Django

Include para todos os campos (`includes/_field.html`, uso: `{% include "includes/_field.html" with field=form.cpf %}`):

```django
<div class="mb-3">
  <label class="form-label" for="{{ field.id_for_label }}">{{ field.label }}{% if field.field.required %} <span class="text-danger">*</span>{% endif %}</label>
  {{ field }}
  {% if field.help_text %}<div class="form-text" id="{{ field.id_for_label }}-help">{{ field.help_text }}</div>{% endif %}
  {% for e in field.errors %}<div class="invalid-feedback d-block">{{ e }}</div>{% endfor %}
</div>
```

- No `forms.py`, adicione as classes nos widgets (`attrs={"class": "form-control"}`) e, no `__init__`, acrescente `is-invalid` e `aria-invalid="true"` aos campos com erro.
- Campo bloqueado (código com histórico, CPF após primeiro aluguel): `self.fields["codigo"].disabled = True`. O Django ignora o valor enviado e o template mostra a explicação em `help_text`.
- Datas: `forms.DateInput(attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d")` e `min` com a data de hoje no fuso America/Recife (`timezone.localdate()` com `TIME_ZONE = "America/Recife"`).

### 5.5 Listas, pesquisa e estado vazio

- Pesquisa de equipamentos: `<form method="get">` com `<input name="q">`; a view filtra por `Q(nome__icontains=q) | Q(codigo__icontains=q)`. Clientes usam o mesmo padrão com `q` por nome ou CPF (RF009). O histórico usa `<select name="situacao">` (RF010).
- Vazio: `{% for e in equipamentos %}…{% empty %}{% include "includes/_empty_state.html" %}{% endfor %}`. Diferencie "nenhum cadastrado" de "nenhum resultado para q".
- Disponibilidade e situação do aluguel chegam prontas da view/model (`@property`); o template só escolhe a classe do badge.
- Mobile: o mais simples é `table-responsive`. Para cartões, adicione `data-label="Código"` em cada `<td>` e use o CSS de 5.7.

### 5.6 JavaScript simples (opcional)

Em `static/js/equipafacil.js`, sem frameworks:

- **Máscaras:** CPF (`000.000.000-00`) e telefone (`(81) 99999-9999`) no evento `input`. O backend continua validando e salvando só dígitos.
- **Prévia do aluguel (P07):** ao mudar equipamento ou datas, `dias = (devolucao - retirada)/86400000 + 1` e `total = dias * diaria`. A diária de cada opção vai em `<option value="3" data-diaria="80.00">`. Mostrar "—" quando incompleto. A view recalcula tudo ao salvar.
- **Confirmação de exclusão:** habilitar o botão Excluir só quando o código digitado confere (ou modal simples).
- **Atraso na devolução (P09):** ao mudar a data, comparar com a prevista e mostrar alerta de atraso.
- **Botão Salvar:** ao enviar, `disabled` + spinner (`spinner-border spinner-border-sm`) para evitar duplo envio.

### 5.7 CSS opcional para tabela em cartões

```css
@media (max-width:767.98px){
  .table-stack thead{display:none}
  .table-stack tr{display:block;padding:12px 16px;border-bottom:1px solid var(--bs-border-color)}
  .table-stack td{display:flex;justify-content:space-between;gap:12px;border:0;padding:3px 0}
  .table-stack td::before{content:attr(data-label);color:var(--bs-secondary-color);font-size:.8rem}
}
```

### 5.8 Checklist de fidelidade

- [ ] Um só `btn-primary` por tela, no lugar previsto.
- [ ] Badges com texto em todas as situações.
- [ ] Motivo visível em toda ação ou campo bloqueado.
- [ ] Erro por campo + alerta-resumo; foco no primeiro erro.
- [ ] Mensagens via `django.contrib.messages` após cada POST (Post/Redirect/Get).
- [ ] Testado em 390px de largura sem rolagem horizontal da página.
- [ ] Navegação completa só com teclado.

---

## 6. Limitações e decisões provisórias

### O que cada coisa é

| Categoria | O que entra aqui |
|---|---|
| Protótipo funcional demonstrativo | Login, navegação, pesquisa, cadastros, ações de equipamento, aluguel e devolução funcionam só em memória no navegador. Recarregar volta aos dados iniciais. Senha de demonstração fixa. Nada é enviado a servidor |
| Regra de negócio aprovada (RF001–RF010, RN001–RN004, I1–I5, D10–D16) | Disponibilidade = ativo e sem aluguel aberto · retirada a partir de hoje (Recife) · devolução prevista ≥ retirada · diárias inclusivas · diária contratada congelada no aluguel · sem cancelamento de aluguel · devolução entre a retirada e hoje, uma única vez · excluir só sem histórico e sem aluguel aberto · inativar/reativar sem aluguel aberto · código bloqueado com histórico · CPF bloqueado após o primeiro aluguel · sem pesquisa e sem exclusão de clientes (D14) |
| Proposta visual (pode mudar sem afetar o backend) | Paleta, tipografia IBM Plex, ícones, layout com barra lateral, textos de mensagens, tabela em cartões no mobile, confirmação de exclusão digitando o código, chip Pxx no cabeçalho, tema escuro, atalhos com contagem na página inicial |
| Integração real ainda não implementada | Autenticação Django, persistência PostgreSQL, validação no servidor, transação/bloqueio na criação do aluguel (corrida de disponibilidade), fuso America/Recife no servidor, `django.contrib.messages`, proteção CSRF |

### Decisões de UX provisórias (para validar)

1. P04 como modal a partir do botão "Ações" da listagem, em vez de página. As três ações sempre aparecem; as bloqueadas mostram o motivo.
2. Confirmação de exclusão exige digitar o código do equipamento. Uma confirmação simples (Cancelar / Excluir) também atende.
3. Nome completo exige ao menos nome e sobrenome. Se o RF não pedir isso, basta "obrigatório".
4. Telefone aceita fixo (10 dígitos) ou celular (11 dígitos), sempre com DDD.
5. Diária aceita vírgula ou ponto e até duas casas; "80" vira R$ 80,00.
6. Histórico ordena aluguéis em aberto primeiro, depois por retirada mais recente. Contadores por situação na barra superior são informativos.
7. Registrar devolução fica em destaque (`btn-primary`) quando o aluguel está Atrasado.
8. Lista de clientes em ordem alfabética.
9. Página inicial mostra contagens simples (equipamentos disponíveis, aluguéis em aberto) nos atalhos. Pode ser removido sem impacto.
10. Botões "Simular lista vazia" existem só no protótipo. Não fazem parte do sistema.

### Fora do escopo (não desenhado de propósito)

Dashboard financeiro, pagamentos, multas, reservas, cancelamento de aluguel, edição de aluguel registrado, pesquisa e exclusão de clientes, perfis e permissões, recuperação de senha, cadastro público, API REST e integrações externas.

---

*Fonte: PDF "EquipaFácil — Design System" (31 páginas), artifact EquipaFacil, última alteração 2026-11-02.*
