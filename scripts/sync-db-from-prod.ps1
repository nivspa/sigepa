# Copia o banco de producao (.env.prod) para o MySQL local (.env).
# Uso (na raiz do projeto):
#   .\scripts\sync-db-from-prod.ps1
#   .\scripts\sync-db-from-prod.ps1 -SkipDump -DumpFile backups\sigepa_prod_20260522_124615.sql

param(
    [switch]$SkipDump,
    [string]$DumpFile = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Read-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Arquivo nao encontrado: $Path"
    }
    $vars = @{}
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $idx = $line.IndexOf("=")
        if ($idx -lt 1) { return }
        $key = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim()
        $vars[$key] = $value
    }
    return $vars
}

function Get-MySqlExe {
    param([string]$Name)
    if ($env:MYSQL_BIN) {
        $candidate = Join-Path $env:MYSQL_BIN $Name
        if (Test-Path $candidate) { return $candidate }
    }
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $default = "C:\Program Files\MySQL\MySQL Server 8.4\bin\$Name"
    if (Test-Path $default) { return $default }
    throw "Nao encontrei $Name. Instale o MySQL client ou defina MYSQL_BIN."
}

$prod = Read-DotEnv (Join-Path $ProjectRoot ".env.prod")
$local = Read-DotEnv (Join-Path $ProjectRoot ".env")

$prodKeys = @("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
$localKeys = @("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
foreach ($key in $prodKeys) {
    if (-not $prod[$key]) { throw ".env.prod sem $key" }
}
foreach ($key in $localKeys) {
    if (-not $local[$key]) { throw ".env sem $key" }
}

$mysql = Get-MySqlExe "mysql.exe"
$mysqldump = Get-MySqlExe "mysqldump.exe"
$backupsDir = Join-Path $ProjectRoot "backups"
New-Item -ItemType Directory -Path $backupsDir -Force | Out-Null

if (-not $DumpFile) {
    $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $DumpFile = Join-Path $backupsDir "sigepa_prod_$stamp.sql"
}

if (-not $SkipDump) {
    Write-Host "Exportando producao ($($prod.DB_HOST))..."
    # --result-file grava UTF-8 direto no disco (evita corromper acentos no pipe do PowerShell)
    $env:MYSQL_PWD = $prod.DB_PASSWORD
    & $mysqldump `
        -h $prod.DB_HOST `
        -P $prod.DB_PORT `
        -u $prod.DB_USER `
        --default-character-set=utf8mb4 `
        --single-transaction `
        --routines `
        --triggers `
        --set-gtid-purged=OFF `
        --no-tablespaces `
        --result-file="$DumpFile" `
        $prod.DB_NAME 2>$null
    if ($LASTEXITCODE -ne 0) { throw "mysqldump falhou (codigo $LASTEXITCODE)" }
    Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
    $sizeMb = [math]::Round((Get-Item $DumpFile).Length / 1MB, 2)
    Write-Host "Dump salvo: $DumpFile ($sizeMb MB)"
} else {
    if (-not (Test-Path $DumpFile)) { throw "Dump nao encontrado: $DumpFile" }
    Write-Host "Usando dump existente: $DumpFile"
}

Write-Host "Preparando banco local ($($local.DB_HOST))..."
$env:MYSQL_PWD = $local.DB_PASSWORD
& $mysql -h $local.DB_HOST -P $local.DB_PORT -u $local.DB_USER -e @"
DROP DATABASE IF EXISTS ``$($local.DB_NAME)``;
CREATE DATABASE ``$($local.DB_NAME)`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"@ 2>&1 | Out-String | Write-Host
if ($LASTEXITCODE -ne 0) {
    Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
    throw "Falha ao criar banco local. Verifique DB_USER/DB_PASSWORD no .env"
}

Write-Host "Importando dump no banco local..."
$importCmd = "`"$mysql`" -h $($local.DB_HOST) -P $($local.DB_PORT) -u $($local.DB_USER) $($local.DB_NAME) < `"$DumpFile`""
cmd /c $importCmd | Out-Null
if ($LASTEXITCODE -ne 0) {
    Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
    throw "Importacao falhou (codigo $LASTEXITCODE)"
}
Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue

Write-Host "Concluido. Banco local '$($local.DB_NAME)' atualizado com dados de producao."
Write-Host "Suba o app: .\venv\Scripts\Activate.ps1; python manage.py runserver"
