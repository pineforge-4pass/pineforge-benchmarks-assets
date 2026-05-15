# benchmarks/assets/strategies/CMakeLists.txt — build one .dylib/.so per bench strategy.
#
# Enabled by the top-level option PINEFORGE_BUILD_BENCH_STRATEGIES (default OFF).
# Wire-in from the engine root CMakeLists.txt:
#
#   option(PINEFORGE_BUILD_BENCH_STRATEGIES
#       "Build benchmarks bench strategies (.dylib/.so per strategy)" OFF)
#   if(PINEFORGE_BUILD_BENCH_STRATEGIES)
#       add_subdirectory(benchmarks/assets/strategies)
#   endif()
#
# Prerequisites:
#   - All strategies must have generated.cpp already present (no codegen invoked here).
#   - The `pineforge` static library target must exist before this subdirectory is added.
#
# Each strategy.dylib / strategy.so is placed next to its generated.cpp (i.e.
# inside the strategy directory alongside strategy.pine, pineforge_trades.csv, etc.)
# so that scripts/run_strategy.py can discover it by conventional path.
#
# Build all bench strategies in one command:
#   cmake --build build --target bench_strategies -j

file(GLOB STRATEGY_DIRS RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
     ${CMAKE_CURRENT_SOURCE_DIR}/[0-9]*)

set(_n_bench 0)

foreach(STRAT_REL IN LISTS STRATEGY_DIRS)
    set(STRAT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${STRAT_REL})
    if(NOT IS_DIRECTORY ${STRAT_DIR})
        continue()
    endif()
    set(STRAT_CPP ${STRAT_DIR}/generated.cpp)
    if(NOT EXISTS ${STRAT_CPP})
        continue()
    endif()

    # Derive a unique CMake target name from the relative path.
    # e.g. "01-sma-cross" -> "bench_strategy_01_sma_cross"
    string(REPLACE "-" "_" TARGET_NAME ${STRAT_REL})
    set(TARGET_NAME "bench_strategy_${TARGET_NAME}")
    string(MAKE_C_IDENTIFIER ${TARGET_NAME} TARGET_NAME)

    add_library(${TARGET_NAME} SHARED ${STRAT_CPP})

    target_link_libraries(${TARGET_NAME} PRIVATE pineforge)

    # Force-load libpineforge so all C-ABI symbols (pf_version_get,
    # strategy_set_trace_enabled, etc.) that scripts/run_strategy.py
    # expects via dlsym are present even if generated.cpp never references them.
    if(APPLE)
        target_link_options(${TARGET_NAME} PRIVATE
            "-Wl,-force_load,$<TARGET_FILE:pineforge>")
    elseif(UNIX)
        target_link_options(${TARGET_NAME} PRIVATE
            "-Wl,--whole-archive"
            "$<TARGET_FILE:pineforge>"
            "-Wl,--no-whole-archive")
    endif()

    # Suppress warnings that codegen-emitted C++ can never avoid.
    target_compile_options(${TARGET_NAME} PRIVATE
        -Wno-unused-but-set-variable
        -Wno-unused-variable
        -Wno-unused-parameter
        -Wno-sign-compare)

    # Output the shared library as strategy.dylib / strategy.so, co-located
    # with generated.cpp so scripts/run_strategy.py finds it by convention.
    set_target_properties(${TARGET_NAME} PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${STRAT_DIR}
        RUNTIME_OUTPUT_DIRECTORY ${STRAT_DIR}
        OUTPUT_NAME strategy
        PREFIX "")

    math(EXPR _n_bench "${_n_bench} + 1")
endforeach()

message(STATUS "bench strategies: configured ${_n_bench} strategy .dylib/.so targets")

# Aggregate target — build all bench strategies in one go:
#   cmake --build build --target bench_strategies
add_custom_target(bench_strategies
    COMMENT "Built all bench strategy .dylib/.so files")

foreach(STRAT_REL IN LISTS STRATEGY_DIRS)
    set(STRAT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/${STRAT_REL})
    if(NOT IS_DIRECTORY ${STRAT_DIR})
        continue()
    endif()
    if(NOT EXISTS ${STRAT_DIR}/generated.cpp)
        continue()
    endif()
    string(REPLACE "-" "_" TGT ${STRAT_REL})
    set(TGT "bench_strategy_${TGT}")
    string(MAKE_C_IDENTIFIER ${TGT} TGT)
    add_dependencies(bench_strategies ${TGT})
endforeach()
