cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED SKBUILD_PROJECT_VERSION)
  set(SKBUILD_PROJECT_VERSION "0.0.0")
endif()

project(DFTTEST2_NVRTC_Package VERSION "${SKBUILD_PROJECT_VERSION}" LANGUAGES CXX)

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# === VapourSynth Include Resolution ===
find_path(
  VAPOURSYNTH_INCLUDE_DIR
  NAMES VapourSynth4.h VapourSynth.h
  HINTS
    "${CMAKE_CURRENT_SOURCE_DIR}/../../.venv/Lib/site-packages/vapoursynth/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Lib/site-packages/vapoursynth/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/../../vapoursynth/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth"
    "${CMAKE_CURRENT_SOURCE_DIR}/.venv/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/.venv/Lib/site-packages/vapoursynth"
  PATH_SUFFIXES vapoursynth/include vapoursynth include
  DOC "Path to VapourSynth headers"
)

if(VAPOURSYNTH_INCLUDE_DIR)
  message(STATUS "Found VapourSynth headers: ${VAPOURSYNTH_INCLUDE_DIR}")
else()
  message(FATAL_ERROR "VapourSynth headers not found. Ensure vapoursynth>=75 is installed.")
endif()

# === Dependencies ===
find_package(CUDAToolkit REQUIRED)

set(SRC_DFTTEST2_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-dfttest2")

# === Fatbin Generation ===
find_program(NVCC_EXECUTABLE nvcc HINTS "${CUDAToolkit_BIN_DIR}")
if(NOT NVCC_EXECUTABLE)
  message(FATAL_ERROR "nvcc executable not found in CUDA Toolkit bin directory.")
endif()

set(KERNELS_CU "${SRC_DFTTEST2_DIR}/nvrtc_source/kernels.cu")
set(FATBIN_OUT "${CMAKE_CURRENT_BINARY_DIR}/kernels.fatbin")
set(FATBIN_HEADER "${CMAKE_CURRENT_BINARY_DIR}/kernels_fatbin.h")

find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_command(
  OUTPUT "${FATBIN_HEADER}"
  COMMAND "${NVCC_EXECUTABLE}"
          -fatbin
          -O3
          --use_fast_math
          --threads 0
          -gencode arch=compute_75,code=sm_75
          -gencode arch=compute_80,code=sm_80
          -gencode arch=compute_86,code=sm_86
          -gencode arch=compute_89,code=sm_89
          -gencode arch=compute_90,code=sm_90
          -gencode arch=compute_120,code=sm_120
          -gencode arch=compute_75,code=compute_75
          "${KERNELS_CU}"
          -o "${FATBIN_OUT}"
  COMMAND "${Python3_EXECUTABLE}"
          "${CMAKE_CURRENT_SOURCE_DIR}/bin2c.py"
          "${FATBIN_OUT}"
          "${FATBIN_HEADER}"
          "kernels_fatbin"
  DEPENDS "${KERNELS_CU}" "${SRC_DFTTEST2_DIR}/nvrtc_source/dft_codelets.cuh"
  COMMENT "Compiling AOT CUDA kernels to Fatbin and embedding header..."
)

add_custom_target(generate_kernels_fatbin DEPENDS "${FATBIN_HEADER}")

# === Target Definition & Configuration ===
add_library(dfttest2_nvrtc MODULE "${SRC_DFTTEST2_DIR}/nvrtc_source/source.cpp")
add_dependencies(dfttest2_nvrtc generate_kernels_fatbin)

set_target_properties(
  dfttest2_nvrtc
  PROPERTIES CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON POSITION_INDEPENDENT_CODE ON
)

target_include_directories(
  dfttest2_nvrtc
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIR}" "${SRC_DFTTEST2_DIR}" "${CMAKE_CURRENT_BINARY_DIR}"
)

if(NOT PROJECT_VERSION_MAJOR)
  set(PROJECT_VERSION_MAJOR 1)
endif()
if(NOT PROJECT_VERSION_MINOR)
  set(PROJECT_VERSION_MINOR 0)
endif()

target_compile_definitions(
  dfttest2_nvrtc
  PRIVATE
    PLUGIN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PLUGIN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PLUGIN_VERSION_STRING="v${PROJECT_VERSION}"
)

target_link_libraries(dfttest2_nvrtc PRIVATE CUDA::cuda_driver)

if(MSVC)
  set_property(TARGET dfttest2_nvrtc PROPERTY MSVC_RUNTIME_LIBRARY "MultiThreaded")
  target_link_libraries(dfttest2_nvrtc PRIVATE ntdll)
endif()

if(UNIX)
  execute_process(
    COMMAND
      ${CMAKE_COMMAND} -E create_symlink "${CUDAToolkit_LIBRARY_DIR}/stubs/libcuda.so"
      "${CMAKE_CURRENT_BINARY_DIR}/libcuda.so.1"
  )

  target_link_directories(dfttest2_nvrtc PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
  target_link_libraries(dfttest2_nvrtc PRIVATE :libcuda.so.1)
  target_link_options(dfttest2_nvrtc PRIVATE "-Wl,--exclude-libs,ALL")
  set_target_properties(dfttest2_nvrtc PROPERTIES CXX_VISIBILITY_PRESET hidden VISIBILITY_INLINES_HIDDEN ON)
  set_target_properties(dfttest2_nvrtc PROPERTIES INSTALL_RPATH "$ORIGIN;$ORIGIN/../../../nvidia/cu13/lib")
endif()

add_custom_target(build_nvrtc ALL DEPENDS dfttest2_nvrtc)

# === Packaging & Installation ===
install(TARGETS dfttest2_nvrtc LIBRARY DESTINATION .)

if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\ndfttest2_nvrtc\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibdfttest2_nvrtc\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
