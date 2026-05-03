# dfttest2

A VapourSynth re-implementation of DFTTest.

This package serves as a **meta-package** providing:

1.  A high-level **Python interface** for `dfttest2`.
2.  Optional **backend dependencies** via extras to simplify installation.

## Backends

### **GPU Backends**

| Backend  | Platform                                | Implementation Type        |
| -------- | --------------------------------------- | -------------------------- |
| `nvrtc`  | Windows, Linux (x86-64, aarch64)        | JIT Compilation            |
| `hiprtc` | Windows, Linux (x86-64)                 | JIT Compilation            |
| `cufft`  | Windows, Linux (x86-64, aarch64)        | Library                    |
| `hipfft` | Windows, Linux (x86-64)                 | Library                    |
| `cpu`    | Windows, Linux (x86-64), macOS (x86-64) | VCL                        |
| `gcc`    | All Platforms                           | Compiler Vector Extensions |

### **Which one to use?**

| Backend | Requirement                         |
| ------- | ----------------------------------- |
| NVRTC   | `sbsize=16` and CUDA-enabled system |
| HIPRTC  | `sbsize=16` and HIP-enabled system  |
| cuFFT   | CUDA-enabled system                 |
| hipFFT  | HIP-enabled system                  |
| CPU     | `sbsize=16`                         |
| GCC     | `sbsize=16`                         |

**Approximate Speed:** NVRTC == HIPRTC >> cuFFT > hipFFT > CPU == GCC

## Installation

For example, to install the NVRTC and CPU backends:

```bash
pip install dfttest2[nvrtc,cpu]
```

---

README.md from parent project

---
