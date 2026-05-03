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

# Show submodule status with lightweight tags
substatus:
  git submodule foreach "git rev-parse --short HEAD; git describe --tags --always"

# Launch a Developer PowerShell session with MSVC environment (x64)
[windows]
dev-shell:
  @pwsh -NoProfile -ExecutionPolicy Bypass -NoExit -File scripts\Enter-DevShell.ps1
