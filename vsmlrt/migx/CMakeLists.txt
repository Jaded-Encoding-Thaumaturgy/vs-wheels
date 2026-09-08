cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED SKBUILD_PROJECT_VERSION)
  set(SKBUILD_PROJECT_VERSION "0.0.0")
endif()

project(VSMIGX_Package VERSION "${SKBUILD_PROJECT_VERSION}" LANGUAGES CXX)

if(NOT CMAKE_SYSTEM_NAME MATCHES "Linux")
  message(FATAL_ERROR "vsmigx is only supported on Linux.")
endif()

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIR}" "vs-mlrt/vsmigx"
)

target_compile_definitions(
  vsmigx
  PRIVATE
    PLUGIN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PLUGIN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PLUGIN_VERSION_STRING="v${PROJECT_VERSION}"
)

# === Link Libraries Setup ===
target_link_libraries(vsmigx PRIVATE migraphx::c hip::host)

# === Packaging & Installation ===
install(TARGETS vsmigx LIBRARY DESTINATION . RUNTIME DESTINATION .)
