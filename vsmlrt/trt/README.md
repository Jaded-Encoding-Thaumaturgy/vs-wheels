# VapourSynth-MLRT-TRT

This package contains the TensorRT backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

```bash
pip install vapoursynth-mlrt-trt
```

## Building from source

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. MSVC 2019+, GCC, Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies**:
  - `CUDAToolkit` (nvcc, cudart, cuda_profiler_api)
  - `TensorRT` SDK (including runtime, plugins, dispatch, and lean libraries)
- **Environment Variables**:
  - `TENSORRT_HOME`: Path to the TensorRT installation directory (must contain `include`, `lib`, and `bin`).

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/trt/vs-mlrt
   ```

2. **Set the `TENSORRT_HOME` environment variable** to point to your TensorRT installation:

   ```powershell
   # Windows (PowerShell)
   $env:TENSORRT_HOME = "C:\Path\To\TensorRT"
   ```

   ```bash
   # Linux
   export TENSORRT_HOME="/path/to/TensorRT"
   ```

3. **Build the wheel:**

   ```bash
   uv build --package vapoursynth-mlrt-trt
   ```
---

Detailed parameter information from the parent project follows.

---
