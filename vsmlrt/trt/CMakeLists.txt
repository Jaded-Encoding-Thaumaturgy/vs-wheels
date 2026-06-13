cmake_minimum_required(VERSION 3.22)
project(VSTRT_Package)

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

# === TensorRT Version Detection ===
find_path(
  TENSORRT_INCLUDE_DIR
  NvInferVersion.h
  HINTS "${TENSORRT_HOME}/include" "$ENV{TENSORRT_HOME}/include"
  PATHS "/usr/include" "/usr/local/include"
)

if(TENSORRT_INCLUDE_DIR)
  get_filename_component(_TENSORRT_HOME "${TENSORRT_INCLUDE_DIR}" DIRECTORY)
  file(READ "${TENSORRT_INCLUDE_DIR}/NvInferVersion.h" _VERSION_CONTENT)
  if(_VERSION_CONTENT MATCHES "#define TRT_MAJOR_ENTERPRISE ([0-9]+)")
    set(TRT_MAJOR "${CMAKE_MATCH_1}")
  endif()
  if(_VERSION_CONTENT MATCHES "#define TRT_MINOR_ENTERPRISE ([0-9]+)")
    set(TRT_MINOR "${CMAKE_MATCH_1}")
  endif()
endif()

if(NOT DEFINED TRT_MAJOR OR NOT DEFINED TRT_MINOR)
  message(
    FATAL_ERROR
    "Could not find or parse TensorRT version from NvInferVersion.h (TENSORRT_HOME: ${TENSORRT_HOME}, ENV: $ENV{TENSORRT_HOME})"
  )
endif()

message(STATUS "TensorRT Version inferred: ${TRT_MAJOR}.${TRT_MINOR}")

set(TENSORRT_LIBRARY_SUFFIX "" CACHE STRING "TensorRT library suffix")
if(WIN32 AND NOT TENSORRT_LIBRARY_SUFFIX)
  set(TENSORRT_LIBRARY_SUFFIX "_${TRT_MAJOR}")
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
add_library(vstrt SHARED vs-mlrt/vstrt/vs_tensorrt.cpp "${PATCHED_WIN32}")

set_target_properties(
  vstrt
  PROPERTIES POSITION_INDEPENDENT_CODE ON CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

if(UNIX)
  if(APPLE)
    set_target_properties(vstrt PROPERTIES INSTALL_RPATH "@loader_path")
  else()
    set_target_properties(vstrt PROPERTIES INSTALL_RPATH "$ORIGIN/../../../tensorrt_libs")
  endif()
endif()

target_include_directories(
  vstrt
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIRECTORY}" "vs-mlrt/vstrt" "vs-mlrt/common" ${CUDAToolkit_INCLUDE_DIRS}
  PUBLIC "${PROJECT_BINARY_DIR}"
)

target_compile_definitions(vstrt PRIVATE USE_NVINFER_PLUGIN)

configure_file(vs-mlrt/vstrt/config.h.in config.h)

# === Link Libraries Setup ===
target_link_libraries(vstrt PRIVATE "nvinfer${TENSORRT_LIBRARY_SUFFIX}" CUDA::cudart_static)

if(MSVC)
  target_link_options(vstrt PRIVATE "/DELAYLOAD:nvinfer${TENSORRT_LIBRARY_SUFFIX}.dll" "delayimp.lib")
endif()

# Configure TensorRT home directory & paths
if(DEFINED ENV{TENSORRT_HOME})
  file(TO_CMAKE_PATH "$ENV{TENSORRT_HOME}" _TENSORRT_HOME)
  target_include_directories(vstrt PRIVATE "${_TENSORRT_HOME}/include")
  target_link_directories(vstrt PRIVATE "${_TENSORRT_HOME}/lib")
  message(STATUS "Using TENSORRT_HOME: ${_TENSORRT_HOME}")
else()
  message(WARNING "TENSORRT_HOME not set")
endif()

target_link_libraries(vstrt PRIVATE "nvinfer_plugin${TENSORRT_LIBRARY_SUFFIX}")
if(MSVC)
  target_link_options(vstrt PRIVATE "/DELAYLOAD:nvinfer_plugin${TENSORRT_LIBRARY_SUFFIX}.dll")
endif()

# === Packaging & Installation ===
install(TARGETS vstrt LIBRARY DESTINATION . RUNTIME DESTINATION .)

# Write VapourSynth Manifest
if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nvstrt\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibvstrt\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
