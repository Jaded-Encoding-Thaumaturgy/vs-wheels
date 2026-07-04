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
    set(HIP_DLL_SEARCH_DIRS "${HIP_ROOT_DIR}/bin")
    foreach(HIP_PREFIX_PATH IN LISTS CMAKE_PREFIX_PATH)
      list(APPEND HIP_DLL_SEARCH_DIRS "${HIP_PREFIX_PATH}/bin")
    endforeach()
    if(DEFINED ENV{CMAKE_PREFIX_PATH})
      cmake_path(CONVERT "$ENV{CMAKE_PREFIX_PATH}" TO_CMAKE_PATH_LIST HIP_ENV_PREFIX_PATHS)
      foreach(HIP_PREFIX_PATH IN LISTS HIP_ENV_PREFIX_PATHS)
        list(APPEND HIP_DLL_SEARCH_DIRS "${HIP_PREFIX_PATH}/bin")
      endforeach()
    endif()
    list(REMOVE_DUPLICATES HIP_DLL_SEARCH_DIRS)

    foreach(HIP_BIN_DIR IN LISTS HIP_DLL_SEARCH_DIRS)
      file(
        GLOB FOUND_HIP_DLLS
        "${HIP_BIN_DIR}/amdhip64_*.dll"
        "${HIP_BIN_DIR}/amd_comgr[0-9]*.dll"
        "${HIP_BIN_DIR}/hipfft.dll"
        "${HIP_BIN_DIR}/hiprtc[0-9]*.dll"
        "${HIP_BIN_DIR}/hiprtc-builtins*.dll"
        "${HIP_BIN_DIR}/rocfft.dll"
      )
      list(APPEND HIP_DLLS ${FOUND_HIP_DLLS})
    endforeach()
    list(REMOVE_DUPLICATES HIP_DLLS)

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
      message(WARNING "No HIP/ROCm DLLs found in ${HIP_DLL_SEARCH_DIRS}")
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
