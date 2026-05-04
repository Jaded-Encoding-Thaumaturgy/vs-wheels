cmake_minimum_required(VERSION 3.22)
project(DFTTEST2_CUDA_Package)

# Define the include path relative to this wrapper
set(VS_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

# Fix version detection
if(SKBUILD_PROJECT_VERSION)
  set(VCS_TAG "v${SKBUILD_PROJECT_VERSION}" CACHE STRING "Version from scikit-build-core")
  set(CMAKE_DISABLE_FIND_PACKAGE_Git ON)
endif()

set(ENABLE_CUDA ON CACHE BOOL "" FORCE)
set(USE_NVRTC_STATIC ON CACHE BOOL "" FORCE)
set(ENABLE_CPU OFF CACHE BOOL "" FORCE)
set(ENABLE_GCC OFF CACHE BOOL "" FORCE)
set(ENABLE_HIP OFF CACHE BOOL "" FORCE)

# Add the submodule but skip its internal install rules
add_subdirectory(vs-dfttest2 EXCLUDE_FROM_ALL)

if(WIN32 AND ENABLE_CUDA)
  find_package(CUDAToolkit QUIET)
  file(GLOB CUFFT_DLL "${CUDAToolkit_BIN_DIR}/x64/cufft64_*.dll")

  if(CUFFT_DLL)
    message(STATUS "Found cuFFT DLL: ${CUFFT_DLL}")
    install(FILES ${CUFFT_DLL} DESTINATION vsmlrt-cuda)
  else()
    message(WARNING "No cuFFT DLL found in ${CUDAToolkit_BIN_DIR}/x64")
  endif()
endif()

add_custom_target(build_cuda ALL DEPENDS dfttest2_cuda)

if(WIN32 AND CUFFT_DLL)
  add_custom_command(
    TARGET build_cuda
    POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E make_directory $<TARGET_FILE_DIR:dfttest2_cuda>/vsmlrt-cuda
    COMMAND ${CMAKE_COMMAND} -E copy_if_different ${CUFFT_DLL} $<TARGET_FILE_DIR:dfttest2_cuda>/vsmlrt-cuda
    COMMENT "Copying cuFFT DLL to vsmlrt-cuda subdirectory"
  )
endif()

install(TARGETS dfttest2_cuda LIBRARY DESTINATION .)
install(FILES "manifest.vs" DESTINATION .)
