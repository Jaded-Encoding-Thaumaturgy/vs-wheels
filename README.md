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

### DFTTEST2

### VS-MLRT

### FMTCONV / FMTC

Available on vs-wheels index and on all platforms.

- **31**: Matches upstream release R31.
  - **Windows**: Compiled with Visual Studio 2026.
