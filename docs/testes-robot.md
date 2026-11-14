# Testes automatizados com Robot Framework

Automação de interface dos cenários CT01–CT20 (Documento de Casos de Teste v1.4),
com Robot Framework e a biblioteca Browser, na estrutura exigida pela disciplina
de Qualidade de Software.

Os testes rodam **somente em ambiente local e isolado**: um servidor do Django em
`127.0.0.1` com um banco SQLite descartável. Render, Neon e o `db.sqlite3` de
desenvolvimento não são usados.

## Estrutura

```
tests/
├── Pages/                  um arquivo por tela, só *** Variables *** com XPaths
├── Keywords/               um _Steps.robot por tela, com as ações reutilizáveis
├── Cenario16.robot         um arquivo por caso de teste (CenarioNN.robot)
scripts/robot/
├── executar.py             sobe o servidor isolado e roda o Robot
├── massa.py                zera o banco isolado e cria a massa de um cenário
├── massas/ctNN.py          massa fictícia de cada cenário
└── settings_robot.py       configuração do Django só para a automação
resultados-robot/           relatórios e banco isolado (fora do Git)
```

Regras da disciplina:

- `Pages` contém apenas variáveis com seletores XPath. Nenhuma keyword.
- `Keywords` contém as ações e usa as variáveis das `Pages`.
- Os cenários não têm seletores: chamam somente keywords.
- Nenhum XPath é repetido. Se um elemento mudar, a correção é feita em um só lugar.

## Preparar o ambiente (uma vez)

Requisitos: Python 3.13, Node.js 20 ou mais recente e o ambiente virtual do projeto.

```
python -m pip install --requirement requirements-robot.txt
rfbrowser init chromium
```

O segundo comando baixa o navegador usado pela automação e pode demorar alguns minutos.

## Executar

Sempre pelo script, com o ambiente virtual ativo e a partir da raiz do projeto:

```
python scripts/robot/executar.py tests/Cenario16.robot     # um cenário
python scripts/robot/executar.py                           # a suíte inteira
python scripts/robot/executar.py --visivel tests/Cenario16.robot   # com o navegador na tela
```

Opções do Robot podem ser repassadas, por exemplo `--include Smoke`.

O script:

1. cria (ou atualiza) o banco `resultados-robot/robot.sqlite3`;
2. gera usuário e senha fictícios só para aquela execução;
3. sobe o servidor em `http://127.0.0.1:8765` (use `--porta` se estiver ocupada);
4. roda o Robot e encerra o servidor.

Não rode `robot` diretamente: sem as variáveis do script, os cenários param na
verificação de ambiente. Não rode duas execuções ao mesmo tempo, porque elas
dividiriam o mesmo banco.

## Relatórios

Ficam em `resultados-robot/`:

| Arquivo | Para que serve |
|---|---|
| `report.html` | Resumo: total de testes, aprovados, reprovados e estatísticas por tag. Abra primeiro. |
| `log.html` | Passo a passo de cada keyword, com mensagens de erro e a captura de tela tirada na falha. |
| `output.xml` | Resultado bruto, usado para gerar os outros dois e por ferramentas de CI. |
| `servidor.log` | Saída do servidor do Django durante a execução. |

Verde em `report.html` significa que todos os testes passaram. Em caso de falha,
abra o `log.html`, expanda o teste em vermelho e veja a keyword que falhou.

## Como adicionar o seu cenário

Exemplo para o CT03:

1. **Massa:** crie `scripts/robot/massas/ct03.py` com a função `preparar()`.
   Use as fábricas de `config/tests/fabricas.py` e só dados fictícios do
   documento de casos de teste. O banco chega vazio, apenas com o usuário de teste.
2. **Page:** se a tela ainda não tiver arquivo, crie `tests/Pages/<Tela>_Page.robot`
   só com `*** Variables ***`. Dê às variáveis o prefixo da tela
   (`EQUIPAMENTOS_...`, `CLIENTES_...`), porque elas são globais.
3. **Keywords:** crie ou complete `tests/Keywords/<Tela>_Steps.robot`.
4. **Cenário:** crie `tests/Cenario03.robot` no modelo do `Cenario16.robot`:
   `Test Setup    Iniciar Cenario    ct03` e `Test Teardown    Encerrar Cenario`.
5. Rode `python scripts/robot/executar.py tests/Cenario03.robot`.

Já existem e podem ser reutilizados: `Common_Steps.robot` (ambiente, massa e
navegador), `Login_Steps.robot` (`Entrar Como Funcionario`), `Home_Steps.robot`
(menu) e `Historico_Steps.robot`.

## Como trabalhar sem conflitos

- Cada integrante tem os próprios `CenarioNN.robot` e `massas/ctNN.py`: esses
  arquivos nunca conflitam.
- Cada tela tem **um responsável** pelos arquivos `_Page.robot` e `_Steps.robot`.
  Quem precisar de um seletor ou keyword de outra tela pede ao responsável ou
  abre um PR pequeno só com esse acréscimo.
- Antes de criar um XPath, procure nas `Pages` se ele já existe.
- Acrescente linhas novas no fim das seções; não reordene nem renomeie o que
  outros já usam.
- Não altere `Common_Steps.robot`, `executar.py`, `massa.py` nem
  `settings_robot.py` sem combinar com a equipe.
- Uma branch por integrante, a partir da branch da infraestrutura, com PRs pequenos.

## Segurança

- Nenhuma credencial fica no repositório: usuário e senha são gerados a cada execução.
- `Exigir Ambiente Local` recusa qualquer endereço diferente de `127.0.0.1` ou `localhost`.
- `massa.py` recusa apagar dados se o banco configurado não for o banco isolado.
- A automação é um teste técnico; não substitui o registro das execuções manuais.
