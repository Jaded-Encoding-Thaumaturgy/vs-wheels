cmake_minimum_required(VERSION 3.22)
project(VSTRT_RTX_Package)

# === Apply patches ===
include("${CMAKE_CURRENT_SOURCE_DIR}/ApplyPatch.cmake")

set(SRC_VSTRT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-mlrt")
set(BIN_VSTRT_DIR "${CMAKE_CURRENT_BINARY_DIR}/vs-mlrt")

add_patched_source(
  PATCHED_WIN32
  "${SRC_VSTRT_DIR}/vstrt/win32.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/patches/nvidia-wheel-paths.patch"
)

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# === TensorRT RTX Version Detection ===
find_path(
  TENSORRT_RTX_INCLUDE_DIR
  NvInferVersion.h
  HINTS "${TENSORRT_RTX_HOME}/include" "$ENV{TENSORRT_RTX_HOME}/include"
  PATHS "/usr/include" "/usr/local/include"
)

if(TENSORRT_RTX_INCLUDE_DIR)
  get_filename_component(_TENSORRT_RTX_HOME "${TENSORRT_RTX_INCLUDE_DIR}" DIRECTORY)
  file(READ "${TENSORRT_RTX_INCLUDE_DIR}/NvInferVersion.h" _VERSION_CONTENT)
  if(_VERSION_CONTENT MATCHES "#define TRT_MAJOR_RTX ([0-9]+)")
    set(TRT_MAJOR_RTX "${CMAKE_MATCH_1}")
  endif()
  if(_VERSION_CONTENT MATCHES "#define TRT_MINOR_RTX ([0-9]+)")
    set(TRT_MINOR_RTX "${CMAKE_MATCH_1}")
  endif()
endif()

if(NOT DEFINED TRT_MAJOR_RTX OR NOT DEFINED TRT_MINOR_RTX)
  message(
    FATAL_ERROR
    "Could not find or parse TensorRT RTX version from NvInferVersion.h (TENSORRT_RTX_HOME: ${TENSORRT_RTX_HOME}, ENV: $ENV{TENSORRT_RTX_HOME})"
  )
endif()

message(STATUS "TensorRT RTX Version inferred: ${TRT_MAJOR_RTX}.${TRT_MINOR_RTX}")

set(TENSORRT_RTX_LIBRARY_SUFFIX "" CACHE STRING "TensorRT library suffix")
if(WIN32 AND NOT TENSORRT_RTX_LIBRARY_SUFFIX)
  set(TENSORRT_RTX_LIBRARY_SUFFIX "_${TRT_MAJOR_RTX}_${TRT_MINOR_RTX}")
endif()

set(
  VAPOURSYNTH_INCLUDE_DIRECTORY
  "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include"
  CACHE PATH
  "Path to VapourSynth headers"
)

if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

# === Dependencies ===
find_package(CUDAToolkit REQUIRED)

# === Target Definition & Configuration ===
add_library(vstrt_rtx SHARED vs-mlrt/vstrt/vs_tensorrt.cpp "${PATCHED_WIN32}")

set_target_properties(
  vstrt_rtx
  PROPERTIES POSITION_INDEPENDENT_CODE ON CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

if(UNIX)
  if(APPLE)
    set_target_properties(vstrt_rtx PROPERTIES INSTALL_RPATH "@loader_path")
  else()
    set_target_properties(vstrt_rtx PROPERTIES INSTALL_RPATH "$ORIGIN/../../../tensorrt_rtx_libs")
  endif()
endif()

target_include_directories(
  vstrt_rtx
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIRECTORY}" "vs-mlrt/vstrt" "vs-mlrt/common" ${CUDAToolkit_INCLUDE_DIRS}
  PUBLIC "${PROJECT_BINARY_DIR}"
)

target_compile_definitions(
  vstrt_rtx
  PRIVATE USE_NVINFER_PLUGIN TRT_MAJOR_RTX=${TRT_MAJOR_RTX} TRT_MINOR_RTX=${TRT_MINOR_RTX}
)

configure_file(vs-mlrt/vstrt/config.h.in config.h)

# === Link Libraries Setup ===
target_link_libraries(vstrt_rtx PRIVATE CUDA::cudart_static)

# Configure TensorRT RTX home directory & paths
target_include_directories(vstrt_rtx PRIVATE "${_TENSORRT_RTX_HOME}/include")
target_link_directories(vstrt_rtx PRIVATE "${_TENSORRT_RTX_HOME}/lib")
message(STATUS "Using TENSORRT_RTX_HOME: ${_TENSORRT_RTX_HOME}")

if(WIN32)
  target_link_libraries(vstrt_rtx PRIVATE "tensorrt_rtx${TENSORRT_RTX_LIBRARY_SUFFIX}")
  if(MSVC)
    target_link_options(vstrt_rtx PRIVATE "/DELAYLOAD:tensorrt_rtx${TENSORRT_RTX_LIBRARY_SUFFIX}.dll" "delayimp.lib")
  endif()
else()
  target_link_libraries(vstrt_rtx PRIVATE tensorrt_rtx)
endif()

# === Packaging & Installation ===
install(TARGETS vstrt_rtx LIBRARY DESTINATION . RUNTIME DESTINATION .)

# Write VapourSynth Manifest
if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nvstrt_rtx\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibvstrt_rtx\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
