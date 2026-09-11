# Cross platform shebang:
shebang := if os() == 'windows' {
  'pwsh.exe'
} else {
  '/usr/bin/env pwsh'
}

set windows-shell := ['pwsh.exe', '-CommandWithArgs']
set positional-arguments

# Format CMake files (Windows)
format:
  #!{{shebang}}
  $files = git ls-files --others --cached --exclude-standard | Select-String -Pattern 'CMakeLists\.txt$', '\.cmake$' | ForEach-Object { $_.ToString() }
  if ($files) {
    uv run python -m gersemi $files -i --definitions bm3dcuda/bm3dcpu/Common.cmake
  }
  uv run ruff format .

# Show submodule status with lightweight tags
substatus:
  git submodule foreach "git rev-parse --short HEAD; git describe --tags --always"

# Launch a Developer PowerShell session with MSVC environment (x64)
[windows]
dev-shell:
  @pwsh -NoProfile -ExecutionPolicy Bypass -NoExit -File scripts\Enter-DevShell.ps1

# Build one or more CPU packages
build *args:
  #!{{shebang}}
  if ($args.Count -eq 0) {
    Write-Host "Please specify at least one package to build" -ForegroundColor Yellow
    exit 1
  }
  foreach ($pkg in $args) {
    switch ($pkg) {
      "ares"         { & scripts/builds/Build-Ares.ps1 }
      "atools"       { & scripts/builds/Build-ATools.ps1 }
      "bm3dcpu"      { & scripts/builds/Build-BM3DCPU.ps1 }
      "fmtc"         { & scripts/builds/Build-FMTC.ps1 }
      "dfttest2_cpu" { & scripts/builds/Build-DFTTest2-CPU.ps1 }
      "dfttest2_gcc" { & scripts/builds/Build-DFTTest2-GCC.ps1 }
      default {
        Write-Error "Unknown package"
        exit 1
      }
    }
  }
