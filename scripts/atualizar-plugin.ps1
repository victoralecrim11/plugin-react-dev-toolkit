<#
.SYNOPSIS
    Atualiza o React Dev Hub no Claude Code e no Codex de uma vez.

.DESCRIPTION
    Rode depois de um push para trazer a versao nova para as duas plataformas.
    Nao instala o plugin do zero -- para isso, veja o README.

    Nenhuma das duas recarrega uma sessao aberta: no Claude Code use
    /reload-plugins, no Codex reinicie o app.

.EXAMPLE
    pwsh scripts/atualizar-plugin.ps1
    pwsh scripts/atualizar-plugin.ps1 -LimparCache
#>
[CmdletBinding()]
param(
    [string]$Plugin = 'plugin-react-dev-toolkit',
    [string]$Marketplace = 'react-dev-marketplace',
    [switch]$LimparCache
)

$ErrorActionPreference = 'Continue'
$falhas = @()

function Titulo($t) { Write-Host ''; Write-Host "== $t" -ForegroundColor Cyan }
function Aviso($t)  { Write-Host "  $t" -ForegroundColor Yellow }
function Ok($t)     { Write-Host "  $t" -ForegroundColor Green }
function Existe($c) { $null -ne (Get-Command $c -ErrorAction SilentlyContinue) }

Titulo 'Claude Code'
if (Existe 'claude') {
    if ($LimparCache) {
        $cache = Join-Path $HOME '.claude/plugins/cache'
        if (Test-Path $cache) { Remove-Item -Recurse -Force $cache; Aviso "cache removido: $cache" }
    }
    claude plugin marketplace update $Marketplace
    if ($LASTEXITCODE -ne 0) { $falhas += 'claude plugin marketplace update' }
    # `plugin update` exige o nome do plugin; nao existe --all
    claude plugin update "$Plugin@$Marketplace"
    if ($LASTEXITCODE -ne 0) { $falhas += 'claude plugin update' }
    Ok 'feito. Numa sessao aberta, rode /reload-plugins.'
} else {
    Aviso "CLI 'claude' nao encontrada no PATH -- pulando."
}

Titulo 'Codex'
if (Existe 'codex') {
    if ($LimparCache) {
        $cache = Join-Path $HOME '.codex/plugins/cache'
        if (Test-Path $cache) { Remove-Item -Recurse -Force $cache; Aviso "cache removido: $cache" }
    }
    codex plugin marketplace list
    codex plugin marketplace upgrade
    if ($LASTEXITCODE -ne 0) { $falhas += 'codex plugin marketplace upgrade' }
    Ok 'feito. Reinicie o Codex para carregar os arquivos novos.'
} else {
    Aviso "CLI 'codex' nao encontrada no PATH -- pulando."
}

Write-Host ''
if ($falhas.Count -gt 0) {
    Write-Host "Falhou: $($falhas -join ', ')" -ForegroundColor Red
    exit 1
}
Ok 'Atualizacao concluida.'
