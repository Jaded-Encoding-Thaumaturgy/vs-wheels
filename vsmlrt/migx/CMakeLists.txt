cmake_minimum_required(VERSION 3.22)
project(VSMIGX_Package)

if(NOT CMAKE_SYSTEM_NAME MATCHES "Linux")
  message(FATAL_ERROR "vsmigx is only supported on Linux.")
endif()

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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
if(DEFINED ENV{ROCM_PATH})
  file(TO_CMAKE_PATH "$ENV{ROCM_PATH}" _ROCM_PATH)
else()
  set(_ROCM_PATH "/opt/rocm")
endif()

# Add ROCm path to CMake search prefix
list(APPEND CMAKE_PREFIX_PATH "${_ROCM_PATH}")

# MIGraphX is distributed as a ROCm Extras package with its own prefix.
if(DEFINED ENV{ROCM_EXTRAS_PATH})
  file(TO_CMAKE_PATH "$ENV{ROCM_EXTRAS_PATH}" _ROCM_EXTRAS_PATH)
  list(APPEND CMAKE_PREFIX_PATH "${_ROCM_EXTRAS_PATH}")
endif()

if(DEFINED ENV{MIGRAPHX_DIR})
  file(TO_CMAKE_PATH "$ENV{MIGRAPHX_DIR}" migraphx_DIR)
endif()

find_package(migraphx REQUIRED CONFIG)
find_package(hip REQUIRED CONFIG)

# === Target Definition & Configuration ===
add_library(vsmigx SHARED vs-mlrt/vsmigx/vs_migraphx.cpp vs-mlrt/vsmigx/win32.cpp)

set_target_properties(
  vsmigx
  PROPERTIES POSITION_INDEPENDENT_CODE ON CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

set_target_properties(vsmigx PROPERTIES INSTALL_RPATH "$ORIGIN")

target_include_directories(
  vsmigx
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIRECTORY}" "vs-mlrt/vsmigx"
  PUBLIC "${PROJECT_BINARY_DIR}"
)

# Generate config.h
configure_file(vs-mlrt/vsmigx/config.h.in config.h)

# === Link Libraries Setup ===
target_link_libraries(vsmigx PRIVATE migraphx::c hip::host)

# === Packaging & Installation ===
install(TARGETS vsmigx LIBRARY DESTINATION . RUNTIME DESTINATION .)
