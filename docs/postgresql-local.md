# PostgreSQL local — validação pendente (DEV-02)

> **Situação em 02/11/2026: nenhum teste foi executado em PostgreSQL.** A suíte passou apenas com o SQLite temporário. Este documento descreve como fazer a primeira execução com segurança. Até ela acontecer e ser registrada, o PostgreSQL **não** está validado.

## Ambiente encontrado

Consulta feita sem autenticar e sem alterar nada no servidor:

| Item | Situação |
|------|----------|
| Serviço | `postgresql-x64-18`, em execução, início automático |
| Versão | PostgreSQL 18.6 (`postgres --version`) |
| Disponibilidade | `pg_isready -h localhost -p 5432`: aceitando conexões |
| Cliente | `psql` 18.6 em `C:\Program Files\PostgreSQL\18\bin`, fora do `PATH` |
| Credenciais | Nenhuma conhecida pelo projeto; nenhuma tentativa de login foi feita |

O Django 5.2 exige PostgreSQL 14 ou superior e psycopg 3.1.8 ou superior; o projeto usa psycopg 3.3.6. A compatibilidade com o PostgreSQL 18 só fica confirmada depois da execução da suíte.

## Princípios

- Usuário e banco **exclusivos** do EquipaFácil. A aplicação nunca usa o superusuário `postgres`.
- Não alterar `pg_hba.conf`, configurações globais do servidor nem senhas existentes.
- A senha fica fora do repositório e do histórico do terminal; de preferência, também fora do `.env`.
- `manage.py test` cria e apaga um banco próprio, `test_<DB_NAME>`, em UTF8 a partir do `template0`. Ele não mexe no banco de desenvolvimento, mas o usuário precisa da permissão `CREATEDB`.

## 1. Criar usuário e banco (uma vez, por Rickelme)

Exige a senha do superusuário definida na instalação do PostgreSQL; o `psql` a pede de forma interativa.

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -U postgres -d postgres
```

No `psql`:

```sql
CREATE ROLE equipafacil_dev LOGIN CREATEDB;
\password equipafacil_dev
CREATE DATABASE equipafacil_dev OWNER equipafacil_dev ENCODING 'UTF8' TEMPLATE template0;
\q
```

O `\password` pede a senha sem exibi-la e sem gravá-la no histórico do `psql`.

## 2. Guardar a senha no `pgpass.conf`

O libpq lê a senha deste arquivo, fora do repositório:

```powershell
New-Item -ItemType Directory -Force "$env:APPDATA\postgresql" | Out-Null
notepad "$env:APPDATA\postgresql\pgpass.conf"
```

Conteúdo, em uma linha, salvo em UTF-8 sem BOM:

```text
localhost:5432:*:equipafacil_dev:<senha-definida-no-passo-1>
```

O `*` cobre o banco de desenvolvimento e o banco de testes. Com isso, `DB_PASSWORD` fica vazio no `.env`.

## 3. Configurar o `.env`

```text
DJANGO_DEBUG=True
DB_ENGINE=postgresql
DB_NAME=equipafacil_dev
DB_USER=equipafacil_dev
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=prefer
```

`DB_SSLMODE=prefer` serve para o servidor local; serviços gerenciados como o Neon exigem `require`.

## 4. Executar

```powershell
python manage.py check --database default
python manage.py test -v 2
```

Resultado esperado: todos os testes aprovados e **nenhum pulado**. Os três testes de `config/tests/test_postgresql.py` passam a rodar e conferem a versão mínima (14), a conexão em UTC e a codificação UTF8.

Para usar o `runserver` com PostgreSQL, rode `python manage.py migrate` no banco `equipafacil_dev`. Nesta etapa ele cria apenas as tabelas nativas do Django (autenticação, Admin, sessões).

## 5. Registrar o resultado

Anote a data, as versões (PostgreSQL, Django, psycopg) e o resultado da suíte no PR do DEV-02. Só então o PostgreSQL local pode ser considerado validado. Testes de restrições e de concorrência dependem dos modelos de DEV-03 e continuam pendentes.

## Descartar (se necessário)

Operação destrutiva, só por decisão de Rickelme, conectado como `postgres`:

```sql
DROP DATABASE equipafacil_dev;
DROP ROLE equipafacil_dev;
```

Remova também a linha correspondente do `pgpass.conf`.
