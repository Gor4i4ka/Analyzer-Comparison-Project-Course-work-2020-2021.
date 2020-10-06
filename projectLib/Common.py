import pickle
import numpy as np


def juliet_shorten(str):

    if str[5] == "_":
        return str[:5]
    else:
        return str[:6]


def remove_parent_dirs(str):
    #return str
    ln = len(str) - 1
    while ln > 0:
        if str[ln] == '/':
            return str[ln + 1:]
        ln -= 1
    return str


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


def count_warnings(analyzer_info):
    warning_list = []
    for file in analyzer_info:
        for el in file[2]:
            in_list = False
            for warn in warning_list:
                if el == warn[0]:
                    warn[1] += 1
                    in_list = True
                    break
            if not in_list:
                warning_list.append([el, 1])
    return warning_list


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
    #print(row_buffer_max)
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


def save_list(list, path):
    with open(path, "wb") as filehandle:
         # store the data as binary data stream
         pickle.dump(list, filehandle)
    return 0


def load_list(path):
    with open(path, 'rb') as filehandle:
        # read the data as binary data stream
        return pickle.load(filehandle)


def print_list(list):
    for el in list:
        print("{}".format(el))
    return 0

