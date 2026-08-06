cmake_minimum_required(VERSION 3.22)
project(VSORT_CUDA_Package LANGUAGES NONE)

# === Dependencies ===
find_package(onnxruntime REQUIRED)

get_filename_component(_ROOT "${onnxruntime_DIR}/../../.." ABSOLUTE)

if(WIN32)
  set(ORT_CUDA_PROVIDER "${_ROOT}/lib/onnxruntime_providers_cuda.dll")
  set(ORT_CUDA_DESTINATION "vsort")
else()
  set(ORT_CUDA_PROVIDER "${_ROOT}/lib64/libonnxruntime_providers_cuda.so")
  set(ORT_CUDA_DESTINATION ".")
endif()


if(NOT EXISTS "${ORT_CUDA_PROVIDER}")
  message(FATAL_ERROR "Missing ${ORT_CUDA_PROVIDER}")
endif()

install(FILES "${ORT_CUDA_PROVIDER}" DESTINATION "${ORT_CUDA_DESTINATION}")
