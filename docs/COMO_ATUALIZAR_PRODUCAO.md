# Como atualizar o SIGEPA em produção (sem JavaScript antigo)

## Deploy automático (recomendado)

Configure uma vez o **[CI/CD com GitHub Actions](CI_CD_GITHUB.md)**. Depois disso:

**`git push origin main`** → build e publicação automáticos → Shepherd atualiza produção.

---

## Deploy manual (alternativa)

Em produção o sistema usa **imagem Docker**. O JavaScript e o CSS entram na imagem no momento do **build**, não quando você só envia código para o servidor.

## Por que o JS ficou velho?

1. A imagem em produção foi construída **antes** das alterações em `static/js/`.
2. O navegador (ou proxy) guardou cópia antiga dos arquivos.
3. Só atualizar arquivos no Git **sem** gerar imagem nova não troca o que está dentro do container.

## O que mudamos no projeto (solução definitiva)

A partir de agora, em **produção**, cada `collectstatic` gera nomes com **hash**, por exemplo:

- `ocorrencia-form.a1b2c3d4.js` em vez de só `ocorrencia-form.js`

Cada deploy novo gera hash novo → o navegador baixa o arquivo certo, sem depender de `?v=26` manual.

## Passo a passo para publicar (obrigatório)

### 1. Commit e push do código atual

Envie tudo para o repositório (GitHub/GitLab) que o build usa.

### 2. Gerar imagem Docker **nova** (sem cache de build)

Na máquina de CI ou local, com Docker instalado:

```bash
cd sigepa
docker build --no-cache -t SEU_USUARIO/sigepa:latest .
docker push SEU_USUARIO/sigepa:latest
```

Troque `SEU_USUARIO/sigepa` pela imagem que o Portainer/Swarm usa hoje.

> **Importante:** `--no-cache` força copiar o `static/` novo e rodar `collectstatic` de novo.

### 3. Atualizar o serviço em produção

- Se usa **Shepherd**: ele puxa a tag `latest` após alguns minutos; confira se a data da imagem no Portainer mudou.
- Se sobe manual no Portainer: **Recreate** / **Pull and redeploy** do serviço `sigepa`.

### 4. Conferir no navegador

1. Abra a ficha de ocorrência.
2. **F12** → aba **Rede** → recarregar com **Ctrl+F5**.
3. Procure `ocorrencia-form` — o nome do arquivo deve ter um **hash** no meio (ex.: `ocorrencia-form.8f3a2b1c.js`).
4. Se ainda aparecer só `ocorrencia-form.js` sem hash, a imagem antiga ainda está rodando.

## Checklist rápido

| Passo | Feito? |
|-------|--------|
| Push do código com `config/settings/prod.py` novo | ☐ |
| `docker build --no-cache` | ☐ |
| `docker push` | ☐ |
| Container/serviço recriado em produção | ☐ |
| Ctrl+F5 na ficha — JS com hash no nome | ☐ |

## Desenvolvimento local (não muda)

No seu PC, `runserver` continua lendo `static/` direto. Não precisa rebuild para testar — só em produção.

## Se algo ainda falhar

- **CEP não preenche:** teste `https://sigepa.saude.pa.gov.br/core/api/cep/?cep=66010000` — se der erro, pode ser Redis ou firewall (não é só JS).
- **Login sem “Registre-se”:** é template Python — se não mudou, a imagem antiga ainda está no ar.

## Contato técnico

Versão do formulário no JS (só para conferência no código-fonte): procure no início de `static/js/ocorrencia-form.js` o comentário `SIGEPA-STATIC-VERSION`.
