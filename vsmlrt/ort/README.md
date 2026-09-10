# VapourSynth-MLRT-ORT

This package contains the ONNX Runtime backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

To install the standard CPU/DirectML/CoreML package:

```bash
pip install vapoursynth-mlrt-ort
```

To install the CUDA-enabled package:

```bash
pip install "vapoursynth-mlrt-ort[cuda]"
```

## Building from source

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. MSVC 2019+, GCC, Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies** (must be built/installed before the plugin):
  - `onnxruntime` (ONNX Runtime SDK — built from source in CI)
  - `ONNX` (built from source, version matched to ONNX Runtime's pinned submodule)
- **Backend-specific Dependencies**:
  - **DirectML** (Windows only): DirectML SDK. Set `DML_DIR` to the SDK directory.
  - **CUDA** (Windows/Linux): `CUDAToolkit` and `cuDNN`. Ensure `CUDA_PATH` and `CUDNN_PATH`/`CUDNN_HOME` are set.
  - **CoreML** (macOS only): Enabled automatically, no extra setup needed.

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/ort/vs-mlrt
   ```

2. **Build ONNX Runtime from source** (or install a pre-built SDK), then **build ONNX from source** using the version pinned by ONNX Runtime (`onnxruntime/cmake/external/onnx/`). Both must be discoverable by CMake (via `CMAKE_PREFIX_PATH` or installed system-wide).

3. **Set environment variables** for backend-specific SDKs:

   ```powershell
   # Windows DirectML
   $env:DML_DIR = "C:\Path\To\DirectML"
   ```

4. **Build the wheel:**

   ```bash
   uv build --package vapoursynth-mlrt-ort
   ```

   To disable bundling CUDA provider libraries into the main wheel (CI does this, shipping them in a separate `vapoursynth-mlrt-ort-cuda` package instead):

   ```bash
   uv build --package vapoursynth-mlrt-ort -C "cmake.define.INSTALL_CUDA=OFF"
   ```
---

Detailed parameter information from the parent project follows.

---
