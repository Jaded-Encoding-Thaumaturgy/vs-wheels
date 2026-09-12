cmake_minimum_required(VERSION 3.22)

if(NOT DEFINED SKBUILD_PROJECT_VERSION)
  set(SKBUILD_PROJECT_VERSION "0.0.0")
endif()

project(DFTTEST2_HIP_Package VERSION "${SKBUILD_PROJECT_VERSION}" LANGUAGES CXX)

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

find_package(hip REQUIRED config)
find_package(hipfft REQUIRED config)
find_package(hiprtc REQUIRED config)

set(SRC_DFTTEST2_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vs-dfttest2")

add_library(dfttest2_hip MODULE "${SRC_DFTTEST2_DIR}/hip_source/source.cpp")

set_target_properties(
  dfttest2_hip
  PROPERTIES CXX_EXTENSIONS OFF CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON POSITION_INDEPENDENT_CODE ON
)

target_include_directories(
  dfttest2_hip
  PRIVATE "${VAPOURSYNTH_INCLUDE_DIR}" "${SRC_DFTTEST2_DIR}" "${CMAKE_CURRENT_BINARY_DIR}"
)

if(NOT PROJECT_VERSION_MAJOR)
  set(PROJECT_VERSION_MAJOR 1)
endif()
if(NOT PROJECT_VERSION_MINOR)
  set(PROJECT_VERSION_MINOR 0)
endif()

target_compile_definitions(
  dfttest2_hip
  PRIVATE
    PLUGIN_VERSION_MAJOR=${PROJECT_VERSION_MAJOR}
    PLUGIN_VERSION_MINOR=${PROJECT_VERSION_MINOR}
    PLUGIN_VERSION_STRING="v${PROJECT_VERSION}"
)

target_link_libraries(dfttest2_hip PRIVATE hip::host hip::hipfft hiprtc::hiprtc)

add_custom_target(build_hip ALL DEPENDS dfttest2_hip)

# === Packaging & Installation ===
if(WIN32)
  file(TO_CMAKE_PATH "$ENV{HIP_PATH}" HIP_ROOT_DIR)
  if(NOT HIP_ROOT_DIR)
    file(TO_CMAKE_PATH "$ENV{ROCM_PATH}" HIP_ROOT_DIR)
  endif()

  if(HIP_ROOT_DIR)
    set(HIP_BIN_DIR "${HIP_ROOT_DIR}/bin")

    file(
      GLOB HIP_DLLS
      "${HIP_BIN_DIR}/amdhip64_*.dll"
      "${HIP_BIN_DIR}/amd_comgr[0-9]*.dll"
      "${HIP_BIN_DIR}/amd_comgr.dll"
      "${HIP_BIN_DIR}/hipfft.dll"
      "${HIP_BIN_DIR}/hiprtc[0-9]*.dll"
      "${HIP_BIN_DIR}/hiprtc-builtins*.dll"
      "${HIP_BIN_DIR}/rocfft.dll"
      "${HIP_BIN_DIR}/rocm_kpack.dll"
    )

    if(HIP_DLLS)
      message(STATUS "Found HIP/ROCm DLLs: ${HIP_DLLS}")
      install(FILES ${HIP_DLLS} DESTINATION .)

      add_custom_command(
        TARGET build_hip
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:dfttest2_hip>
        COMMAND ${CMAKE_COMMAND} -E copy_if_different ${HIP_DLLS} $<TARGET_FILE_DIR:dfttest2_hip>
        COMMENT "Copying HIP/ROCm DLLs"
      )
    else()
      message(WARNING "No HIP/ROCm DLLs found in ${HIP_BIN_DIR}")
    endif()
  endif()
endif()

install(TARGETS dfttest2_hip LIBRARY DESTINATION .)

if(WIN32)
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\ndfttest2_hip\n")
else()
  file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" "[VapourSynth Manifest V1]\nlibdfttest2_hip\n")
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/manifest.vs" DESTINATION .)
