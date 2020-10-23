import pickle
import os
import asciitree
import sys
import clang
import clang.cindex
import copy

#Internal imports
from projectLib.ProjectConfig import xml_source_path, juliet_work_path


def list_intersect(lst1: list, lst2: list):
    result_list = []
    for el1 in lst1:
        if el1 in lst2:
            result_list.append(lst1)

    return result_list


def list_subtraction(lst1: list, lst2: list):
    result_list = copy.deepcopy(lst1)
    for el1 in lst1:
        if el1 in lst2:
            result_list.remove(el1)
            lst2.remove(el1)

    return result_list

#print(list_subtraction([[1, 4], 2, 3, 4, 5, 2], [3, [1, 4], 5, 2]))
def dump_ast(node: clang.cindex.Cursor, ident=""):
    print(ident + str(node.kind))

    for c in node.get_children():
        dump_ast(c, ident + "_")


def replace_at_home(filename: str, at_home=False):
    if not at_home:
        return filename
    home_path = '/home/gorchichka/'
    return home_path + filename[11:]

def juliet_shorten(string: str):

    if string[5] == "_":
        return string[:5]
    else:
        return string[:6]


def find_in_juliet(filename: str, flag=False):

    juliet_path = get_parent_dirs(xml_source_path["juliet"]) + "/testcases"
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


def remove_parent_dirs(string: str):
    ln = len(string) - 1
    while ln > 0:
        if string[ln] == '/':
            return string[ln + 1:]
        ln -= 1
    return string


def get_parent_dirs(string: str):
    ln = len(string) - 1
    while ln > 0:
        if string[ln] == '/':
            return string[:ln]
        ln -= 1
    return string


def srch_info(info, el):
    for piece in info:
        if el[0] == piece[0]:
            return piece
    return None


def srch_ind(lst, el):
    for piece in range(len(lst)):
        if el[0] == lst[piece][0]:
            return piece
    return None


def srch_list_ind(lst, val):
    for ind in range(len(lst)):
        if lst[ind] == val:
            return ind
    return None


def print_num_blanks(amount):
    for i in range(amount):
        print(" ", end='')


def print_numpy(nparray, rows, columns):
    int_buffer_max = len(str(nparray.max()))
    column_buffer_max = 0
    row_buffer_max = 0

    for column in columns:
        if len(column) > column_buffer_max:
            column_buffer_max = len(column)

    for row in rows:
        if len(row) > row_buffer_max:
            row_buffer_max = len(row)

    value_size = max(int_buffer_max, column_buffer_max)
    interval_size = 1

    blank_value = ''
    blank_interval = ''

    for i in range(value_size):
        blank_value += ' '

    for i in range(interval_size):
        blank_interval += ' '

    ### First Row
    print_num_blanks(row_buffer_max)
    print(blank_interval, end='')
    for column in columns:
        print(column, end='')
        print_num_blanks(column_buffer_max - len(column))
        print(blank_interval, end='')
    print()

    ### All rows
    for row_ind in range(len(rows)):
        print(rows[row_ind], end='')
        print_num_blanks(row_buffer_max - len(rows[row_ind]))
        print(blank_interval, end='')
        for column_ind in range(len(columns)):
            value = str(nparray[row_ind][column_ind])
            print(value, end='')
            print_num_blanks(column_buffer_max - len(value))
            print(blank_interval, end='')
        print()


def save_list(lst, path):
    with open(path, "wb") as filehandle:
         pickle.dump(lst, filehandle)
    return 0


def load_list(path):
    with open(path, 'rb') as filehandle:
        # read the data as binary data stream
        return pickle.load(filehandle)


def print_list(lst):
    for el in lst:
        print("{}".format(el))
    return 0


