cmake_minimum_required(VERSION 3.12)
project(analyzer_comparison)

file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/juliet_info)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/svace_info)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/comparison_results)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/comparison_results/analyzer1_info)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/comparison_results/analyzer2_info)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/svres_generates)

#find_package(python3)
#find_package(
#	projectLib
#	PATHS ${PROJECT_SOURCE_DIR}
#	NAMES projectLib
#	)

#find_package(Python3 COMPONENTS Interpreter Development)
#Python3_add_library(projectLib ${PROJECT_SOURCE_DIR}/projectLib)

add_custom_target(allclean COMMAND rm -r ${PROJECT_BINARY_DIR}/*)

#add_custom_target(main_test COMMAND python3 ${PROJECT_SOURCE_DIR}/tests/main_test.py)
