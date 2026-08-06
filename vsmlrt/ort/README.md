# VapourSynth-MLRT-ORT

This package contains the ONNX Runtime backend implementation of the [vs-mlrt](https://github.com/AmusementClub/vs-mlrt) plugin.

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
- **Dependencies**:
  - `onnxruntime` (ONNX Runtime SDK)
  - `ONNX`
  - `Protobuf`
- **Backend Dependencies**:
  - **DirectML** (Windows): Requires DirectML SDK. Define the `DML_DIR` environment/CMake variable to point to the SDK directory.
  - **CUDA** (Windows and Linux): Requires `CUDAToolkit` and `cuDNN` SDKs. Ensure `CUDA_PATH`, `CUDNN_PATH` / `CUDNN_HOME` are set correctly.

### Compilation

The package builds with CUDA support on Windows and Linux, CoreML on macOS, and DirectML on Windows:

```powershell
uv build --package vapoursynth-mlrt-ort
```

---

Detailed parameter information from the parent project follows.

---
