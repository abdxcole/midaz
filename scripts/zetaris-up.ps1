<#
.SYNOPSIS
  HU-00: levanta Zetaris local (Docker Compose) y prueba un SELECT por REST.

.DESCRIPTION
  Basado en github.com/zetaris/getting-started (docs/install/updated_zetaris_installation_guide.md
  y docs/connections/client-setup.md). No guarda ni imprime secretos: la llave se lee de
  variables de entorno (ZETARIS_API_KEY, ZETARIS_ORG_ID, ZETARIS_REST_URL).

  Antes (una sola vez, ver docs/08-hu00-zetaris.md): Docker Desktop instalado (admin), WSL2 + Ubuntu,
  bundle zetaris-platform.zip descargado de Zetaris Cloud > Run locally, `docker login
  zetarishackathon.azurecr.io` hecho, y el .env DEL BUNDLE editado (admin email/password/org).

.EXAMPLE
  .\scripts\zetaris-up.ps1 -PlatformDir C:\zetaris\zetaris-platform
  .\scripts\zetaris-up.ps1 -SkipCompose -Sql "SHOW LIGHTNING DATABASES"
#>
param(
  [string]$PlatformDir = $env:ZETARIS_PLATFORM_DIR,
  [switch]$SkipCompose,
  [string]$Sql = "SELECT 1 AS one",
  [int]$WaitSeconds = 900
)
$ErrorActionPreference = "Stop"

function Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }

if (-not $SkipCompose) {
  Step "Docker"
  if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker no esta instalado. Ver docs/08-hu00-zetaris.md, paso 1 (requiere admin)."
  }
  docker version --format "{{.Server.Version}}" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw "Docker esta instalado pero el daemon no corre: abrir Docker Desktop." }
  docker compose version
  if (-not $PlatformDir) { throw "Falta -PlatformDir (carpeta con docker-compose.yml del bundle) o `$env:ZETARIS_PLATFORM_DIR." }
  $PlatformDir = (Resolve-Path $PlatformDir).Path
  if (-not (Test-Path (Join-Path $PlatformDir "docker-compose.yml"))) { throw "No hay docker-compose.yml en $PlatformDir" }
  if (-not (Test-Path (Join-Path $PlatformDir ".env"))) { throw "No hay .env del bundle en $PlatformDir (viene en el zip; editarlo antes del primer arranque)." }

  Push-Location $PlatformDir
  try {
    Step "Validando configuracion (--quiet no imprime secretos)"
    docker compose config --quiet; if ($LASTEXITCODE -ne 0) { throw "docker compose config fallo" }
    Step "docker compose pull (la primera vez tarda 30-45 min)"
    docker compose pull; if ($LASTEXITCODE -ne 0) { throw "pull fallo: revisar 'docker login zetarishackathon.azurecr.io'" }
    Step "docker compose up -d"
    docker compose up -d; if ($LASTEXITCODE -ne 0) { throw "up fallo" }
    docker compose ps --all
  } finally { Pop-Location }
}

Step "Esperando la API REST"
$base = if ($env:ZETARIS_REST_URL) { $env:ZETARIS_REST_URL.TrimEnd('/') } else { "http://localhost:8888/api/v1.0" }
$deadline = (Get-Date).AddSeconds($WaitSeconds)
do {
  try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 ($base -replace '/api/v1.0$', '/redoc/index.html') | Out-Null; $up = $true }
  catch { $up = $false; Start-Sleep 10 }
} until ($up -or (Get-Date) -gt $deadline)
if (-not $up) { throw "La API no contesto en $WaitSeconds s. Ver: docker compose logs --tail=80 driver api bootstrap" }
Write-Host "API arriba en $base"

if (-not $env:ZETARIS_API_KEY) {
  Write-Warning "Falta ZETARIS_API_KEY. Entrar a http://localhost:3000 > Management > API Tokens > +, y en ESTA consola: `$env:ZETARIS_API_KEY = [Net.NetworkCredential]::new('', (Read-Host -AsSecureString)).Password"
  exit 2
}
if (-not $env:ZETARIS_ORG_ID) { Write-Warning "ZETARIS_ORG_ID vacio: uso 1 (verlo en Management > Organisation > ID)." }

Step "POST $base/sql-editor/sqls/run  ->  $Sql"
$body = @{ queryId = [guid]::NewGuid().ToString(); sql = $Sql; source = "SqlEditor"; limit = 100 } | ConvertTo-Json
$headers = @{
  Authorization  = "Bearer $($env:ZETARIS_API_KEY)"
  "X-Org-ID"     = $(if ($env:ZETARIS_ORG_ID) { $env:ZETARIS_ORG_ID } else { "1" })
  "X-Request-ID" = [guid]::NewGuid().ToString()
}
$sw = [Diagnostics.Stopwatch]::StartNew()
try {
  $r = Invoke-RestMethod -Method Post -Uri "$base/sql-editor/sqls/run" -Headers $headers -ContentType "application/json" -Body $body
} catch {
  $code = $_.Exception.Response.StatusCode.value__
  if ($code -eq 401) { throw "401: llave mala o vencida -> crear otra en API Tokens." }
  if ($code -eq 400) { throw "400: ZETARIS_ORG_ID no es el ID numerico o X-Request-ID invalido." }
  throw
}
$sw.Stop()
$r.data | ConvertTo-Json -Depth 6
Write-Host ("HU-00 OK: SELECT por REST en {0} ms" -f $sw.ElapsedMilliseconds) -ForegroundColor Green
