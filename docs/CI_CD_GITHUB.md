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

No **Portainer**, no stack do **Shepherd**, defina (arquivo `deploy/shepherd.env.example`):

```env
DOCKERHUB_USER=nivspa
DOCKERHUB_TOKEN=seu_token_do_docker_hub
```

Depois **Update the stack**. Não commite o token no Git.

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

## 8. Onde clicar no Portainer (passo a passo)

O guia “atualizar na mão” pode ser feito **sem terminal**, só na interface.

### A) Atualizar o SIGEPA (imagem nova)

1. Menu esquerdo → **Services** (Serviços).  
   *Não* use Containers — no Swarm o SIGEPA é um **serviço**.
2. Clique em **`sigepa_sigepa`** (nome exato pode variar; procure o do stack `sigepa`).
3. Botão **Update the service** (Atualizar serviço).
4. **Image:** `nivspa/sigepa:latest`
5. Ative **Pull latest image version**.
6. Se pedir registry: antes cadastre em **Registries** → Add → Docker Hub → usuário `nivspa` + **token** como senha.
7. Confirme **Update** — aguarde o serviço ficar verde de novo.

### B) Configurar o Shepherd (token Docker Hub)

1. Menu **Stacks** → stack do Shepherd.
2. **Editor** ou aba de variáveis de ambiente.
3. Adicione `DOCKERHUB_USER=nivspa` e `DOCKERHUB_TOKEN=<token>`.
4. **Update the stack**.

### C) Terminal (só se A não funcionar)

Use o console do **nó/host** (manager), **não** o console do container do site:

**Hosts** → nó manager → **>_ Console** → aí sim os comandos `docker login`, `docker pull`, `docker service update`.

---

## 9. Problemas comuns

| Sintoma | O que verificar |
|---------|------------------|
| `toomanyrequests` no log do Shepherd | Shepherd sem login no Hub → passo **B** acima |
| `Image does not exist` | GitHub Actions falhou ou pull bloqueado → **Registries** + **Services → Update** |
| Actions falhou no login | Secrets `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` no GitHub |
| Actions OK, site igual | Volume `static_data` antigo? **Volumes** → remover `static_data` |
| JS antigo no navegador | Ctrl+F5; arquivo JS deve ter hash no nome (F12 → Rede) |

---

## Arquivos relacionados

- Workflow: `.github/workflows/docker-publish.yml`
- Imagem: `nivspa/sigepa:latest` (`docker-compose.yml`)
- Shepherd: `deploy/shepherd-stack.yml`
- Estáticos com hash: `config/settings/prod.py` (`CompressedManifestStaticFilesStorage`)
