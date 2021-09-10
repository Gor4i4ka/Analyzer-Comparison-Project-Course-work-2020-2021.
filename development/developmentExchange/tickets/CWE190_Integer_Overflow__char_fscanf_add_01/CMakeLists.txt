cmake_minimum_required(VERSION 2.8)
project(CWE190_Integer_Overflow__char_fscanf_add_01)

SET (CMAKE_RUNTIME_OUTPUT_DIRECTORY
${PROJECT_BINARY_DIR}/bin
CACHE PATH
"executable main"
)

include_directories(${PROJECT_SOURCE_DIR}/testcasesupport)
link_directories(${PROJECT_BINARY_DIR})

add_definitions(-DINCLUDEMAIN)
add_executable(Testcase ${PROJECT_SOURCE_DIR}/CWE190_Integer_Overflow__char_fscanf_add_01.c)

target_link_libraries(Testcase ${PROJECT_SOURCE_DIR}/testcasesupport/io.c.o)

add_custom_target(allclean COMMAND rm -r ${PROJECT_BINARY_DIR}/*)