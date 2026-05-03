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
