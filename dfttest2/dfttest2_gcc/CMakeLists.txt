cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED SKBUILD_PROJECT_VERSION)
  set(SKBUILD_PROJECT_VERSION "0.0.0")
endif()

project(DFTTEST2_GCC_Package VERSION "${SKBUILD_PROJECT_VERSION}" LANGUAGES CXX)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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

find_package(Threads REQUIRED)

set(SRC_DFTTEST2_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-dfttest2")

add_library(
  dfttest2_gcc
  MODULE
  "${SRC_DFTTEST2_DIR}/gcc_source/source.cpp"
  "${SRC_DFTTEST2_DIR}/gcc_source/getframe_impl.cpp"
)

set_target_properties(
  dfttest2_gcc
  PROPERTIES CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON
)

target_include_directories(
  dfttest2_gcc
  PRIVATE "${SRC_DFTTEST2_DIR}/gcc_source" "${VAPOURSYNTH_INCLUDE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}"
)

if(NOT PROJECT_VERSION_MAJOR)
  set(PROJECT_VERSION_MAJOR 1)
endif()
if(NOT PROJECT_VERSION_MINOR)
  set(PROJECT_VERSION_MINOR 0)
endif()

target_compile_definitions(
  dfttest2_gcc
  PRIVATE
    PLUGIN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PLUGIN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PLUGIN_VERSION_STRING="v${PROJECT_VERSION}"
)

target_link_libraries(dfttest2_gcc PRIVATE Threads::Threads)

add_custom_target(build_gcc ALL DEPENDS dfttest2_gcc)

install(TARGETS dfttest2_gcc LIBRARY DESTINATION .)

if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\ndfttest2_gcc\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibdfttest2_gcc\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
