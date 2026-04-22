<#
.SYNOPSIS
  Push rápido para o GitHub — TrilhaGracaSoberana
.DESCRIPTION
  Faz commit (com mensagem) e push usando o token configurado no remote.
  Uso:  .\scripts\git-push.ps1 "mensagem do commit"
  Ou sem argumento para commit vazio (trigger de rebuild).
#>
param(
  [string]$Msg = ""
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# ── Verificar se o remote já tem token embutido ──────────
$remote = git remote get-url origin 2>&1
if ($remote -notmatch "https://[^@]+@github.com") {
  # Tenta ler token do .env ou variável de ambiente
  $token = $env:GITHUB_PAT
  if (-not $token) {
    $envFile = Join-Path $PSScriptRoot ".." ".env"
    if (Test-Path $envFile) {
      $match = Select-String -Path $envFile -Pattern "^GITHUB_PAT=(.+)$"
      if ($match) { $token = $match.Matches[0].Groups[1].Value.Trim() }
    }
  }
  if ($token) {
    $owner = "robottraderglobal-blip"
    $repo  = "TrilhaGracaSoberana"
    git remote set-url origin "https://${token}@github.com/${owner}/${repo}.git"
    Write-Host "[OK] Remote atualizado com token." -ForegroundColor Green
  } else {
    Write-Host "[ERRO] GITHUB_PAT nao encontrado no .env nem em variavel de ambiente." -ForegroundColor Red
    Write-Host "       Adicione GITHUB_PAT=ghp_xxx no .env e rode novamente." -ForegroundColor Yellow
    exit 1
  }
}

# ── Commit ────────────────────────────────────────────────
if ($Msg -eq "") {
  git commit --allow-empty -m "chore: trigger rebuild $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
  Write-Host "[OK] Commit vazio (trigger rebuild)." -ForegroundColor Cyan
} else {
  git add -A
  git commit -m $Msg
  Write-Host "[OK] Commit: $Msg" -ForegroundColor Cyan
}

# ── Push ──────────────────────────────────────────────────
git push origin HEAD 2>&1
if ($LASTEXITCODE -eq 0) {
  Write-Host "[OK] Push concluido com sucesso!" -ForegroundColor Green
} else {
  Write-Host "[ERRO] Push falhou. Verifique o token." -ForegroundColor Red
  exit 1
}
