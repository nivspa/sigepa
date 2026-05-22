# Deploy automático: webhook Portainer + runner interno

## Visão rápida

1. **GitHub (nuvem)** publica `nivspa/sigepa:producao` no Docker Hub.
2. **Runner self-hosted** (VM na rede SESPA) executa o job `deploy`.
3. **Webhook** do Portainer reinicia o serviço `sigepa_sigepa` no Swarm.

---

## Passo 1 — Portainer: ligar o webhook do serviço

1. Portainer → **Services** → `sigepa_sigepa`
2. Ative **Service webhook** (toggle ON)
3. Copie a **URL do webhook** (guarde num gestor de senhas)
4. Em **Update the service**, use a imagem **`nivspa/sigepa:producao`** (ou `:latest`)
   - Evite fixar `@sha256:...` se quiser que cada deploy puxe a imagem nova.

---

## Passo 2 — GitHub: secret do webhook

Repositório **nivspa/sigepa** → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Nome | Valor |
|------|--------|
| `PORTAINER_WEBHOOK_URL` | URL copiada do Portainer (passo 1) |

Mantenha também: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.

---

## Passo 3 — Runner self-hosted (rede interna)

Precisa de uma **VM Linux** na mesma rede que alcança `portainer.saude.pa.gov.br` (peça à TI se necessário).

No GitHub: **Settings** → **Actions** → **Runners** → **New self-hosted runner**

1. Escolha **Linux** e **x64**
2. Na VM, execute os comandos que o GitHub mostra, por exemplo:

```bash
mkdir -p ~/actions-runner-sigepa && cd ~/actions-runner-sigepa
curl -o actions-runner-linux-x64.tar.gz -L https://github.com/actions/runner/releases/download/v2.334.0/actions-runner-linux-x64-2.334.0.tar.gz
tar xzf ./actions-runner-linux-x64.tar.gz
./config.sh --url https://github.com/nivspa/sigepa --token <TOKEN_DO_GITHUB> --labels sigepa
sudo ./svc.sh install
sudo ./svc.sh start
```

3. Confirme em **Settings → Actions → Runners** que aparece **Idle** com label `sigepa`.

Teste na VM:

```bash
curl -I https://portainer.saude.pa.gov.br
```

Se falhar aqui, o runner também não conseguirá o webhook.

---

## Passo 4 — Publicar o workflow

Commit e push de `.github/workflows/deploy.yml` na branch `main`.

---

## Verificar

1. **Actions** → workflow **Build and Deploy**
2. Job `build` → verde (Docker Hub)
3. Job `deploy` → verde (webhook)
4. Portainer → serviço `sigepa_sigepa` → **Last updated** recente

---

## Problemas comuns

| Sintoma | Solução |
|---------|---------|
| Job `deploy` fica **Queued** | Runner offline ou sem label `sigepa` |
| `Could not resolve host` no runner | VM fora da rede interna / DNS |
| Build ok, app antiga no ar | Imagem fixada em `@sha256`; usar `:producao` e webhook ON |
| Webhook 404 | URL errada ou webhook desligado no Portainer |
