cmake_minimum_required(VERSION 3.20)
project(BM3DCPU_Distribution VERSION 2.6 LANGUAGES CXX)

set(VAPOURSYNTH_INCLUDE_DIRECTORY "vapoursynth/include" CACHE PATH "Path to VapourSynth headers")

option(BM3D_MULTI_TARGET "Build multiple optimized binaries for distribution" OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(SOURCE_FILE "VapourSynth-BM3DCUDA/cpu_source/source.cpp")
set(SOURCE_DIR "VapourSynth-BM3DCUDA/cpu_source")

function(apply_bm3d_compile_options TARGET_NAME MTUNE EXTRA_FLAGS)
  # Case 1: GCC or Clang (Any Platform)
  # Uses standard Unix-style optimization flags.
  if((CMAKE_CXX_COMPILER_ID STREQUAL "GNU") OR (CMAKE_CXX_COMPILER_ID MATCHES "^(Apple)?Clang$"))
    target_compile_options(${TARGET_NAME} PRIVATE "-march=x86-64-v3" "-mtune=${MTUNE}" ${EXTRA_FLAGS} "-ffast-math")

    # Case 2: Intel/IntelLLVM AND Linux
    # On Linux, Intel compilers typically use GCC-compatible -march/-mtune syntax.
  elseif(
    ((CMAKE_CXX_COMPILER_ID STREQUAL "Intel") OR (CMAKE_CXX_COMPILER_ID STREQUAL "IntelLLVM"))
    AND (CMAKE_SYSTEM_NAME STREQUAL "Linux")
  )
    target_compile_options(${TARGET_NAME} PRIVATE "-march=core-avx2" "-mtune=${MTUNE}")

    # Case 3: MSVC OR (Intel/IntelLLVM AND Windows)
    # On Windows, Intel compilers (icx/icl) usually follow MSVC-style /arch flag syntax.
  elseif(
    (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    OR
      (
        ((CMAKE_CXX_COMPILER_ID STREQUAL "Intel") OR (CMAKE_CXX_COMPILER_ID STREQUAL "IntelLLVM"))
        AND (CMAKE_SYSTEM_NAME STREQUAL "Windows")
      )
  )
    target_compile_options(${TARGET_NAME} PRIVATE "/arch:AVX2")
  endif()
endfunction()

if(BM3D_MULTI_TARGET)
  file(READ "arch_configs.json" JSON_DATA)
  string(JSON CONFIG_COUNT LENGTH "${JSON_DATA}")
  math(EXPR CONFIG_MAX "${CONFIG_COUNT} - 1")

  foreach(I RANGE ${CONFIG_MAX})
    string(JSON CONFIG GET "${JSON_DATA}" ${I})
    string(JSON SUFFIX GET "${CONFIG}" "suffix")
    string(JSON MTUNE GET "${CONFIG}" "mtune")
    string(JSON EXTRA_FLAGS GET "${CONFIG}" "extra_flags")

    set(TARGET_NAME "bm3dcpu_${SUFFIX}")
    add_library(${TARGET_NAME} SHARED ${SOURCE_FILE})
    target_include_directories(${TARGET_NAME} PRIVATE ${VAPOURSYNTH_INCLUDE_DIRECTORY})

    apply_bm3d_compile_options(${TARGET_NAME} "${MTUNE}" "${EXTRA_FLAGS}")

    set_target_properties(${TARGET_NAME} PROPERTIES OUTPUT_NAME "bm3dcpu${SUFFIX}")

    install(TARGETS ${TARGET_NAME} DESTINATION .)
  endforeach()

  install(FILES "manifest.vs" DESTINATION .)

else()
  add_library(bm3dcpu SHARED ${SOURCE_FILE})
  target_include_directories(bm3dcpu PRIVATE ${VAPOURSYNTH_INCLUDE_DIRECTORY})

  apply_bm3d_compile_options(bm3dcpu "native" "")

  install(TARGETS bm3dcpu DESTINATION .)
endif()
