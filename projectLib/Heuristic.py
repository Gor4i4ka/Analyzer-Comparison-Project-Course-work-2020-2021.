import clang
import re
import numpy as np

from clang import cindex as cl

from copy import deepcopy as dc
# Internal imports
from projectLib.Binding import Binding
from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo

from Common import create_cursor, reaching_var_def_by_line, remove_colon_str


class Heuristic:

    heuristic_name = ""
    heuristic_params = {}

    def __init__(self, heuristic_name: str, heuristic_params: dict):
        self.heuristic_name = heuristic_name
        self.heuristic_params = heuristic_params
        return

    def compare_info_with_heuristic(self, analyzer1_info=None, analyzer2_info=None, used_comparison=None):

        if self.heuristic_name == "lines":
            return self.__lines(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "syntax_construct":
            return self.__syntax_construct(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "reaching_defs":
            return self.__reaching_defs(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "files":
            return self.__files(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "funcs":
            return self.__funcs(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "vars":
            return self.__vars(used_comparison)

        print("NO SUCH HEURISTIC")
        return -1

    # COMMON FOR HEURISTICS BEGIN

    def __subproc_get_msg_leak_var(self, error_info, analyzer_name):
        msg = error_info.msg

        if analyzer_name == "svace":
            regex = re.compile("referenced by '\S*'")
            result = regex.findall(msg)

            if len(result):

                regex = re.compile("'\S*'")
                result = regex.findall(result[0])

                return remove_colon_str(result[0])
            return None

        if analyzer_name == "juliet":
            regex = re.compile("'data'")
            result = regex.findall(msg)

            if len(result):
                return remove_colon_str(result[0])
            return None

        print("ANALYZER {} IS NOT SUPPORTED\n".format(analyzer_name))
        return None

    def __subproc_result_comparison_binding_create(self, result_comparison, file_info_an1, file_info_an2,
                                                   error_info_an1_ind, error_info_an2_ind):

        file_an1_in_result_comparison = result_comparison.analyzer1_info.search_by_file(file_info_an1.file)
        file_an2_in_result_comparison = result_comparison.analyzer2_info.search_by_file(file_info_an2.file)

        file_an1_in_result_comparison[error_info_an1_ind].bindings.append(Binding(ind=error_info_an2_ind))
        file_an2_in_result_comparison[error_info_an2_ind].bindings.append(
            Binding(ind=error_info_an1_ind))

        return

    def __subproc_lines_check_intersect(self, lines_list_an1, lines_list_an2, distance):

        for line1 in lines_list_an1:
            for line2 in lines_list_an2:
                if abs(line1 - line2) <= distance:
                    return True
        return False

    def __subproc_stat_matrix_init(self, comparison):

        comparison.stat_matrix = np.zeros((len(comparison.name_catalog_an1), len(comparison.name_catalog_an2)), dtype="int")
        comparison.stat_matrix[-1][-1] = -1
        comparison.stat_matrix[-1][-2] = -1
        comparison.stat_matrix[-2][-1] = -1
        comparison.stat_matrix[-2][-2] = -1

        return

    def __subproc_comparison_init(self, comparison, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        def __subproc_count_warnings(analyzer_info):
            warning_list = []
            if analyzer_info.info_type == "FileInfo":
                for file in analyzer_info.info:
                    for error in file:
                        in_list = False
                        for warning in warning_list:
                            if error.type == warning[0]:
                                warning[1] += 1
                                in_list = True
                                break
                        if not in_list:
                            warning_list.append([error.type, 1])

            return warning_list

        comparison.name_catalog_an1 = [warn[0] for warn in __subproc_count_warnings(analyzer1_info)]
        comparison.name_catalog_an2 = [warn[0] for warn in __subproc_count_warnings(analyzer2_info)]

        comparison.name_catalog_an1.append("ONLY_IN_ANALYZER2")
        comparison.name_catalog_an1.append("TOTAL_AMOUNT_AN2")

        comparison.name_catalog_an2.append("ONLY_IN_ANALYZER1")
        comparison.name_catalog_an2.append("TOTAL_AMOUNT_AN1")

        self.__subproc_stat_matrix_init(comparison)

        comparison.analyzer1_info = dc(analyzer1_info)
        comparison.analyzer2_info = dc(analyzer2_info)

        return 0

    # COMMON FOR HEURISTICS END

    # HEURISTICS BEGIN

    def __lines(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, used_comparison=None):

        result_comparison = Comparison()
        self.__subproc_comparison_init(result_comparison, analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        # FileInfo actions BEGIN

        for file_info_an1 in analyzer1_info.info:
            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)

            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            for error_info_an1_ind in range(len(file_info_an1.errors)):
                for error_info_an2_ind in range(len(file_info_an2.errors)):
                    if self.__subproc_lines_check_intersect(file_info_an1[error_info_an1_ind].lines,
                                                            file_info_an2[error_info_an2_ind].lines,
                                                            self.heuristic_params["distance"]):
                        self.__subproc_result_comparison_binding_create(result_comparison, file_info_an1, file_info_an2,
                                                                        error_info_an1_ind, error_info_an2_ind)

                        
        # FileInfo actions END
        result_comparison.stat_matrix_fill_by_bindings()
        return result_comparison

    def __syntax_construct(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, used_comparison=None):

        # SUBPROCEDURES BEGIN

        def __subfunc_search(node: clang.cindex.Cursor, lst: list):

            if node.kind in self.heuristic_params["statement_list"]:
                trace_unit = []
                trace_unit.append(node.location.line)
                sub_stmts = list(node.get_children())
                for el in sub_stmts:
                    trace_unit.append(el.location.line)
                lst.append(trace_unit)

            for c in node.get_children():
                __subfunc_search(c, lst)
            return

        # SUBPROCEDURES END

        result_comparison = Comparison()
        self.__subproc_comparison_init(result_comparison, analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        # FileInfo actions BEGIN

        for file_info_an1 in analyzer1_info:

            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)
            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            index = clang.cindex.Index.create()
            translation_unit = index.parse(file_info_an1.file, args=[self.heuristic_params["c++_version"]])
            cursor = translation_unit.cursor

            syntax_constr_line_list = []
            __subfunc_search(cursor, syntax_constr_line_list)

            for error_info_an1_ind in range(len(file_info_an1.errors)):
                for error_info_an2_ind in range(len(file_info_an2.errors)):
                    if file_info_an1[error_info_an1_ind].type in self.heuristic_params["analyzer1_warn_types_list"] and \
                       file_info_an2[error_info_an2_ind].type in self.heuristic_params["analyzer2_warn_types_list"]:

                        for statement_lines in syntax_constr_line_list:
                            if self.__subproc_lines_check_intersect(file_info_an1[error_info_an1_ind].lines,
                                                                    statement_lines, 0) and \
                                self.__subproc_lines_check_intersect(file_info_an2[error_info_an2_ind].lines,
                                                                     statement_lines, 0):
                                self.__subproc_result_comparison_binding_create(result_comparison, file_info_an1, file_info_an2,
                                                                                error_info_an1_ind, error_info_an2_ind)

        # FileInfo actions END
        result_comparison.stat_matrix_fill_by_bindings()
        return result_comparison

    def __reaching_defs(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, used_comparison=None):

        result_comparison = Comparison()
        self.__subproc_comparison_init(result_comparison, analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        for file_info_an1 in analyzer1_info:

            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)
            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            cursor = create_cursor(file_info_an1.file)

            for error_an1_ind, error_an1 in enumerate(file_info_an1):
                var_er_an1 = self.__subproc_get_msg_leak_var(error_an1, analyzer1_info.analyzer_name)

                if var_er_an1 is None:
                    continue

                line_er_an1 = error_an1.main_line
                cursor_er_an1 = reaching_var_def_by_line(cursor, var_er_an1, line_er_an1)
                for error_an2_ind, error_an2 in enumerate(file_info_an2):
                    var_er_an2 = self.__subproc_get_msg_leak_var(error_an2, analyzer2_info.analyzer_name)

                    if var_er_an2 is None:
                        continue

                    line_er_an2 = error_an2.main_line
                    cursor_er_an2 = reaching_var_def_by_line(cursor, var_er_an2, line_er_an2)

                    if cursor_er_an1 is None or cursor_er_an2 is None:
                        continue

                    if cursor_er_an2 == cursor_er_an1:
                        self.__subproc_result_comparison_binding_create(result_comparison, file_info_an1, file_info_an2,
                                                                        error_an1_ind, error_an2_ind)

        result_comparison.stat_matrix_fill_by_bindings()
        return result_comparison

    def __files(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, used_comparison=None):

        result_comparison = Comparison()
        self.__subproc_comparison_init(result_comparison, analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        for file_info_an1 in analyzer1_info:

            #if file_info_an1.file == "/home/nick/C/testcases/CWE401_Memory_Leak/s01/CWE401_Memory_Leak__char_calloc_21.c":
            #    print("HEH")

            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)
            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            for error_an1_ind, error_an1 in enumerate(file_info_an1):
                var_er_an1 = self.__subproc_get_msg_leak_var(error_an1, analyzer1_info.analyzer_name)

                for error_an2_ind, error_an2 in enumerate(file_info_an2):
                    var_er_an2 = self.__subproc_get_msg_leak_var(error_an2, analyzer2_info.analyzer_name)

                    if var_er_an1 == var_er_an2:
                        self.__subproc_result_comparison_binding_create(result_comparison, file_info_an1, file_info_an2,
                                                                        error_an1_ind, error_an2_ind)

        result_comparison.stat_matrix_fill_by_bindings()
        return result_comparison

    def __funcs(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo, used_comparison=None):
        # TODO: fully implement and debug

        def __subproc_same_func_in_file_check(cursor: cl.Cursor, error_an1, error_an2):

            for child in cursor.get_children():
                if child.kind == cl.CursorKind.FUNCTION_DECL:
                    if child.extent.start.line <= error_an1.main_line <= child.extent.end.line and \
                            child.extent.start.line <= error_an2.main_line <= child.extent.end.line:
                        return True

        result_comparison = Comparison()
        self.__subproc_comparison_init(result_comparison, analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        for file_info_an1 in analyzer1_info:

            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)
            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            cursor = create_cursor(file_info_an1.file)

            for error_info_an1_ind, error_an1 in enumerate(file_info_an1):
                for error_info_an2_ind, error_an2 in enumerate(file_info_an2):
                    if __subproc_same_func_in_file_check(cursor, error_an1, error_an2):
                        self.__subproc_result_comparison_binding_create(result_comparison, file_info_an1, file_info_an2,
                                                                        error_info_an1_ind, error_info_an2_ind)

        result_comparison.stat_matrix_fill_by_bindings()
        return result_comparison

    def __vars(self, used_comparison):

        def __subproc_search_entities_in_lines(node: clang.cindex.Cursor, found_lines: list, result_set: set):
            # dump_ast(node)
            if node.kind == clang.cindex.CursorKind.VAR_DECL or \
                    node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                if node.location.line in found_lines:
                    result_set.add(str(node.displayname))
            for c in node.get_children():
                __subproc_search_entities_in_lines(c, found_lines, result_set)

        def __subproc_present_entity_uses(node, lines_list, variable_set):
            if node.kind == clang.cindex.CursorKind.VAR_DECL or \
                    node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
                if node.location.line in lines_list:
                    if str(node.displayname) in variable_set:
                        return True
            for c in node.get_children():
                if __subproc_present_entity_uses(c, lines_list, variable_set):
                    return True
            return False

        if not used_comparison.check_both_FileInfo_format():
            return -1

        list_buf_overflow_types_an1 = self.heuristic_params["type_groups"][used_comparison.analyzer1_info.analyzer_name]["Buffer_overflow"]
        list_buf_overflow_types_an2 = self.heuristic_params["type_groups"][used_comparison.analyzer2_info.analyzer_name]["Buffer_overflow"]

        analyzer1_info_res = dc(used_comparison.analyzer1_info)
        analyzer2_info_res = dc(used_comparison.analyzer2_info)

        # FileInfo actions BEGIN
        for file_info_an1 in used_comparison.analyzer1_info:

            file_info_an2 = used_comparison.analyzer2_info.search_by_file(file_info_an1.file)

            if isinstance(file_info_an2, int) and file_info_an2 == -1:
                continue

            index = clang.cindex.Index.create()
            translation_unit = index.parse(file_info_an1.file, args=["-std=c++17"])
            cursor = translation_unit.cursor

            for error_info_an1_ind in range(len(file_info_an1.errors)):
                if file_info_an1[error_info_an1_ind].type in list_buf_overflow_types_an1:

                    er1_bindings = []
                    er1_entities = set()

                    for binding1 in file_info_an1[error_info_an1_ind].bindings:

                        if binding1.file:
                            continue

                        #Experimental comment
                        #if file_info_an2[binding1.ind].type not in list_buf_overflow_types_an2:
                         #   continue

                        er1_bindings.append(binding1)

                    __subproc_search_entities_in_lines(cursor, file_info_an1[error_info_an1_ind].lines, er1_entities)

                    for error_info_an1_ind_sub in range(len(file_info_an1.errors)):
                        if file_info_an1[error_info_an1_ind_sub].type in list_buf_overflow_types_an1:
                            if __subproc_present_entity_uses(cursor, file_info_an1[error_info_an1_ind_sub].lines, er1_entities):
                                for binding in er1_bindings:

                                    file_an1_in_result_comparison = analyzer1_info_res.search_by_file(file_info_an1.file)
                                    file_an2_in_result_comparison = analyzer2_info_res.search_by_file(file_info_an2.file)

                                    if not file_an1_in_result_comparison[error_info_an1_ind_sub].binding_already_present(binding):
                                        file_an1_in_result_comparison[error_info_an1_ind_sub].append(binding)
                                        file_an2_in_result_comparison[binding.ind].append(Binding(ind=error_info_an1_ind_sub))

                    for error_info_an2_ind_sub in range(len(file_info_an2.errors)):
                        if file_info_an2[error_info_an2_ind_sub].type in list_buf_overflow_types_an2:
                            if __subproc_present_entity_uses(cursor, file_info_an1[error_info_an2_ind_sub].lines,
                                                                  er1_entities):
                                file_an1_in_result_comparison = analyzer1_info_res.search_by_file(file_info_an1.file)
                                file_an2_in_result_comparison = analyzer2_info_res.search_by_file(file_info_an2.file)

                                binding_to_add = Binding(ind=error_info_an1_ind)
                                if not file_an2_in_result_comparison[error_info_an2_ind_sub]. \
                                    binding_already_present(binding_to_add):
                                    file_an2_in_result_comparison[error_info_an2_ind_sub].append(binding_to_add)
                                    file_an1_in_result_comparison[error_info_an1_ind].append(Binding(ind=error_info_an2_ind_sub))

        # FileInfo actions END

        used_comparison.analyzer1_info = analyzer1_info_res
        used_comparison.analyzer2_info = analyzer2_info_res

        self.__subproc_stat_matrix_init(used_comparison)
        used_comparison.stat_matrix_fill_by_bindings()

        return

    # HEURISTICS END


