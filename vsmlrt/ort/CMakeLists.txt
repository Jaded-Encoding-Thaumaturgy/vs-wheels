cmake_minimum_required(VERSION 3.22)
project(VSORT_Package)

# === Apply patches ===
include("${CMAKE_CURRENT_SOURCE_DIR}/ApplyPatch.cmake")

set(SRC_VSORT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-mlrt")
set(BIN_VSORT_DIR "${CMAKE_CURRENT_BINARY_DIR}/vs-mlrt")

add_patched_source(
  PATCHED_WIN32
  "${SRC_VSORT_DIR}/vsort/win32.cpp"
  "${CMAKE_CURRENT_SOURCE_DIR}/patches/nvidia-wheel-paths.patch"
)

# === C++ Standard & Options ===
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Options
set(ENABLE_CUDA OFF CACHE BOOL "Enable CUDA backend")
set(ENABLE_DML OFF CACHE BOOL "Enable DirectML backend")
set(ENABLE_COREML OFF CACHE BOOL "Enable CoreML support")

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
find_package(Protobuf REQUIRED CONFIG)
find_package(ONNX REQUIRED)
find_package(onnxruntime REQUIRED)

if(ENABLE_CUDA)
  find_package(CUDAToolkit REQUIRED)
endif()

# === Target Definition & Configuration ===
add_library(
  vsort
  SHARED
  vs-mlrt/vsort/vs_onnxruntime.cpp
  "${PATCHED_WIN32}"
  vs-mlrt/common/onnx_utils.cpp
  vs-mlrt/common/convert_float_to_float16.cpp
)

set_target_properties(
  vsort
  PROPERTIES POSITION_INDEPENDENT_CODE ON CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

if(UNIX)
  if(APPLE)
    set_target_properties(vsort PROPERTIES INSTALL_RPATH "@loader_path")
  else()
    if(ENABLE_CUDA)
      set_target_properties(
        vsort
        PROPERTIES INSTALL_RPATH "$ORIGIN;$ORIGIN/../../../nvidia/cu13/lib;$ORIGIN/../../../nvidia/cudnn/lib"
      )
    else()
      set_target_properties(vsort PROPERTIES INSTALL_RPATH "$ORIGIN")
    endif()
  endif()
endif()

target_include_directories(
  vsort
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIRECTORY}" "vs-mlrt/vsort" "vs-mlrt/common"
  PUBLIC "${PROJECT_BINARY_DIR}"
)

if(ENABLE_CUDA)
  target_compile_definitions(vsort PRIVATE ENABLE_CUDA)
  target_include_directories(vsort PRIVATE ${CUDAToolkit_INCLUDE_DIRS})
endif()

if(ENABLE_DML)
  target_compile_definitions(vsort PRIVATE ENABLE_DML)
endif()

if(ENABLE_COREML)
  target_compile_definitions(vsort PRIVATE ENABLE_COREML=1)
endif()

configure_file(vs-mlrt/vsort/config.h.in config.h)

# === Link Libraries Setup ===
target_link_libraries(vsort PRIVATE ONNX::onnx onnxruntime::onnxruntime)

if(MSVC)
  target_link_options(vsort PRIVATE "/DELAYLOAD:onnxruntime.dll" "delayimp.lib")
endif()

if(ENABLE_CUDA)
  target_link_libraries(vsort PRIVATE CUDA::cudart_static)
endif()

# === Packaging & Installation ===
install(TARGETS vsort LIBRARY DESTINATION . RUNTIME DESTINATION .)

# Helper runtime DLL/SO copying/installing logic
if(WIN32)
  # Copy ONNX Runtime
  get_filename_component(_ROOT "${onnxruntime_DIR}/../../.." ABSOLUTE)
  file(GLOB _DLLS "${_ROOT}/bin/*.dll")
  # Copy CUDA providers DLL if CUDA is enabled
  if(ENABLE_CUDA)
    file(GLOB _LIB_DLLS "${_ROOT}/lib/*.dll")
    list(APPEND _DLLS ${_LIB_DLLS})
  endif()

  if(_DLLS)
    install(FILES ${_DLLS} DESTINATION "vsort")
  else()
    message(WARNING "Could not find ONNX Runtime DLLs")
  endif()

  if(ENABLE_DML)
    if(NOT DML_DIR AND DEFINED ENV{DML_DIR})
      set(DML_DIR "$ENV{DML_DIR}")
    endif()

    if(DML_DIR)
      file(TO_CMAKE_PATH "${DML_DIR}" _DML_DIR)
      find_file(_DML NAMES DirectML.dll PATHS "${_DML_DIR}/bin/x64-win" NO_DEFAULT_PATH)
    endif()

    if(_DML)
      install(FILES "${_DML}" DESTINATION "vsort")
    else()
      message(WARNING "Could not find DirectML DLL. DML_DIR='${DML_DIR}'")
    endif()
  endif()
endif()

if(UNIX AND NOT APPLE AND ENABLE_CUDA)
  get_filename_component(_ROOT "${onnxruntime_DIR}/../../.." ABSOLUTE)

  # Glob candidate libraries to bundle
  file(
    GLOB _LINUX_LIBS_PATHS
    # ONNX Runtime provider libraries
    "${_ROOT}/lib/libonnxruntime*.so*"
    "${_ROOT}/lib64/libonnxruntime*.so*"
  )

  if(_LINUX_LIBS_PATHS)
    list(REMOVE_DUPLICATES _LINUX_LIBS_PATHS)
    foreach(_LIB_PATH IN LISTS _LINUX_LIBS_PATHS)
      get_filename_component(_LIB_NAME "${_LIB_PATH}" NAME)
      get_filename_component(_REAL_PATH "${_LIB_PATH}" REALPATH)

      # Check if the filename ends in ".so"
      get_filename_component(_LIB_EXT "${_LIB_NAME}" EXT)
      if("${_LIB_EXT}" STREQUAL ".so")
        set(_ENDS_IN_SO ON)
      else()
        set(_ENDS_IN_SO OFF)
      endif()

      # Determine if we should bundle this library:
      # - Symlinks (which represent the SONAME) that have a version suffix (e.g. libcublas.so.13)
      # - Real files that are unversioned and end in .so (e.g. libonnxruntime_providers_cuda.so)
      get_filename_component(_REAL_NAME "${_REAL_PATH}" NAME)
      set(_SHOULD_BUNDLE OFF)
      if(NOT "${_LIB_NAME}" STREQUAL "${_REAL_NAME}")
        if(NOT _ENDS_IN_SO)
          set(_SHOULD_BUNDLE ON)
        endif()
      else()
        if(_ENDS_IN_SO)
          set(_SHOULD_BUNDLE ON)
        endif()
      endif()

      if(_SHOULD_BUNDLE)
        message(STATUS "Bundling: ${_REAL_PATH} as ${_LIB_NAME}")
        install(FILES "${_REAL_PATH}" RENAME "${_LIB_NAME}" DESTINATION .)
      endif()
    endforeach()
  else()
    message(WARNING "Could not find any Linux ORT libraries to bundle")
  endif()
endif()

# Write VapourSynth Manifest
if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nvsort\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibvsort\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
