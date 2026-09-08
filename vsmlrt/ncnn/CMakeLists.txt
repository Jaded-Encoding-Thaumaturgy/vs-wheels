cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED SKBUILD_PROJECT_VERSION)
  set(SKBUILD_PROJECT_VERSION "0.0.0")
endif()

project(VSNCNN_Package VERSION "${SKBUILD_PROJECT_VERSION}" LANGUAGES CXX)

set(SRC_VSNCNN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-mlrt")

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
find_package(ncnn REQUIRED)
find_package(Protobuf REQUIRED CONFIG)
find_package(ONNX REQUIRED)
find_package(Vulkan REQUIRED)

# === Target Definition & Configuration ===
add_library(
  vsncnn SHARED
  "${SRC_VSNCNN_DIR}/vsncnn/vs_ncnn.cpp"
  "${SRC_VSNCNN_DIR}/vsncnn/onnx2ncnn.cpp"
  "${SRC_VSNCNN_DIR}/common/onnx_utils.cpp"
)

set_target_properties(
  vsncnn
  PROPERTIES POSITION_INDEPENDENT_CODE ON CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

if(UNIX)
  if(APPLE)
    set_target_properties(vsncnn PROPERTIES INSTALL_RPATH "@loader_path;/opt/homebrew/lib;/usr/local/lib")
  else()
    set_target_properties(vsncnn PROPERTIES INSTALL_RPATH "$ORIGIN")
  endif()
endif()

target_include_directories(
  vsncnn
  PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/vs-mlrt/vsncnn"
    "${CMAKE_CURRENT_SOURCE_DIR}/vs-mlrt/common"
    "${VAPOURSYNTH_INCLUDE_DIR}"
)

target_compile_definitions(
  vsncnn
  PRIVATE
    PLUGIN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PLUGIN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PLUGIN_VERSION_STRING="v${PROJECT_VERSION}"
)

# === Link Libraries Setup ===
target_link_libraries(vsncnn PRIVATE ncnn ONNX::onnx Vulkan::Vulkan)

if(APPLE)
  target_link_libraries(
    vsncnn
    PRIVATE
      "-framework Metal"
      "-framework Foundation"
      "-framework QuartzCore"
      "-framework CoreGraphics"
      "-framework IOSurface"
      "-framework AppKit"
      "-framework IOKit"
  )
endif()

# === Packaging & Installation ===
install(TARGETS vsncnn LIBRARY DESTINATION . RUNTIME DESTINATION .)
