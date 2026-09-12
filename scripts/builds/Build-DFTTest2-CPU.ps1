<#
.SYNOPSIS
    Builds the vapoursynth-dfttest2_cpu package wheel.
#>

$RepoRoot = Resolve-Path "$PSScriptRoot/../.."
Push-Location $RepoRoot

try {
    Write-Host "=== Building vapoursynth-dfttest2_cpu ===" -ForegroundColor Cyan

    if ($IsWindows -or $env:OS -eq 'Windows_NT') {
        . "$RepoRoot/scripts/Enter-DevShell.ps1" 
    }

    Write-Host "Running uv build..." -ForegroundColor Cyan
    uv build --package vapoursynth-dfttest2_cpu

    Write-Host "Build completed successfully." -ForegroundColor Green
}
finally {
    Pop-Location
}
