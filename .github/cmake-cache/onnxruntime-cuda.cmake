# CUDA-specific ONNX Runtime cache variables.

set(onnxruntime_USE_FLASH_ATTENTION OFF CACHE BOOL "")
set(onnxruntime_USE_LEAN_ATTENTION OFF CACHE BOOL "")
set(onnxruntime_USE_MEMORY_EFFICIENT_ATTENTION OFF CACHE BOOL "")
set(onnxruntime_USE_FPA_INTB_GEMM OFF CACHE BOOL "")
set(onnxruntime_USE_TRT_FUSED_ATTENTION OFF CACHE BOOL "")
# Disable 1.30.0 GenAI/LLM kernels not needed for video inference
set(onnxruntime_USE_FP4_QMOE OFF CACHE BOOL "")
set(onnxruntime_USE_INT4_KV_CACHE OFF CACHE BOOL "")
set(onnxruntime_USE_FP8_KV_CACHE OFF CACHE BOOL "")

set(onnxruntime_USE_CUDA ON CACHE BOOL "")
set(onnxruntime_NVCC_THREADS 1 CACHE STRING "")
set(onnxruntime_USE_CUDA_NHWC_OPS ON CACHE BOOL "")
set(onnxruntime_ENABLE_NVTX_PROFILE OFF CACHE BOOL "")
set(onnxruntime_DISABLE_FLOAT4_TYPES ON CACHE BOOL "")

set(CMAKE_CUDA_ARCHITECTURES "75-real;86-real;89-real;120-real" CACHE STRING "")

set(CMAKE_CUDA_FLAGS "-D__NV_NO_VECTOR_DEPRECATION_DIAG -Xfatbin=-compress-all --compress-mode=size" CACHE STRING "")
