# PostgreSQL local (DEV-02)

> **Validado em 02/11/2026:** a suíte completa da fundação passou no PostgreSQL 18.6 local, com 64 testes aprovados e nenhum pulado. Detalhes em [Resultado da validação](#resultado-da-validação). Restrições de dados e concorrência só serão testadas com os modelos de DEV-03.

## Configuração adotada

| Item | Valor |
|------|-------|
| Servidor | PostgreSQL 18.6 local, serviço `postgresql-x64-18`, em `127.0.0.1:5432` |
| Cliente `psql` | `C:\Program Files\PostgreSQL\18\bin\psql.exe` (fora do `PATH`) |
| Usuário | `equipafacil_dev`: `LOGIN`, sem `SUPERUSER`, `CREATEROLE`, `CREATEDB`, `REPLICATION` e `BYPASSRLS` |
| Banco de desenvolvimento | `equipafacil_dev`: UTF8, dono `equipafacil_dev`, sem acesso público; usado pelo `runserver` |
| Banco de testes | `test_equipafacil_dev`: UTF8, mesmo dono, sem acesso público; descartável, usado só por `manage.py test --keepdb` |
| Senha | Só no `pgpass.conf` do perfil do Windows; nunca no repositório, no `.env` ou em comandos |

O Django 5.2 exige PostgreSQL 14 ou superior e psycopg 3.1.8 ou superior; a combinação PostgreSQL 18.6 + psycopg 3.3.6 foi validada.

## Por que dois bancos e `--keepdb`

O `manage.py test` normalmente cria e apaga o banco `test_<DB_NAME>`, o que exige a permissão `CREATEDB`. Para o usuário da aplicação não ter esse privilégio, o administrador cria o banco de testes uma vez, e os testes rodam com `--keepdb`:

- o Django encontra o banco (`Using existing test database ... 'test_equipafacil_dev'`), aplica nele as migrations e o mantém no fim (`Preserving test database`);
- nenhum banco é criado, apagado ou renomeado;
- cada teste roda numa transação desfeita no fim, então não sobram dados.

> **Atenção: no PostgreSQL, rode os testes sempre com `--keepdb`.** Sem essa opção, o Django encontra o banco de testes já existente e pergunta se deve apagá-lo (com `--noinput`, apaga sem perguntar). Como o usuário é dono do banco, o `DROP DATABASE` funciona, mas a recriação falha por falta de `CREATEDB`, e o banco de testes se perde até o administrador recriá-lo.

## Criação (administrador, uma vez)

Feita por Rickelme em 02/11/2026. Os passos ficam registrados para reproduzir em outra máquina.

1. Em uma **janela separada do PowerShell**, conecte como superusuário; o `psql` pede a senha sem exibi-la:

   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h 127.0.0.1 -p 5432 -U postgres -d postgres
   ```

2. Confira que os nomes ainda não existem (as duas consultas devem voltar vazias):

   ```sql
   SELECT rolname FROM pg_roles WHERE rolname = 'equipafacil_dev';
   SELECT datname FROM pg_database WHERE datname IN ('equipafacil_dev', 'test_equipafacil_dev');
   ```

3. Crie usuário e bancos. O `CREATE` falha se o nome já existir e o `ON_ERROR_STOP` interrompe tudo, então nada é sobrescrito:

   ```sql
   \set ON_ERROR_STOP on
   CREATE ROLE equipafacil_dev WITH LOGIN NOSUPERUSER NOCREATEROLE NOCREATEDB NOREPLICATION NOBYPASSRLS;
   \password equipafacil_dev
   CREATE DATABASE equipafacil_dev WITH OWNER equipafacil_dev ENCODING 'UTF8' TEMPLATE template0;
   CREATE DATABASE test_equipafacil_dev WITH OWNER equipafacil_dev ENCODING 'UTF8' TEMPLATE template0;
   REVOKE CONNECT, TEMPORARY ON DATABASE equipafacil_dev FROM PUBLIC;
   REVOKE CONNECT, TEMPORARY ON DATABASE test_equipafacil_dev FROM PUBLIC;
   \q
   ```

   O `\password` pede a senha sem exibi-la e sem gravá-la no histórico do `psql`.

4. Guarde a senha no `pgpass.conf` do seu perfil:

   ```powershell
   New-Item -ItemType Directory -Force "$env:APPDATA\postgresql" | Out-Null
   notepad "$env:APPDATA\postgresql\pgpass.conf"
   ```

   Uma linha, salva em UTF-8 sem BOM: `127.0.0.1:5432:*:equipafacil_dev:<senha>`. O host precisa ser igual ao `DB_HOST` (`127.0.0.1`, não `localhost`). O `*` cobre os dois bancos e o `postgres`, que o Django consulta só para verificar se o banco de testes existe. Se a senha tiver `:` ou `\`, ponha uma `\` antes de cada um.

5. Teste o acesso sem senha no comando (o `-w` impede o `psql` de pedir senha):

   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h 127.0.0.1 -p 5432 -U equipafacil_dev -d test_equipafacil_dev -w -c "SELECT current_user, current_database();"
   ```

Não altere `pg_hba.conf` nem as configurações globais do servidor. Se o passo 5 falhar com "no pg_hba.conf entry", pare e avalie antes de mudar qualquer coisa.

## Configuração do Django

No `.env` (ou em variáveis da sessão do PowerShell):

```text
DJANGO_DEBUG=True
DB_ENGINE=postgresql
DB_NAME=equipafacil_dev
DB_USER=equipafacil_dev
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432
DB_SSLMODE=prefer
```

Com `DB_PASSWORD` vazio, o Django não envia senha e o libpq usa o `pgpass.conf`. `DB_SSLMODE=prefer` serve para o servidor local; serviços gerenciados como o Neon exigem `require`.

## Execução

```powershell
python manage.py check --database default
python manage.py makemigrations --check --dry-run
python manage.py test -v 2 --keepdb
```

Os dois primeiros comandos conectam ao banco de desenvolvimento só para leitura. Para garantir isso no próprio servidor, rode-os com a sessão em modo somente leitura e remova a variável antes dos testes:

```powershell
$env:PGOPTIONS = "-c default_transaction_read_only=on"
python manage.py check --database default
python manage.py makemigrations --check --dry-run
Remove-Item Env:PGOPTIONS
python manage.py test -v 2 --keepdb
```

Rode `python manage.py migrate` no `equipafacil_dev` só quando for usar o `runserver` com PostgreSQL. Nesta etapa ele cria apenas as tabelas nativas do Django.

## Resultado da validação

Execução de 02/11/2026, no commit `7e78668` da branch `feat/backend-dev02-foundation`:

| Item | Resultado |
|------|-----------|
| Versões | PostgreSQL 18.6, Django 5.2.18, psycopg 3.3.6, Python 3.13.15 |
| Bancos antes da suíte | Locais (`127.0.0.1:5432`), dono `equipafacil_dev`, UTF8, sem acesso público, vazios |
| `check --database default` | Sem problemas (sessão somente leitura) |
| `makemigrations --check --dry-run` | `No changes detected` (sessão somente leitura) |
| `test -v 2 --keepdb`, 1ª execução | 64 descobertos, **64 aprovados**, 0 falhas, **0 pulados**; 18 migrations nativas aplicadas no banco de testes |
| `test -v 2 --keepdb`, 2ª execução | 64 aprovados, 0 pulados; nenhuma migration nova (banco reaproveitado) |
| Testes de `config/tests/test_postgresql.py` | Executados e aprovados: versão mínima 14, conexão em UTC, codificação UTF8 |
| Banco de testes depois | 10 tabelas, 0 usuários, 0 sessões |
| Banco de desenvolvimento depois | Inalterado: 0 tabelas, 0 linhas inseridas, alteradas ou apagadas |
| Bancos `equipafacil` no servidor | Só `equipafacil_dev` e `test_equipafacil_dev`; nenhum criado ou apagado |
| SQLite, mesmo commit | 64 descobertos, 61 aprovados, 3 pulados (os de PostgreSQL) |

Não houve diferença de comportamento entre SQLite e PostgreSQL nos 61 testes comuns.

**Ainda não validado:** restrições de banco e concorrência (dependem dos modelos de DEV-03), `migrate` no banco de desenvolvimento e qualquer ambiente fora desta máquina (Neon, Render).

## Descartar (se necessário)

Operação destrutiva, só por decisão de Rickelme, conectado como `postgres`:

```sql
DROP DATABASE test_equipafacil_dev;
DROP DATABASE equipafacil_dev;
DROP ROLE equipafacil_dev;
```

Remova também a linha correspondente do `pgpass.conf`.
