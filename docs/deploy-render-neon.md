# Hospedagem no Render com PostgreSQL no Neon (preparação)

> **Situação em 02/11/2026: preparação local, nada implantado.** O código está pronto para um Web Service no Render e um banco no Neon, mas nenhum serviço foi criado, nenhuma variável foi configurada em painel e nenhuma migration rodou fora do banco de testes local. Criar serviços, implantar e rodar migrations exigem autorização explícita de Rickelme.

## Arquitetura

```text
Navegador ──HTTPS──> Proxy do Render ──HTTP + X-Forwarded-Proto──> Gunicorn ──> Django
                                                                                ├── templates (frontend)
                                                                                ├── /static/ servido pelo WhiteNoise
                                                                                ├── /healthz/ (sem banco)
                                                                                └── PostgreSQL no Neon (DATABASE_URL, TLS)
```

- **Um único Web Service** no Render serve backend e frontend: as páginas são Django Templates e os arquivos estáticos (CSS, JS, Bootstrap local) saem do mesmo processo, pelo WhiteNoise. Não há serviço separado de frontend.
- **Banco PostgreSQL no Neon**, acessado por `DATABASE_URL` com TLS obrigatório.
- **Gunicorn** executa o Django; o build roda `collectstatic`; o health check usa `/healthz/`.

## Conexão local × hospedada

| Item | Local (desenvolvimento e testes) | Hospedado (Render + Neon) |
|------|----------------------------------|---------------------------|
| Configuração | Variáveis `DB_*` (`DB_HOST=127.0.0.1`) | `DATABASE_URL` |
| Senha | `pgpass.conf` do perfil do Windows | Só no painel do Render, dentro da `DATABASE_URL` |
| TLS | `sslmode=prefer` (servidor local) | `sslmode=require` obrigatório |
| `DJANGO_DEBUG` | `True` | `False` (ou ausente) |
| Testes | Só aqui, com `--keepdb` ([`postgresql-local.md`](postgresql-local.md)) | Nunca |

**Precedência:** quando `DATABASE_URL` está definida, ela vale e as variáveis `DB_*` são ignoradas. `DATABASE_URL` junto com `DB_ENGINE=sqlite` é recusado. Com `DJANGO_DEBUG=False`, qualquer conexão PostgreSQL sem `sslmode` `require`, `verify-ca` ou `verify-full` é recusada na inicialização. `manage.py test` recusa banco que não esteja em `127.0.0.1`, `localhost` ou `::1`; para testar, a `DATABASE_URL` não pode estar definida na sessão.

## Variáveis de ambiente no Render

| Variável | Valor | Observação |
|----------|-------|------------|
| `DJANGO_SECRET_KEY` | Chave aleatória com 50 caracteres ou mais | Gerada com `python -c "import secrets; print(secrets.token_urlsafe(50))"`; só no painel. Chave fraca impede a inicialização |
| `DJANGO_DEBUG` | `False` | Também é o padrão quando ausente |
| `DATABASE_URL` | String de conexão **direta** do Neon | Formato `postgresql://<usuario>:<senha>@<host>/<banco>?sslmode=require&channel_binding=require`. Senha codificada para URL. Só no painel |
| `DJANGO_SECURE_PROXY_SSL_HEADER` | `True` | O Render termina o HTTPS no proxy; sem isso, o redirecionamento para HTTPS entra em laço |
| `RENDER_EXTERNAL_HOSTNAME` | Definida pelo próprio Render | Entra em `ALLOWED_HOSTS` automaticamente |
| `DJANGO_ALLOWED_HOSTS` | Vazio, ou o domínio próprio, se houver | Hosts além do `onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Vazio | Só se houver formulário vindo de outra origem |
| `DJANGO_SECURE_HSTS_SECONDS` | `0` no início | Ligar só depois de confirmar todo o site em HTTPS no ambiente real |
| `DB_CONN_MAX_AGE` | `0` no início | Conexão nova por requisição. Para reuso, no máximo `300`: o Neon fecha conexões ociosas após 5 minutos |
| `WEB_CONCURRENCY` | Não definir no início | Número de workers do Gunicorn; padrão 1 |

A versão do Python vem de `.python-version` (`3.13.15`). Não defina `PYTHON_VERSION` no painel: ela tem precedência sobre o arquivo. O padrão do Render para serviços novos é Python 3.14, por isso a fixação é necessária.

**Conexão direta do Neon:** use o host sem `-pooler`. A conexão com pool (PgBouncer em modo transação) exige ajustes adicionais no Django, como desligar cursores no servidor, e fica para uma decisão futura.

## Comandos do Web Service

| Campo no Render | Valor |
|-----------------|-------|
| Build Command | `bash scripts/render-build.sh` |
| Start Command | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| Health Check Path | `/healthz/` |

O `scripts/render-build.sh` instala `requirements.txt`, roda `pip check`, `manage.py check --deploy` e `collectstatic`. Ele **não** acessa o banco e **não** roda migrations. O `check --deploy` mostra o aviso `security.W004` enquanto o HSTS estiver desligado; aviso não interrompe o build.

**Gunicorn:** começa com 1 worker (padrão). Aumente com `WEB_CONCURRENCY` só depois de medir a memória usada pelo processo no plano contratado; cada worker é uma cópia do Django em memória. O Gunicorn não roda no Windows (exige o módulo `fcntl`); localmente, a aplicação WSGI foi validada com o servidor `wsgiref` da biblioteca padrão. **O Gunicorn em si só será exercitado no primeiro ambiente Linux.**

## Arquivos estáticos

- O `collectstatic` copia `static/` e os estáticos do Django Admin para `staticfiles/` (fora do Git) e gera nomes com hash e versões `.gz`.
- O WhiteNoise serve `/static/` com cache longo (`max-age=315360000, public, immutable`) para os arquivos com hash.
- No desenvolvimento e nos testes (`DJANGO_DEBUG=True`), o armazenamento é simples e dispensa o `collectstatic`.
- **Para o frontend:** coloque os arquivos em `static/` e use sempre `{% static %}` nos templates. Toda referência `url(...)` em CSS e todo comentário `sourceMappingURL` precisam apontar para arquivos existentes, senão o `collectstatic` falha. No Bootstrap 5.3 local, copie também os arquivos `.map` ou use versões sem esse comentário.

## Health check

`GET /healthz/` (e `HEAD`) responde `200` com o corpo `ok`:

- é público e responde antes da sessão e da autenticação, então nunca consulta o PostgreSQL nem acorda o Neon, mesmo com cookie de sessão;
- não entra em cache, não expõe configuração e responde também por HTTP, sem redirecionar;
- responde para qualquer `Host`, porque vem antes da validação de `ALLOWED_HOSTS`; as demais páginas continuam validando o host.

O Render considera saudável qualquer resposta `2xx` ou `3xx` em até 5 segundos e usa o subdomínio `onrender.com` como `Host`.

## Migrations: estratégia futura (decisão pendente)

O plano Free do Render **não tem** comando pré-deploy, shell nem jobs avulsos. Opções:

1. **Recomendada: manual, a partir da máquina de Rickelme**, com a conexão direta do Neon definida só na sessão do PowerShell:

   ```powershell
   $env:DJANGO_ENV_FILE = ""
   $env:DJANGO_SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(50))")
   $url = Read-Host "DATABASE_URL do Neon (conexão direta)" -AsSecureString
   $env:DATABASE_URL = [Net.NetworkCredential]::new("", $url).Password
   python manage.py migrate --plan
   python manage.py migrate
   Remove-Item Env:DATABASE_URL; Remove-Variable url
   ```

   O `-AsSecureString` esconde a URL na digitação e ela não vai para o histórico do PowerShell. `DJANGO_ENV_FILE=""` ignora o `.env` local; sem `DJANGO_DEBUG`, vale `False` e o TLS é obrigatório. Rode antes um backup (abaixo).
2. **No build do Render:** roda a cada deploy e pode deixar o banco migrado com o código antigo ainda no ar se o deploy falhar depois. Só com decisão específica.
3. **Comando pré-deploy:** exige plano pago.

**Compatibilidade de schema:** o código novo não pode depender de colunas que ainda não existem, e o código antigo não pode quebrar com o schema novo. Prefira migrations em duas etapas: primeiro adicionar (colunas anuláveis ou com padrão), depois remover em um deploy seguinte. Com uma instância só e hibernação, uma indisponibilidade curta durante a troca é aceitável no projeto acadêmico, mas deve ser combinada.

## Backup e recuperação

- **Antes de cada migration:** crie no console do Neon um *branch* a partir do estado atual (cópia instantânea) ou gere um dump com o `pg_dump` 18 instalado localmente (`C:\Program Files\PostgreSQL\18\bin\pg_dump.exe`), gravado fora do repositório.
- **Recuperação do banco:** restaurar o branch de segurança, ou o histórico de restauração do Neon dentro da janela do plano (confira o limite no console), ou `pg_restore` do dump.
- **Recuperação do código:** o Render permite voltar a um deploy anterior. Se a migration já tiver mudado o schema, combine o rollback do código com a restauração do banco.

## Administração

- Não há cadastro público. O primeiro superusuário é criado da máquina de Rickelme, com a `DATABASE_URL` definida só na sessão (como acima), por `python manage.py createsuperuser`: a senha é pedida de forma interativa e não aparece no comando.
- As contas de funcionários são criadas por esse administrador no Django Admin (`/admin/`), que só aceita usuários da equipe; gerir contas exige permissão explícita (D15).
- Nenhuma senha vai para código, logs, variáveis versionadas ou comandos salvos. Não use `DJANGO_SUPERUSER_PASSWORD` nem `createsuperuser --noinput` com senha em variável.

## Restrições do Render Free

- O serviço hiberna após 15 minutos sem tráfego e leva cerca de 1 minuto para voltar.
- 750 horas de instância por mês, somadas entre os serviços Free do workspace; ao esgotar, os serviços ficam suspensos até o mês seguinte.
- Sem shell, SSH, jobs avulsos, comando pré-deploy ou disco persistente (arquivos gravados em disco se perdem a cada reinício).
- Uma única instância; o Render pode reiniciar o serviço a qualquer momento.
- No Neon, o banco também pode hibernar; a primeira requisição depois de um período parado é mais lenta.

## O que falta para o primeiro deploy (cada item exige autorização)

1. Criar o projeto e o banco no Neon e obter a conexão direta.
2. Criar o Web Service no Render a partir da `main` integrada, com os comandos acima e as variáveis no painel.
3. Validar `/healthz/`, o redirecionamento para HTTPS, o login e os estáticos no endereço `onrender.com`.
4. Decidir e executar a estratégia de migrations, com backup antes.
5. Criar o superusuário e as contas de funcionários.
6. Avaliar e ligar o HSTS.

Não há `render.yaml` no repositório: a configuração automática de serviços e banco depende de autorização específica.
