# VapourSynth-BM3DCUDA

This package contains the CUDA implementation of the [VapourSynth-BM3DCUDA](https://github.com/WolframRhodium/VapourSynth-BM3DCUDA) filter.

## Installation

```bash
pip install vapoursynth-bm3dcuda
```

## Building from source

### Requirements

- **[CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit-archive)**: 12.8 or newer.
- **C++ Compiler**: A C++20 compatible compiler.
  - **Windows**: Visual Studio 2022 or newer.
  - **Linux**: GCC

- Windows

  ```powershell
  $env:CUDA_PATH = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0"
  uv build --package vapoursynth-bm3dcuda
  ```

- Linux
  ```bash
  export CUDA_PATH=/usr/local/cuda-12.8
  uv build --package vapoursynth-bm3dcuda
  ```

---

Detailed parameter information from the parent project follows.

---
