# VapourSynth MLRT (Machine Learning Runtime Tools) Backends

This document lists all the backends available in `vsmlrt` distributed by **[VSWheels](https://github.com/Jaded-Encoding-Thaumaturgy/vs-wheels)**.
The upstream project is [AmusementClub/vs-mlrt](https://github.com/AmusementClub/vs-mlrt).

## Summary Table of Backends

| Backend          | Wheel Package               | Supported Platforms (CI Builds) | Dependencies / API                       | Target Hardware                                      |
| :--------------- | :-------------------------- | :------------------------------ | :--------------------------------------- | :--------------------------------------------------- |
| **`ORT CPU`**    | `vapoursynth-mlrt-ort`      | Windows, Linux, macOS           | ONNX Runtime (CPU)                       | Standard CPU inference                               |
| **`ORT CUDA`**   | `vapoursynth-mlrt-ort-cuda` | Windows, Linux                  | ONNX Runtime (CUDA), CUDA Toolkit, cuDNN | NVIDIA GPUs                                          |
| **`ORT DML`**    | `vapoursynth-mlrt-ort`      | Windows                         | ONNX Runtime (DirectML), Direct3D 12     | DirectX 12-capable GPUs                              |
| **`ORT COREML`** | `vapoursynth-mlrt-ort`      | macOS                           | ONNX Runtime (CoreML)                    | Apple Silicon                                        |
| **`OV CPU`**     | `vapoursynth-mlrt-ov`       | Windows, Linux, macOS           | OpenVINO, ONNX                           | Standard CPU inference                               |
| **`OV GPU`**     | `vapoursynth-mlrt-ov`       | Windows, Linux x64              | OpenVINO, OpenCL                         | Intel Integrated Graphics, dedicated GPUs via OpenCL |
| **`OV NPU`**     | `vapoursynth-mlrt-ov`       | Windows, Linux                  | OpenVINO, Intel NPU drivers              | Intel Core Ultra Neural Processing Units (NPUs)      |
| **`TRT`**        | `vapoursynth-mlrt-trt`      | Windows, Linux                  | TensorRT, CUDA Toolkit                   | NVIDIA GPUs                                          |
| **`TRT RTX`**    | `vapoursynth-mlrt-trt_rtx`  | Windows, Linux                  | TensorRT RTX, CUDA Toolkit               | NVIDIA RTX GPUs                                      |
| **`NCNN VK`**    | `vapoursynth-mlrt-ncnn`     | Windows, Linux, macOS           | NCNN, Vulkan SDK, ONNX                   | Broad GPU support via Vulkan                         |
| **`MIGX`**       | `vapoursynth-mlrt-migx`     | Linux x64                       | AMD ROCm/HIP, MIGraphX, MIOpen, rocBLAS  | AMD Radeon / Instinct GPUs (ROCm-capable)            |

## Picking the Right Backend

Below is a decision tree to help select the most suitable backend depending on your hardware, operating system, and performance requirements:

```mermaid
graph TD
    Start([Pick Backend]) --> HW{Hardware?}

    %% NVIDIA branch
    HW -->|Nvidia GPU| NV_Usage{Usage Goal?}
    NV_Usage -->|"Production"| NV_RTX{Trade-off}
    NV_Usage -->|"Fast Startup"| NV_OS{OS?}
    NV_RTX -->|Max performance| TRT["TRT"]
    NV_RTX -->|Faster compilation| TRT_RTX["TRT RTX"]
    NV_OS -->|Linux | NV_OS_linux["ORT CUDA"]
    NV_OS -->|Windows | NV_OS_win["ORT DML"]

    %% AMD branch
    HW -->|AMD GPU| AMD_OS{OS?}
    AMD_OS -->|Linux| AMD_Usage{Usage Goal?}
    AMD_Usage -->|Max Performance| MIGX["MIGX"]
    AMD_Usage -->|Fast Startup| NCNN_VK_AMD["NCNN VK"]
    AMD_OS -->|Windows| ORT_DML["ORT DML"]
    AMD_OS -->|macOS| NCNN_VK_mac["NCNN VK"]

    %% Intel branch
    HW -->|Intel GPU / NPU| Intel_Dev{Device Type?}
    Intel_Dev -->|NPU| OV_NPU["OV NPU"]
    Intel_Dev -->|iGPU / dGPU| Intel_OS{OS?}
    Intel_OS -->|Linux| OV_GPU_intel["OV GPU"]
    Intel_OS -->|Windows| ORT_DML_intel["ORT DML"]

    %% Apple Silicon branch
    HW -->|Apple Silicon / macOS| Mac_Reqs{External
    dependencies?}
    Mac_Reqs -->|Yes| NCNN_VK_mac2["NCNN VK"]
    Mac_Reqs -->|No| ORT_COREML["ORT COREML"]

    %% Generic CPU branch
    HW -->|Generic CPU| OV_CPU_gen["OV CPU"]

    classDef default fill:#1e1e24,stroke:#3a3a4a,stroke-width:2px,color:#d4d4d8;
    classDef decision fill:#2a2b36,stroke:#4f46e5,stroke-width:2px,color:#e0e7ff;
    classDef choice fill:#162521,stroke:#10b981,stroke-width:2px,color:#d1fae5;

    class HW,NV_Usage,NV_OS,NV_RTX,AMD_OS,AMD_Usage,Intel_Dev,Intel_Usage,Mac_Usage,Intel_OS,Mac_Reqs,CPU_Platform decision;
    class TRT_RTX,TRT,ORT_CUDA,NV_OS_win,MIGX,NV_OS_linux,NCNN_VK_AMD,OV_GPU_intel,ORT_DML_intel,ORT_DML,OV_NPU,OV_GPU,OV_CPU,ORT_COREML,NCNN_VK_mac2,NCNN_VK_mac,OV_CPU_gen,ORT_CPU choice;
```

## Notes

- The MIGX backend requires MIGraphX and ROCm/HIP to be installed separately.
  Install `migraphx` through your system package manager, for example `dnf install migraphx`.
- On macOS, the NCNN backend requires Vulkan support through MoltenVK.
  Install it with Homebrew, for example `brew install molten-vk`.
- The TRT and TRT RTX wheels do not bundle `trtexec` or `tensorrt_rtx`.
  Use the `vsscale` (vsjetpack) Python API for engine generation, or provide the matching external executable yourself.
