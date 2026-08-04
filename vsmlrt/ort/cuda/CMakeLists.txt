cmake_minimum_required(VERSION 3.15)
project(ORT_CUDA_Package LANGUAGES NONE)

if(WIN32)
  set(ORT_CUDA_PROVIDER "onnxruntime_providers_cuda.dll")
  set(ORT_CUDA_DESTINATION "vsort")
else()
  set(ORT_CUDA_PROVIDER "libonnxruntime_providers_cuda.so")
  set(ORT_CUDA_DESTINATION ".")
endif()

set(ORT_CUDA_PROVIDER_PATH "${CMAKE_CURRENT_SOURCE_DIR}/provider/${ORT_CUDA_PROVIDER}")

if(NOT EXISTS "${ORT_CUDA_PROVIDER_PATH}")
  message(FATAL_ERROR "Missing ${ORT_CUDA_PROVIDER}")
endif()

install(FILES "${ORT_CUDA_PROVIDER_PATH}" DESTINATION "${ORT_CUDA_DESTINATION}")
