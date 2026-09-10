# VapourSynth-MLRT-TRT-RTX

This package contains the TensorRT-based for RTX GPU inference backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

```bash
pip install vapoursynth-mlrt-trt-rtx
```

## Building from source

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. MSVC 2019+, GCC, Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies**:
  - `CUDAToolkit` (nvcc, cudart, cuda_profiler_api)
  - `TensorRT-RTX` SDK
- **Environment Variables**:
  - `TENSORRT_RTX_HOME`: Path to the TensorRT-RTX installation directory (must contain `include`, `lib`, and `bin`).

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/trt_rtx/vs-mlrt
   ```

2. **Set the `TENSORRT_RTX_HOME` environment variable** to point to your TensorRT-RTX installation:

   ```powershell
   # Windows (PowerShell)
   $env:TENSORRT_RTX_HOME = "C:\Path\To\TensorRT-RTX"
   ```

   ```bash
   # Linux
   export TENSORRT_RTX_HOME="/path/to/TensorRT-RTX"
   ```

3. **Build the wheel:**

   ```bash
   uv build --package vapoursynth-mlrt-trt-rtx
   ```

---

Detailed parameter information from the parent project follows.

---
