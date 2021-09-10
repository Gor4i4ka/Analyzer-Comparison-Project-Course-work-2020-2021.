import re
import clang.cindex

from ctypes import *
from copy import deepcopy as dc

# Internal imports
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ErrorInfo import ErrorInfo
from Common import list_intersect


def __subproc_stratify_juliet_file_name(file_name: str):

    re_expr = re.compile("\D{0,1}\.")
    result = re.split(pattern=re_expr, string=file_name)

    return result[0]


def __subproc_juliet_defect_name_list(analyzer_info: AnalyzerInfo):

    res_list = []

    for file_info in analyzer_info:
        defect_name = __subproc_stratify_juliet_file_name(file_info.file)
        if defect_name not in res_list:
            res_list.append(defect_name)
    return res_list


def juliet_divide_files(analyzer_info_an1, analyzer_info_an2, mode=1):

    # Has 2 modes, either to get only bindable errors, or unbindable by file criteria

    analyzer_info_res_an1 = dc(analyzer_info_an1)
    analyzer_info_res_an2 = dc(analyzer_info_an2)
    analyzer_info_res_an1.info = []
    analyzer_info_res_an2.info = []

    has_errors_list_an1 = __subproc_juliet_defect_name_list(analyzer_info_an1)
    has_errors_list_an2 = __subproc_juliet_defect_name_list(analyzer_info_an2)

    only_useful_files_list = list_intersect(has_errors_list_an1, has_errors_list_an2)

    for file_info_an1 in analyzer_info_an1:
        file_category = __subproc_stratify_juliet_file_name(file_info_an1.file)
        category_present = file_category in only_useful_files_list
        if category_present:
            if mode == 1:
                analyzer_info_res_an1.append(dc(file_info_an1))
        else:
            if mode == 2:
                analyzer_info_res_an1.append(dc(file_info_an1))

    for file_info_an2 in analyzer_info_an2:
        file_category = __subproc_stratify_juliet_file_name(file_info_an2.file)
        category_present = file_category in only_useful_files_list
        if category_present:
            if mode == 1:
                analyzer_info_res_an2.append(dc(file_info_an2))
        else:
            if mode == 2:
                analyzer_info_res_an2.append(dc(file_info_an2))

    return analyzer_info_res_an1, analyzer_info_res_an2


def __subproc_check_error_unlinkable(error_info, start, end):
    for line in error_info.lines:
        if start < line < end:
            return True
    return False


def juliet_divide_funcs_svace(analyzer_info_an1, mode=1):

    # Has 2 modes, either to get only bindable errors, or unbindable by "good" func name criteria

    analyzer_info_res_an1 = dc(analyzer_info_an1)
    analyzer_info_res_an1.info = []

    re_expr = re.compile(".*good.*")

    good_function_start = None
    good_function_end = None

    for file_info in analyzer_info_an1:

        file_info_to_add = dc(file_info)

        index = clang.cindex.Index.create()
        translation_unit = index.parse(file_info.file)
        cursor = translation_unit.cursor

        # FileInfo actions BEGIN

        for possible_func in cursor.get_children():
            good_function_end = possible_func.location.line

            if good_function_start:
                for error_info in file_info:
                    if __subproc_check_error_unlinkable(error_info,
                                                        good_function_start,
                                                        good_function_end):
                        if mode == 1:
                            if error_info in file_info_to_add:
                                file_info_to_add.remove(error_info)
                    else:
                        if mode == 2:
                            if error_info in file_info_to_add:
                                file_info_to_add.remove(error_info)

            if possible_func.kind == clang.cindex.CursorKind.FUNCTION_DECL:

                check_good_in_name = re_expr.findall(possible_func.displayname)
                if len(check_good_in_name):
                    good_function_start = possible_func.location.line

            else:
                good_function_start = None

        analyzer_info_res_an1.append(file_info_to_add)
    return analyzer_info_res_an1


