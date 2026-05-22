# Erro 500 em produção (sigepa.saude.pa.gov.br)

Com `DEBUG=False` o site só mostra **Server Error (500)**. O motivo real está nos **logs do container**.

## 1. Ver o erro real (Portainer)

1. **Home** → **PRD**
2. **Services** → serviço do SIGEPA (`sigepa_sigepa` ou nome parecido)
3. Aba **Logs** (ou **Service logs**)
4. Recarregue a página do site e olhe a linha vermelha no mesmo horário

Copie a última traceback (Python) — ela diz a causa exata.

---

## 2. Causas mais comuns

| Causa | Sintoma nos logs | O que fazer |
|-------|------------------|-------------|
| **Banco MySQL** | `Can't connect to MySQL`, `Access denied` | Conferir `DB_HOST`, `DB_USER`, `DB_PASSWORD` no serviço |
| **Redis** | `ModuleNotFoundError: redis`, `Connection refused` 6379 | Deixar `USE_REDIS=False` (padrão) ou subir Redis + `USE_REDIS=True` |
| **ALLOWED_HOSTS** | `DisallowedHost` | Incluir `sigepa.saude.pa.gov.br` em `ALLOWED_HOSTS` |
| **Estáticos (manifest)** | `Missing static files`, `ValueError` em `staticfiles` | Rebuild da imagem; remover volume `static_data` se existir |
| **Migrate** | Tabela não existe | `docker exec` → `python manage.py migrate` |

---

## 3. Variáveis obrigatórias no serviço SIGEPA

Confira no Portainer → **sigepa** → **Environment**:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=...
ALLOWED_HOSTS=sigepa.saude.pa.gov.br
CSRF_TRUSTED_ORIGINS=https://sigepa.saude.pa.gov.br
DB_NAME=sigepa
DB_USER=sigepa
DB_PASSWORD=...
DB_HOST=mysql.saude.pa.gov.br
DB_PORT=3306
USE_REDIS=False
```

Não defina `REDIS_URL` até ter Redis rodando de verdade.

---

## 4. Depois de corrigir o código

1. Push na `main` (GitHub Actions publica `nivspa/sigepa:producao`)
2. **Services** → sigepa → **Update** → Pull latest
3. Teste de novo o site

---

## 5. Teste rápido no container

Console do serviço ou `docker exec` no container do SIGEPA:

```bash
python manage.py check
python manage.py migrate --plan
```

Se `check` falhar, a mensagem indica o problema.
