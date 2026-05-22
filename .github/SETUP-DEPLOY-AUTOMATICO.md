# Deploy automático SEM SSH e SEM runner

## Como funciona

```text
git push → GitHub Actions → Docker Hub (nivspa/sigepa:producao)
                                    ↓
              Shepherd (no Swarm) verifica a cada 5 min e atualiza sigepa_sigepa
```

Tudo roda **dentro** do cluster. Você só configura uma vez no Portainer.

---

## Passo 1 — Imagem do serviço SIGEPA

Portainer → **PRD** → **Services** → `sigepa_sigepa` → **Update the service**

- Imagem: `nivspa/sigepa:producao` (sem `@sha256:...`)
- Apply

---

## Passo 2 — Subir o Shepherd (uma vez)

1. Portainer → **PRD** → **Stacks** → **Add stack**
2. Nome: `shepherd-sigepa`
3. Cole o conteúdo de `deploy/shepherd-stack.yml`
4. **Deploy the stack**

`FILTER_SERVICES` tem que ser formato Docker, ex.: `name=sigepa_sigepa` (não só `sigepa`).

---

## Passo 3 — GitHub

Secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`

Workflow: `.github/workflows/deploy.yml` (só build)

---

## Uso do dia a dia

1. `git push origin main`
2. Aguarde o Actions ficar verde (~2 min)
3. Em até **5 minutos** o Shepherd atualiza produção sozinho

---

## Se não atualizar

- Serviço ainda com imagem fixada em `@sha256`
- Stack shepherd não está no PRD ou não está running
- Imagem privada sem `REGISTRY_USER` / `REGISTRY_PASSWORD` no Shepherd
