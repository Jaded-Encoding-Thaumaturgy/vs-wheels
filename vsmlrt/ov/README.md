# VapourSynth-MLRT-OV

This package contains the OpenVINO backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

```bash
pip install vapoursynth-mlrt-ov
```

## Building from source

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. MSVC 2019+, GCC, Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies** (must be built/installed before the plugin):
  - `OpenVINO` SDK (built from source in CI — includes OpenVINO Runtime, TBB, and plugins)
  - `ONNX` (built from source, version matched to OpenVINO's pinned submodule at `openvino/thirdparty/onnx/onnx`)
  - `Protobuf` (used by both ONNX and the plugin; CI uses OpenVINO's bundled Protobuf with `use-external-protobuf: true`)
- **CMake Options**:
  - `WIN32_SHARED_OPENVINO` (defaults to `ON` in `pyproject.toml`): When enabled, copies OpenVINO Runtime and dependency DLLs (`tbb12.dll`, plugins, etc.) into the wheel.

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/ov/vs-mlrt
   ```

2. **Build OpenVINO from source** (or install a pre-built SDK), then **build ONNX from source** using the version pinned by OpenVINO (`openvino/thirdparty/onnx/onnx`). Both must be discoverable by CMake (via `CMAKE_PREFIX_PATH` or installed system-wide).

3. **Build the wheel:**

   ```bash
   uv build --package vapoursynth-mlrt-ov
   ```

---

Detailed parameter information from the parent project follows.

---
