# IBM Plex Sans e IBM Plex Mono (arquivos locais)

Tipografia do design system (`equipafacil-design-system.md`, seção 2). Mesmo
princípio do Bootstrap em `static/vendor/bootstrap/`: arquivo local, sem CDN
— o guia de integração proíbe script ou folha de estilo externa sem acordo.

| Arquivo | Peso | Uso |
|---------|------|-----|
| `ibm-plex-sans-400.woff2` | 400 | Texto corrido, valores de campo |
| `ibm-plex-sans-500.woff2` | 500 | Rótulos de formulário e botões |
| `ibm-plex-sans-600.woff2` | 600 | Títulos |
| `ibm-plex-sans-700.woff2` | 700 | Só o valor total do aluguel |
| `ibm-plex-mono-400.woff2` | 400 | Código do equipamento, CPF, valores tabulares |
| `ibm-plex-mono-500.woff2` | 500 | (reservado; não usado nesta etapa) |

| Item | Valor |
|------|-------|
| Fonte | Google Fonts (`fonts.googleapis.com/css2`), subset **latin** |
| Versões | IBM Plex Sans v23, IBM Plex Mono v20 |
| Licença | SIL Open Font License 1.1 (IBM) |
| Tamanho total | ~140 KB (6 arquivos) |

## Por que só o subset "latin"

O subset "latin" do Google Fonts cobre `U+0000–00FF` (inclui o Latin-1
Supplement: ã, õ, ç, á, é, í, ó, ú, â, ê, à, ü), que é o necessário para
português do Brasil. Os demais subsets que o Google oferece por padrão
(`cyrillic`, `cyrillic-ext`, `greek`, `vietnamese`, `latin-ext`) não foram
baixados, para manter o pacote pequeno.

## Como foram obtidos

Para cada peso, uma requisição separada a
`https://fonts.googleapis.com/css2?family=<fonte>:wght@<peso>&display=swap`
com um `User-Agent` de navegador moderno (o Google decide o formato do
arquivo pelo `User-Agent`; sem um moderno, devolve TTF em vez de WOFF2).
Do CSS devolvido, extraído só o bloco `/* latin */` de cada peso.

## SHA-256 dos arquivos versionados

| Arquivo | SHA-256 |
|---------|---------|
| `ibm-plex-sans-400.woff2` | `3b646991d30055a93a4ecc499713d4347953a74a947ecab435ab72070cbdab0e`[^1] |
| `ibm-plex-sans-500.woff2` | `0717336fb31fcdcde4b8deb3675bb4a0f7f6d484864afcd6751ac29975962203`[^1] |
| `ibm-plex-sans-600.woff2` | `8960851d691c054ed38e259bdcf1a6190d157b4203ed5bb32c632a863fb8ec2f`[^1] |
| `ibm-plex-sans-700.woff2` | `42e7b0c143c19df9d99fd896e76b48f846edf0902d200bc29796b34d12c33aa7`[^1] |
| `ibm-plex-mono-400.woff2` | `08949f728dc52d528e69b1667d15c89a5686a4ee9a296ff90983985f99c380f7`[^1] |
| `ibm-plex-mono-500.woff2` | `01d285447409c8a588692162439a038b8cbd7871309ee20267b0d2d91c6e8e22`[^1] |

[^1]: Os arquivos não foram modificados após o download (ao contrário do
`bootstrap.min.css`, nenhum precisou de edição).

Os `@font-face` ficam em `static/css/app.css`, com `font-display: swap` e,
como alternativa, a pilha `system-ui` (o texto aparece com a fonte do sistema
até a fonte própria carregar, e continua legível se ela falhar).
