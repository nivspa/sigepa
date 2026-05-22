# Deploy automático com GitHub Actions

Fluxo: **push na branch `main`** → GitHub builda a imagem → publica no Docker Hub → **Shepherd** puxa `nivspa/sigepa:latest` em produção.

Você não precisa rodar `docker build` na sua máquina no dia a dia.

---

## 1. Token do Docker Hub (uma vez)

1. Acesse https://hub.docker.com/ e entre na conta **nivspa** (ou a que publica `nivspa/sigepa`).
2. **Account Settings** → **Security** → **New Access Token**.
3. Nome: `github-actions-sigepa`.
4. Permissão: **Read, Write, Delete** (ou Read & Write).
5. Copie o token — ele só aparece uma vez.

---

## 2. Secrets no GitHub (uma vez)

1. Abra o repositório: https://github.com/nivspa/sigepa
2. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
3. Crie dois secrets:

| Nome | Valor |
|------|--------|
| `DOCKERHUB_USERNAME` | `nivspa` |
| `DOCKERHUB_TOKEN` | o token copiado do Docker Hub |

---

## 3. Subir o workflow

Commit e push destes arquivos na `main`:

- `.github/workflows/docker-publish.yml`

No GitHub: aba **Actions** → workflow **Publicar imagem Docker** → deve ficar verde após o push.

---

## 4. Produção (Shepherd + Portainer)

O arquivo `deploy/shepherd-stack.yml` já está preparado para:

- Verificar a cada **5 minutos** se há imagem nova
- Atualizar o serviço `sigepa_sigepa` (nome no Swarm)

Confirme no Portainer que o serviço usa a imagem:

```text
nivspa/sigepa:latest
```

Se a imagem for **privada** no Docker Hub, descomente no `shepherd-stack.yml`:

```yaml
REGISTRY_USER: nivspa
REGISTRY_PASSWORD: <token ou senha>
```

---

## 5. Ajuste importante — volume de estáticos (faça UMA vez)

Antes, o `docker-compose` montava um volume em `/app/staticfiles`, **sobrescrevendo** o JavaScript novo da imagem com arquivos velhos.

Isso foi removido. Na próxima atualização em produção:

1. Atualize o stack/compose no servidor (sem volume `static_data`).
2. Se existir volume órfão `static_data`, pode removê-lo no Portainer (**Volumes** → remover) após o deploy estável.

---

## 6. Seu fluxo de trabalho daqui pra frente

```text
1. Desenvolve local (runserver)
2. git add / commit / git push origin main
3. Aguarda ~3–8 min (Actions + Shepherd)
4. Ctrl+F5 no navegador em produção
```

Conferir deploy:

- **GitHub** → Actions → último run verde.
- **Docker Hub** → `nivspa/sigepa` → tag `latest` com data recente.
- **Site** → F12 → Rede → `ocorrencia-form.*.js` com hash no nome.

---

## 7. Publicar manualmente (opcional)

No GitHub: **Actions** → **Publicar imagem Docker** → **Run workflow**.

Útil se quiser republicar sem novo commit.

---

## 8. Problemas comuns

| Sintoma | O que verificar |
|---------|------------------|
| Actions falhou no login | Secrets `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` |
| Actions OK, site igual | Shepherd ativo? Serviço usa `nivspa/sigepa:latest`? |
| JS antigo | Volume `static_data` ainda montado? Remover e redeploy. |
| Shepherd não puxa | Imagem privada sem `REGISTRY_USER` no shepherd |

---

## Arquivos relacionados

- Workflow: `.github/workflows/docker-publish.yml`
- Imagem: `nivspa/sigepa:latest` (`docker-compose.yml`)
- Shepherd: `deploy/shepherd-stack.yml`
- Estáticos com hash: `config/settings/prod.py` (`CompressedManifestStaticFilesStorage`)
