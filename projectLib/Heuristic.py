import math
import numpy as np

import clang
import clang.cindex as ci

# Internal imports
from projectLib.Binding import Binding
from projectLib.Common import srch_list_ind, replace_at_home, dump_ast
from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo


class Heuristic:

    heuristic_name = ""
    heuristic_params = {}

    def __init__(self, heuristic_name: str, heuristic_params: dict):
        self.heuristic_name = heuristic_name
        self.heuristic_params = heuristic_params
        return

    def compare_info_with_heuristic(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        if self.heuristic_name == "lines":
            return self.__lines(analyzer1_info, analyzer2_info)

        if self.heuristic_name == "same_syntax_construct":
            return self.__same_syntax_construct(analyzer1_info, analyzer2_info)

        print("NO SUCH HEURISTIC")
        return -1

    def __subproc_lines_check_intersect(self, lines_list_an1, lines_list_an2, distance):

        for line1 in lines_list_an1:
            for line2 in lines_list_an2:
                if abs(line1 - line2) <= distance:
                    return True
        return False

    def __lines(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        result_comparison = Comparison()
        result_comparison.heur_fill_for_heuristics(analyzer1_info, analyzer2_info)

        if not result_comparison.check_both_FileInfo_format():
            return -1

        # FileInfo actions BEGIN

        for file_info_an1 in analyzer1_info.info:
            file_info_an2 = analyzer2_info.search_by_file(file_info_an1.file)

            if file_info_an2 == -1:
                continue

            for error_info_an1_ind in range(len(file_info_an1.errors)):
                for error_info_an2_ind in range(len(file_info_an2.errors)):
                    if self.__subproc_lines_check_intersect(file_info_an1[error_info_an1_ind].lines,
                                                            file_info_an2[error_info_an2_ind].lines,
                                                            self.heuristic_params["distance"]):
                        file_an1_in_result_comparison = result_comparison.analyzer1_info.search_by_file(file_info_an1.file)
                        file_an2_in_result_comparison = result_comparison.analyzer2_info.search_by_file(file_info_an2.file)

                        file_an1_in_result_comparison[error_info_an1_ind].bindings.append(Binding(ind=error_info_an2_ind))
                        file_an2_in_result_comparison[error_info_an2_ind].bindings.append(
                            Binding(ind=error_info_an1_ind))

        result_comparison.stat_matrix_fill_by_bindings()
                        
        # FileInfo actions END
        return result_comparison

    def __lines_old(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        if analyzer1_info.info_type != "combined" or analyzer2_info.info_type != "combined":
            print("WRONG INFO TYPE FOR EURISTICS LINES")
            return -1

        result_comparison = Comparison()
        result_comparison.fill_for_euristics(analyzer1_info, analyzer2_info)

        cmp_list = result_comparison.compare_list_generation(analyzer1_info, analyzer2_info)

        #################CMP_LIST######################

        for file in cmp_list:
            present_in_an1_ar = np.zeros((len(file[2])), dtype=np.bool)
            for defect1_lines_ind in range(len(file[1])):
                present_in_an2 = False
                error_name1 = file[3][defect1_lines_ind]
                ind1 = srch_list_ind(result_comparison.name_catalog_an1, error_name1)

                for defect2_lines_ind in range(len(file[2])):

                    intersection_found = False
                    for line1 in file[1][defect1_lines_ind]:
                        for line2 in file[2][defect2_lines_ind]:
                            if math.fabs(line2 - line1) <= self.heuristic_params["distance"]:
                                intersection_found = True
                                break
                        if intersection_found:
                            break

                    if intersection_found:
                        present_in_an1_ar[defect2_lines_ind] = True
                        error_name2 = file[4][defect2_lines_ind]
                        ind2 = srch_list_ind(result_comparison.name_catalog_an2, error_name2)

                        present_in_an2 = True
                        result_comparison.stat_matrix[ind1][ind2] += 1
                        result_comparison.error_list_both.append([file[0], file[1][defect1_lines_ind],
                                                                  file[2][defect2_lines_ind], error_name1, error_name2])

                if not present_in_an2:
                    result_comparison.stat_matrix[ind1][-2] += 1
                    result_comparison.error_list_an1.append([file[0], file[1][defect1_lines_ind], error_name1])

            for analyzer2_warning_ind in range(len(present_in_an1_ar)):
                if not present_in_an1_ar[analyzer2_warning_ind]:
                    error_name2 = file[4][analyzer2_warning_ind]
                    ind2 = srch_list_ind(result_comparison.name_catalog_an2, error_name2)
                    result_comparison.stat_matrix[-2][ind2] += 1
                    result_comparison.error_list_an2.append([file[0], file[2][analyzer2_warning_ind], error_name2])

        return result_comparison

    def __subfunc_search(self, node: clang.cindex.Cursor, lst: list):

        if node.kind in self.heuristic_params["statement_list"]:
            trace_unit = []
            trace_unit.append(node.location.line)
            sub_stmts = list(node.get_children())
            for el in sub_stmts:
                trace_unit.append(el.location.line)
            lst.append(trace_unit)

        for c in node.get_children():
            self.__subfunc_search(c, lst)
        return

    def __same_syntax_construct_old(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        if analyzer1_info.info_type != "combined" or analyzer2_info.info_type != "combined":
            print("WRONG INFO TYPE FOR EURISTICS LINES")
            return -1

        result_comparison = Comparison()
        result_comparison.fill_for_euristics(analyzer1_info, analyzer2_info)

        cmp_list = result_comparison.compare_list_generation(analyzer1_info, analyzer2_info)

        #################CMP_LIST######################

        for file in cmp_list:
            refined_file = [file[0], [], [], [], []]
            for an1_ind in range(len(file[3])):
                error_name = file[3][an1_ind]
                if not self.heuristic_params["analyzer1_warn_types_list"] or \
                    error_name in self.heuristic_params["analyzer1_warn_types_list"]:

                    refined_file[1].append(file[1][an1_ind])
                    refined_file[3].append(file[3][an1_ind])
                else:
                    ind = srch_list_ind(result_comparison.name_catalog_an1, error_name)
                    result_comparison.stat_matrix[ind][-2] += 1
                    result_comparison.error_list_an1.append([file[0], file[1][an1_ind], error_name])

            for an2_ind in range(len(file[4])):
                error_name = file[4][an2_ind]
                if not self.heuristic_params["analyzer2_warn_types_list"] or \
                    error_name in self.heuristic_params["analyzer2_warn_types_list"]:

                    refined_file[2].append(file[2][an2_ind])
                    refined_file[4].append(file[4][an2_ind])
                else:
                    ind = srch_list_ind(result_comparison.name_catalog_an2, error_name)
                    result_comparison.stat_matrix[-2][ind] += 1
                    result_comparison.error_list_an2.append([file[0], file[2][an2_ind], error_name])

            if not refined_file[1] or not refined_file[2]:
                for an1_ind in range(len(refined_file[3])):
                    error_name = file[3][an1_ind]
                    ind = srch_list_ind(result_comparison.name_catalog_an1, error_name)
                    result_comparison.stat_matrix[ind][-2] += 1
                    result_comparison.error_list_an1.append([refined_file[0], refined_file[1][an1_ind], refined_file[3][an1_ind]])
                for an2_ind in range(len(refined_file[4])):
                    error_name = file[4][an2_ind]
                    ind = srch_list_ind(result_comparison.name_catalog_an2, error_name)
                    result_comparison.stat_matrix[-2][ind] += 1
                    result_comparison.error_list_an1.append([refined_file[0], refined_file[2][an2_ind], refined_file[4][an2_ind]])
                continue

            ###############LIBCLANG_PART###############

            index = clang.cindex.Index.create()
            translation_unit = index.parse(replace_at_home(refined_file[0]), args=["-std=c++17"])
            cursor = translation_unit.cursor
            syntax_constr_line_list = []
            self.__subfunc_search(cursor, syntax_constr_line_list)

            not_only_in_an2 = np.zeros((len(refined_file[4])), dtype=np.bool)
            for an1_lines_ind in range(len(refined_file[1])):
                error_name1 = refined_file[3][an1_lines_ind]
                ind1 = srch_list_ind(result_comparison.name_catalog_an1, error_name1)

                not_only_in_an1 = False
                found_corresponding_an2 = np.zeros((len(refined_file[4])), dtype=np.bool)
                lines_set_an1 = set(refined_file[1][an1_lines_ind])
                for synt_con_lines in syntax_constr_line_list:
                    synt_set = set(synt_con_lines)
                    for an2_lines_ind in range(len(refined_file[2])):
                        lines_set_an2 = set(refined_file[2][an2_lines_ind])
                        if synt_set.intersection(lines_set_an1) and \
                            synt_set.intersection(lines_set_an2) and not \
                            found_corresponding_an2[an2_lines_ind]:

                            not_only_in_an1 = True
                            found_corresponding_an2[an2_lines_ind] = True
                            not_only_in_an2[an2_lines_ind] = True

                            error_name2 = refined_file[4][an2_lines_ind]
                            ind2 = srch_list_ind(result_comparison.name_catalog_an2, error_name2)

                            result_comparison.stat_matrix[ind1][ind2] += 1
                            result_comparison.error_list_both.append([refined_file[0],
                                                                      refined_file[1][an1_lines_ind],
                                                                      refined_file[2][an2_lines_ind],
                                                                      refined_file[3][an1_lines_ind],
                                                                      refined_file[4][an2_lines_ind]])
                if not not_only_in_an1:
                    result_comparison.stat_matrix[ind1][-2] += 1
                    result_comparison.error_list_an1.append([refined_file[0],
                                                            refined_file[1][an1_lines_ind],
                                                            refined_file[3][an1_lines_ind]])

            for an2_lines_ind in range(not_only_in_an2.shape[0]):
                if not not_only_in_an2[an2_lines_ind]:
                    error_name = refined_file[4][an2_lines_ind]
                    ind = srch_list_ind(result_comparison.name_catalog_an2, error_name)
                    result_comparison.stat_matrix[-2][ind] += 1
                    result_comparison.error_list_an2.append([refined_file[0],
                                                             refined_file[2][an2_lines_ind],
                                                             refined_file[4][an2_lines_ind]])

        return result_comparison




