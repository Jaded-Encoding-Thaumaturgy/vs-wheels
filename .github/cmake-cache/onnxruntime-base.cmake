# Base ONNX Runtime cache variables shared across all platforms.

set(CMAKE_BUILD_TYPE Release CACHE STRING "")

# Build options
set(onnxruntime_BUILD_UNIT_TESTS OFF CACHE BOOL "")
set(onnxruntime_BUILD_SHARED_LIB ON CACHE BOOL "")
set(onnxruntime_ENABLE_LTO ON CACHE BOOL "")

set(onnxruntime_DISABLE_ML_OPS ON CACHE BOOL "")
set(onnxruntime_DISABLE_GENERATION_OPS ON CACHE BOOL "")
set(onnxruntime_DISABLE_FLOAT8_TYPES ON CACHE BOOL "")
set(onnxruntime_DISABLE_SPARSE_TENSORS ON CACHE BOOL "")
set(onnxruntime_DISABLE_OPTIONAL_TYPE ON CACHE BOOL "")
