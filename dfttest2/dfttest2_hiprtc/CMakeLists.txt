cmake_minimum_required(VERSION 3.50.0)
project(DFTTEST2_HIPRTC_Package)

# Define the include path relative to this wrapper
set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

# Fix version detection
if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

set(ENABLE_CUDA OFF CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC OFF CACHE BOOL "" FORCE)
set(ENABLE_HIP ON CACHE BOOL "" FORCE)

# Add the submodule but skip its internal install rules
add_subdirectory(vs-dfttest2 EXCLUDE_FROM_ALL)

if(WIN32 AND ENABLE_HIP)
  file(TO_CMAKE_PATH "$ENV{HIP_PATH}" HIP_ROOT_DIR)
  if(NOT HIP_ROOT_DIR)
    file(TO_CMAKE_PATH "$ENV{ROCM_PATH}" HIP_ROOT_DIR)
  endif()

  if(HIP_ROOT_DIR)
    set(HIP_BIN_DIR "${HIP_ROOT_DIR}/bin")
    file(GLOB HIP_DLLS 
      "${HIP_BIN_DIR}/amdhip64_*.dll"
      "${HIP_BIN_DIR}/hipfft.dll"
      "${HIP_BIN_DIR}/hiprtc[0-9]*.dll"
    )

    if(HIP_DLLS)
      message(STATUS "Found HIP/ROCm DLLs: ${HIP_DLLS}")
      install(FILES ${HIP_DLLS} DESTINATION .)
    else()
      message(WARNING "No HIP/ROCm DLLs found in ${HIP_BIN_DIR}")
    endif()
  endif()
endif()

add_custom_target(build_hiprtc ALL DEPENDS dfttest2_hiprtc)

if(WIN32 AND HIP_DLLS)
  add_custom_command(
    TARGET build_hiprtc
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:dfttest2_hiprtc>
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${HIP_DLLS} $<TARGET_FILE_DIR:dfttest2_hiprtc>
    COMMENT "Copying HIP/ROCm DLLs"
  )
endif()

install(TARGETS dfttest2_hiprtc LIBRARY DESTINATION .)
install(FILES "manifest.vs" DESTINATION .)
