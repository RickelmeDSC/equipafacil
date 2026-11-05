# Bootstrap 5.3 (arquivo local)

Bootstrap servido como arquivo estático do próprio projeto, sem CDN, conforme a
seção 5.3 do `docs/guia-integracao-frontend-backend.md` e o checklist do DEV-07.

| Item | Valor |
|------|-------|
| Versão | 5.3.8 |
| Arquivo | `bootstrap.min.css` (somente o CSS) |
| Origem | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css` |
| SHA-256 (baixado) | `d85327d99c7a3ee1f9b5d0500d1370acea3ad2db39c163c2f51f232baedbdede` |
| SHA-256 (versionado) | `8f8173cb2d8f867274aeb0cb15328e60f490c7f272351e51a55f1dabb486e4ff` |
| Licença | MIT (Bootstrap Authors / Twitter, Inc.) |

## Duas observações sobre o arquivo

1. **A última linha foi removida.** O arquivo publicado pelo Bootstrap termina em
   `/*# sourceMappingURL=bootstrap.min.css.map */`. O `collectstatic` com
   `CompressedManifestStaticFilesStorage` (usado fora do desenvolvimento, e
   validado no job Gunicorn da CI) resolve essa referência e falharia, porque o
   `.map` não é versionado. Daí os dois SHA-256 acima: o do arquivo original,
   para conferir a origem, e o do arquivo que está no Git.
2. **Só o CSS.** O `bootstrap.bundle.min.js` não foi incluído porque nenhuma tela
   depende de JavaScript do Bootstrap: a navegação não usa menu colapsável e a
   confirmação de exclusão (P04) é um bloco `<details>`, não um modal. O guia
   exige que as páginas funcionem sem JavaScript. Se alguma tela futura precisar
   de componente com JavaScript (modal, dropdown, toast), o bundle da **mesma
   versão** deve ser baixado para esta pasta e registrado aqui.

Para atualizar a versão: baixe o novo arquivo, remova a última linha
(`sourceMappingURL`), atualize esta tabela e rode a suíte de testes.
