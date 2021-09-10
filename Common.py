import pickle
import copy
import re
import clang

from copy import deepcopy as dc
from clang import cindex as cl
# Internal imports
from ProjectConfig import code_project_source_path

# HANDY STRING STUFF BEGIN

def remove_colon_str(string):
    return string[1:-1]

# HANDY STRING STUFF END

# HANDY CLANG STUFF BEGIN

possible_definitions_list = [
    cl.CursorKind.FIELD_DECL,
    cl.CursorKind.VAR_DECL,
    cl.CursorKind.PARM_DECL,
    cl.CursorKind.MEMBER_REF,
    cl.CursorKind.VARIABLE_REF,
    cl.CursorKind.DECL_REF_EXPR
]

def create_cursor(file_name):
    index = clang.cindex.Index.create()
    translation_unit = index.parse(file_name)
    cursor = translation_unit.cursor

    return cursor

def dump_ast(cursor: clang.cindex.Cursor, depth=0):

    for i in range(depth):
        print("-", end="")
    print(cursor.kind)

    for child in cursor.get_children():
        dump_ast(child, depth+1)
    return 0


def reaching_var_def_by_line(TU: clang.cindex.Cursor, var: str, line: int):

    def __subproc_children_check(cursor: clang.cindex.Cursor, var: str, line: int, cur_def_list: list):

        def __subproc_checks(cursor, var, line, cur_def_list):

            if cursor.extent.start.line <= line:

                if cursor.kind in possible_definitions_list:
                    if cursor.displayname == var:
                        cur_def_list.clear()
                        cur_def_list.append(cursor)
                        return True

                if cursor.kind == cl.CursorKind.BINARY_OPERATOR:
                    for possible_def in cursor.get_children():
                        if possible_def.displayname == var:
                            cur_def_list.clear()
                            cur_def_list.append(possible_def)
                            return True
                        break

            return False

        if __subproc_checks(cursor, var, line, cur_def_list):
            return

        for child in cursor.get_children():
            __subproc_checks(child, var, line, cur_def_list)

        start = cursor.extent.start.line
        end = cursor.extent.end.line

        if start <= line <= end:
            for child in cursor.get_children():
                __subproc_children_check(child, var, line, cur_def_list)
            return

    current_definition_list = [TU]
    __subproc_children_check(TU, var, line, current_definition_list)

    if current_definition_list[0] == TU:
        return None

    return current_definition_list[0]

# HANDY CLANG STUFF END

# HANDY REGEX STUFF BEGIN

def remove_parent_dirs(file_path):

    regex = re.compile("/")
    result = regex.split(file_path)

    return result[-1]

# HANDY REGEX STUFF END

# HANDY NUMPY STUFF BEGIN

def __subproc_print_num_blanks(amount):
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

    # First Row
    __subproc_print_num_blanks(row_buffer_max)
    print(blank_interval, end='')
    for column in columns:
        print(column, end='')
        __subproc_print_num_blanks(column_buffer_max - len(column))
        print(blank_interval, end='')
    print()

    # All rows
    for row_ind in range(len(rows)):
        print(rows[row_ind], end='')
        __subproc_print_num_blanks(row_buffer_max - len(rows[row_ind]))
        print(blank_interval, end='')
        for column_ind in range(len(columns)):
            value = str(nparray[row_ind][column_ind])
            print(value, end='')
            __subproc_print_num_blanks(column_buffer_max - len(value))
            print(blank_interval, end='')
        print()

# HANDY NUMPY STUFF END

# HANDY LIST STUFF BEGIN


def list_union(lst1: list, lst2: list):
    result_list = dc(lst1)
    for el2 in lst2:
        if el2 not in result_list:
            result_list.append(dc(el2))

    return result_list


def list_intersect(lst1: list, lst2: list):
    result_list = []
    for el1 in lst1:
        if el1 in lst2:
            result_list.append(el1)

    return result_list


def list_subtraction(lst1: list, lst2: list):
    result_list = copy.deepcopy(lst1)
    for el1 in lst1:
        if el1 in lst2:
            result_list.remove(el1)
            lst2.remove(el1)

    return result_list


def srch_list_ind(lst, val):
    for ind in range(len(lst)):
        if lst[ind] == val:
            return ind
    return None


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

# HANDY LIST STUFF END

