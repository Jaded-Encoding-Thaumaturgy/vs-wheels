cmake_minimum_required(VERSION 4.0)
project(DFTTEST2_HIP_Package)

# === C++ Standard & Options ===
set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

set(ENABLE_CUDA OFF CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC OFF CACHE BOOL "" FORCE)
set(ENABLE_HIP ON CACHE BOOL "" FORCE)

# === Target Definition & Configuration ===
# Add the submodule but skip its internal install rules
add_subdirectory(vs-dfttest2 EXCLUDE_FROM_ALL)

add_custom_target(build_hip ALL DEPENDS dfttest2_hip)

# === Packaging & Installation ===
if(WIN32 AND ENABLE_HIP)
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
      "${HIP_BIN_DIR}/hipfft.dll"
      "${HIP_BIN_DIR}/hiprtc[0-9]*.dll"
      "${HIP_BIN_DIR}/hiprtc-builtins*.dll"
      "${HIP_BIN_DIR}/rocfft.dll"
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
