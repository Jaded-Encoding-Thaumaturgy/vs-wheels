# VapourSynth-MLRT-MIGX

This package contains the MIGraphX backend implementation of the [vs-mlrt](https://github.com/Ichunjo/vs-mlrt) plugin.

## Installation

```bash
pip install vapoursynth-mlrt-migx
```

## Building from source

Only Linux x86-64 is currently supported.

### Requirements

- **C++ Compiler**: C++20 compatible (e.g. GCC, AMD Clang)
- **Build Tools**: [uv](https://docs.astral.sh/uv/), CMake, Ninja
- **Dependencies**:
  - `migraphx` (MIGraphX SDK — installed via ROCm packages)
  - `hip` (ROCm HIP runtime)
  - ROCm components: `base`, `runtime-devel`, `llvm`, `blas-devel`, `hipblas-common-devel`, `dnn-devel`
- **Environment Variables**:
  - `ROCM_PATH`: Path to ROCm installation (defaults to `/opt/rocm` if not set)

### Compilation

1. **Initialize the submodule:**

   ```bash
   git submodule update --init --recursive vsmlrt/migx/vs-mlrt
   ```

2. **Install ROCm, HIP, and MIGraphX** via your system package manager:

   ```bash
   # Example (RHEL/Fedora)
   dnf install rocm-devel migraphx-devel
   ```

3. **Set `ROCM_PATH`** if ROCm is not installed in the default `/opt/rocm`:

   ```bash
   export ROCM_PATH="/opt/rocm"
   ```

4. **Build the wheel:**

   ```bash
   uv build --wheel --package vapoursynth-mlrt-migx
   ```

---

Detailed parameter information from the parent project follows.

---
