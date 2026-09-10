# VapourSynth-MLRT-NCNN

This package contains the NCNN backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

```bash
pip install vapoursynth-mlrt-ncnn
```

## Building from source

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. MSVC 2019+, GCC, Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies** (must be built/installed before the plugin):
  - `ncnn` (built from source in CI with Vulkan support enabled)
  - `ONNX` (built from source in CI)
  - `Vulkan` SDK ([LunarG](https://vulkan.lunarg.com/sdk/home))
- **Platforms**: Windows, Linux, macOS (uses Metal via MoltenVK on macOS)

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/ncnn/vs-mlrt
   ```

2. **Install the Vulkan SDK** from [LunarG](https://vulkan.lunarg.com/sdk/home).

3. **Build NCNN from source** (with Vulkan enabled) and **build ONNX from source**. Both must be discoverable by CMake (via `CMAKE_PREFIX_PATH` or installed system-wide).

4. **Build the wheel:**

   ```bash
   uv build --package vapoursynth-mlrt-ncnn
   ```
---

Detailed parameter information from the parent project follows.

---
