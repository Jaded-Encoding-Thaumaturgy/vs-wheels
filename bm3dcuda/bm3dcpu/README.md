# VapourSynth-BM3DCPU

This package contains the CPU implementation of the [VapourSynth-BM3DCUDA](https://github.com/WolframRhodium/VapourSynth-BM3DCUDA) filter.

## Installation

Install the multi-target wheel that includes binaries for multiple architectures (AVX2 and Zen4)

```bash
pip install vapoursynth-bm3dcpu
```

To compile and install the package with optimizations tailored to your specific CPU:

- Windows within the developer shell:

  ```powershell
  pip install vapoursynth-bm3dcpu --no-binary vapoursynth-bm3dcpu
  ```

- Linux:
  ```bash
  pip install vapoursynth-bm3dcpu --no-binary vapoursynth-bm3dcpu
  ```

## Building from source

### Requirements

- **C++ Compiler**: C++17 compatible.
  - **Windows**: MSVC (Visual Studio 2019+) or Clang.
  - **Linux**: GCC or Clang.

```powershell
uv build --package vapoursynth-bm3dcpu
```

---

Detailed parameter information from the parent project follows.

---
