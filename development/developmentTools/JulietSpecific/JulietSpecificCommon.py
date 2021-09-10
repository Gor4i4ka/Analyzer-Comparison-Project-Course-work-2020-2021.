import os
import re
import subprocess

from copy import deepcopy as dc


def juliet_shorten(string: str):

    if string[5] == "_":
        return string[:5]
    else:
        return string[:6]


def find_in_juliet(filename: str, code_project_source_path, flag=False):

    juliet_path = code_project_source_path + "/testcases"
    for testcase in os.listdir(juliet_path):
        if os.path.isdir(juliet_path + "/" + testcase):
            if juliet_shorten(testcase) == juliet_shorten(filename):
                juliet_path += "/" + testcase
                break
    if flag:
        print(juliet_path)
    for segment_or_file in os.listdir(juliet_path):
        if os.path.isdir(juliet_path + "/" + segment_or_file):
            subdir = "/" + segment_or_file
            if flag:
                print(juliet_path + subdir)
            for file in os.listdir(juliet_path + subdir):

                if file == filename:
                    return juliet_path + subdir + "/" + file
        if os.path.isfile(juliet_path + "/" + segment_or_file):
            if flag:
                print("HEH2")
            if filename == segment_or_file:
                return juliet_path + "/" + segment_or_file
    if flag:
        print(juliet_path)
    return -1