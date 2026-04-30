<#
.SYNOPSIS
    Configures the current PowerShell session with the Visual Studio Developer environment.
    
.DESCRIPTION
    Locates the latest Visual Studio installation and imports the DevShell module.
    Sets up the environment for x64 development by default.
#>

$vsPath = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -products * -property installationPath

if (-not $vsPath) {
    Write-Error "Visual Studio installation not found."
    return
}

$devShellDll = Join-Path $vsPath 'Common7\Tools\Microsoft.VisualStudio.DevShell.dll'

if (-not (Test-Path $devShellDll)) {
    Write-Error "DevShell module not found at: $devShellDll"
    return
}

Import-Module $devShellDll
Enter-VsDevShell -VsInstallPath $vsPath -SkipAutomaticLocation -DevCmdArguments '-arch=x64'

Write-Host "Developer Environment Loaded (x64) from $vsPath" -ForegroundColor Green
