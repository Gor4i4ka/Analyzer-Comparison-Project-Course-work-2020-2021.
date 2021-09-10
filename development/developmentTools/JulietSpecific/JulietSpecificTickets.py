import re
import os
import subprocess

# Internal imports
from ProjectConfig import project_binary_dir, code_project_source_path
from Common import remove_parent_dirs


def __subproc_juliet_find_cwe_num(cwe_name):

    regex = re.compile("CWE\d{1,3}")
    cwe_num = regex.findall(cwe_name)

    return cwe_num[0]


def __subproc_get_testcase_name(file_name: str):

    re_expr = re.compile("\D{0,1}\.")
    result = re.split(pattern=re_expr, string=file_name)

    return result[0]


def __subproc_testcase_full_file_list(code_project_path, cwe_name, testcase_name):

    cwe_full_name = None

    for dir in os.listdir(path=code_project_path + "/testcases"):
        if cwe_name in dir:
            cwe_full_name = dir

    bash_command = "find " + code_project_path + "/testcases" + "/" + cwe_full_name + \
                  " -name " + testcase_name + "*.c*"

    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output_binary = process.communicate()[0]

    output = None

    if output_binary:
        output = bytes.decode(output_binary)

    regex = re.compile("\n")
    result = regex.split(output)

    return result


def __subproc_create_cmake_list(ticket_path, testcase_name, file_list):

    # Creating CMakeLists.txt

    cmake_lists_path = ticket_path + "/CMakeLists.txt"
    bash_command = "touch " + cmake_lists_path
    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

    with open(cmake_lists_path, 'a') as cmake_lists:

        cmake_lists.write("cmake_minimum_required(VERSION 2.8)\n")
        cmake_lists.write("project(" + testcase_name + ")\n\n")
        cmake_lists.write('SET (CMAKE_RUNTIME_OUTPUT_DIRECTORY\n'
                          '${PROJECT_BINARY_DIR}/bin\n'
                          'CACHE PATH\n'
                          '"executable main"\n'
                          ')\n\n')
        cmake_lists.write("include_directories(${PROJECT_SOURCE_DIR}/testcasesupport)\n")
        cmake_lists.write("link_directories(${PROJECT_BINARY_DIR})\n\n")

        main_file = file_list[-2]

        cmake_lists.write("add_definitions(-DINCLUDEMAIN)\n")
        cmake_lists.write("add_executable(Testcase " +
                          "${PROJECT_SOURCE_DIR}/" + remove_parent_dirs(main_file) + ")\n\n")

        # Creating libs from extra files

        library_needed_flag = False
        library_script = "add_library(extra_files "

        for extra_file in file_list:
            if extra_file and extra_file != main_file:
                library_needed_flag = True
                library_script += "${PROJECT_SOURCE_DIR}/" + remove_parent_dirs(extra_file) + " "

        library_script += ")\n"

        if library_needed_flag:
            cmake_lists.write(library_script)

        link_script = "target_link_libraries(Testcase ${PROJECT_SOURCE_DIR}/testcasesupport/io.c.o"
        if library_needed_flag:
            link_script += " extra_files"

        link_script += ")\n\n"

        cmake_lists.write(link_script)

        cmake_lists.write("add_custom_target(allclean COMMAND rm -r ${PROJECT_BINARY_DIR}/*)")

    return 0


def juliet_create_ticket(file_name):


    # Getting all files in the testcase

    cwe_name = __subproc_juliet_find_cwe_num(file_name)
    testcase_name = __subproc_get_testcase_name(file_name)

    ticket_path = project_binary_dir + "/tickets" + "/" + testcase_name

    testcase_file_path_list = __subproc_testcase_full_file_list(code_project_source_path, cwe_name, testcase_name)

    # Creating directories and moving files

    bash_command = "mkdir " + ticket_path
    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

    bash_command = "mkdir " + ticket_path + "/build"
    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

    bash_command = "cp -r " + code_project_source_path + "/testcasesupport" + " " + ticket_path + "/testcasesupport"
    subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

    for source_file_path in testcase_file_path_list:

        bash_command = "cp " + source_file_path + " " + ticket_path + "/" + remove_parent_dirs(source_file_path)
        subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)

    __subproc_create_cmake_list(ticket_path, testcase_name, testcase_file_path_list)

    return 0