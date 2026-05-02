# VSWheels

VSWheels provides pre-built wheels for various VapourSynth plugins.

PEP 503-compliant Python package index URL: [https://jaded-encoding-thaumaturgy.github.io/vs-wheels/](https://jaded-encoding-thaumaturgy.github.io/vs-wheels/)

## Installation

If downloading from the vs-wheels index:

- Using uv

  ```bash
  uv add --index https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple <package-name>
  ```

- Using pip

  ```bash
  pip install <package-name> --extra-index-url https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple
  ```

## Configuration

To avoid specifying the index URL manually, you can configure your tools to include the `vs-wheels` index by default.

### pip

Add the repository as an `extra-index-url` in your [configuration file](https://pip.pypa.io/en/stable/topics/configuration/#location).

```ini
[global]
extra-index-url = https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple
```

### uv

`uv` provides multiple methods for configuring index URLs.

- [Configuration files](https://docs.astral.sh/uv/concepts/configuration-files/).
- [Pinning a package to an index](https://docs.astral.sh/uv/concepts/indexes/#pinning-a-package-to-an-index).

#### Project Configuration

- **pyproject.toml**

  ```toml
  [[tool.uv.index]]
  name = "vs-wheels"
  url = "https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
  ```

- **uv.toml**

  ```toml
  [[index]]
  name = "vs-wheels"
  url = "https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
  ```

#### User Configuration (Global)

To use the index across all your projects, add it to your user-level `uv.toml`.

- **Windows:** `%APPDATA%\uv\uv.toml`
- **Linux/macOS:** `~/.config/uv/uv.toml`

```toml
[[index]]
name = "vs-wheels"
url = "https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
```

#### System-wide Configuration

To use the index system-wide, add it to your system-level `uv.toml`.

```toml
[[index]]
name = "vs-wheels"
url = "https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
```

#### Environment Variables

Or as environment variables for quick configuration or in CI/CD pipelines.

```bash
# Unix-like
export UV_INDEX="https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
```

```powershell
# PowerShell
$env:UV_INDEX = "https://jaded-encoding-thaumaturgy.github.io/vs-wheels/simple"
```

## Available Packages

### BM3DCPU

Available on PyPI.

- **2.16**: Yanked.
- **2.16.1**: Yanked.
- **2.16.2**: Yanked.
- **2.16.3**: Matches upstream R2.16.

### BM3DCUDA

Available on PyPI.

- **2.16**: Matches upstream release R2.16.
  - **Windows**: Compiled with CUDA 13.0.1 and Visual Studio 2022.
  - **Linux**: Compiled with CUDA 12.8.
- **2.17.dev1**:
  - **Windows**: Compiled with CUDA 13.2.1 and Visual Studio 2026.
  - **Linux**: Compiled with CUDA 13.2.

### BM3DHIP

Available on PyPI.

- **2.16**: Matches upstream release R2.16.
  - **Windows**: Compiled with HIP 6.4.2 and Visual Studio 2022.
  - **Linux**: Compiled with HIP 7.0.
- **2.17.dev1**:
  - **Windows**: Compiled with HIP 7.1.1 and Visual Studio 2026.
  - **Linux**: Compiled with HIP 7.2.2.

### DFTTEST2

### VS-MLRT

### FMTCONV / FMTC

Available on vs-wheels index and on all platforms.

- **31**: Matches upstream release R31.
  - **Windows**: Compiled with Visual Studio 2026.
