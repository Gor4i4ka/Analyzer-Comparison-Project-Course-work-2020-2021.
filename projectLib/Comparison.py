from operator import itemgetter

import numpy as np
import copy
import clang
import clang.cindex

# Internal imports
from projectLib.Common import srch_list_ind, save_list, load_list, print_numpy, dump_ast
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ProjectConfig import type_groups
from projectLib.FileInfo import FileInfo
from projectLib.ErrorInfo import ErrorInfo
from projectLib.Binding import Binding


class Comparison:

    def __init__(self,
                 analyzer1_info: AnalyzerInfo=AnalyzerInfo(),
                 analyzer2_info: AnalyzerInfo=AnalyzerInfo()):

        self.name_catalog_an1 = []
        self.name_catalog_an2 = []
        self.stat_matrix = None

        self.analyzer1_info = copy.deepcopy(analyzer1_info)
        self.analyzer2_info = copy.deepcopy(analyzer2_info)

    def check_both_FileInfo_format(self):
        if self.analyzer1_info.info_type != "FileInfo" or \
           self.analyzer2_info.info_type != "FileInfo":
            print("GROUP COMPARISON ONLY SUPPORTED FOR FileInfo info_type")
            return False
        return True

    def get_errors_only_in_analyzer_num(self, analyzer_num: int):
        if not self.check_both_FileInfo_format():
            return -1

        if analyzer_num == 1:
            analyzer_info = self.analyzer1_info
        else:
            if analyzer_num == 2:
                analyzer_info = self.analyzer2_info
            else:
                print("NO SUCH ANALYZER_NUM")
                return -1

        result_analyzer_info = AnalyzerInfo(analyzer_name=analyzer_info.analyzer_name,
                                            info_type=analyzer_info.info_type)

        # FileInfo actions BEGIN
        for file_info in analyzer_info.info:
            file_to_add = FileInfo(file=file_info.file)
            for error_info in file_info.errors:
                if not error_info.has_bindings():
                    file_to_add.append(error_info)
            if file_to_add.has_errors():
                result_analyzer_info.append(file_to_add)

        # FileInfo actions END
        return result_analyzer_info

    def get_errors_in_all_analyzers(self):
        if not self.check_both_FileInfo_format():
            return -1

        result_analyzer_info = AnalyzerInfo(analyzer_name="COMBINED",
                                            info_type=self.analyzer1_info)

        # FileInfo actions BEGIN

        for file_info_an1 in self.analyzer1_info.info:
            for error_info_an1 in file_info_an1:
                for binding in error_info_an1.bindings:
                    filename_to_search = file_info_an1.file
                    if binding.file:
                        filename_to_search = binding.file
                    file_info_an2 = self.analyzer2_info.search_by_file(filename_to_search)
                    error_info_an2 = file_info_an2[binding.ind]
                    result_analyzer_info.append(
                        [ErrorInfo(
                            file=file_info_an1.file,
                            lines=error_info_an1.lines,
                            type=error_info_an1.type),
                        ErrorInfo(
                            file=binding.file,
                            lines=error_info_an2.lines,
                            type=error_info_an2.type
                        )])

        # FileInfo actions END
        return result_analyzer_info

    def comparison_copy(self, orig):
        self.name_catalog_an1 = copy.deepcopy(orig.name_catalog_an1)
        self.name_catalog_an2 = copy.deepcopy(orig.name_catalog_an2)
        self.stat_matrix = copy.deepcopy(orig.stat_matrix)

        self.analyzer1_info = copy.deepcopy(orig.analyzer1_info)
        self.analyzer2_info = copy.deepcopy(orig.analyzer2_info)

    def save_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/cmp_name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/cmp_name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/cmp_stat_matrix" + str(comparison_id) + ".npy"
        analyzer1_info_path = res_dir
        analyzer2_info_path = res_dir

        save_list(self.name_catalog_an1, name_catalog_an1_path)
        save_list(self.name_catalog_an2, name_catalog_an2_path)
        np.save(stat_matrix_path, self.stat_matrix)
        self.analyzer1_info.save_info(analyzer1_info_path, comparison_id)
        self.analyzer2_info.save_info(analyzer2_info_path, comparison_id)

        return 0

    def load_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/cmp_name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/cmp_name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/cmp_stat_matrix" + str(comparison_id) + ".npy"
        analyzer1_info_path = res_dir
        analyzer2_info_path = res_dir

        self.name_catalog_an1 = load_list(name_catalog_an1_path)
        self.name_catalog_an2 = load_list(name_catalog_an2_path)
        self.stat_matrix = np.load(stat_matrix_path)
        self.analyzer1_info.load_info(analyzer1_info_path, comparison_id)
        self.analyzer2_info.load_info(analyzer2_info_path, comparison_id)

        return 0

    def group_comparison(self, an1_type_groups, an2_type_groups):
        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = Comparison(copy.deepcopy(self.analyzer1_info),
                                       copy.deepcopy(self.analyzer2_info))

        result_comparison.stat_matrix = np.zeros((self.stat_matrix.shape[0] - an1_type_groups["TOTAL_COMPRESSION"],
                                                  self.stat_matrix.shape[1] - an2_type_groups["TOTAL_COMPRESSION"]),
                                                  dtype=np.int)

        name_catalog_an1_dict = []
        name_catalog_an1_initial = []

        for el_ind in range(len(self.name_catalog_an1)):
            name_catalog_an1_initial.append([self.name_catalog_an1[el_ind], [el_ind]])

        for dict_name in an1_type_groups:
            if dict_name == "TOTAL_COMPRESSION":
                continue
            dict_name_column_list = []
            for catalog_name_ind in range(len(self.name_catalog_an1)):
                if self.name_catalog_an1[catalog_name_ind] in an1_type_groups[dict_name]:
                    dict_name_column_list.append(catalog_name_ind)
                    name_catalog_an1_initial.remove([self.name_catalog_an1[catalog_name_ind], [catalog_name_ind]])
            name_catalog_an1_dict.append([dict_name, dict_name_column_list])

        name_catalog_an2_dict = []
        name_catalog_an2_initial = []

        for el_ind in range(len(self.name_catalog_an2)):
            name_catalog_an2_initial.append([self.name_catalog_an2[el_ind], [el_ind]])

        for dict_name in an2_type_groups:
            if dict_name == "TOTAL_COMPRESSION":
                continue
            dict_name_column_list = []
            for catalog_name_ind in range(len(self.name_catalog_an2)):
                if self.name_catalog_an2[catalog_name_ind] in an2_type_groups[dict_name]:
                    dict_name_column_list.append(catalog_name_ind)
                    name_catalog_an2_initial.remove(
                        [self.name_catalog_an2[catalog_name_ind], [catalog_name_ind]])
            name_catalog_an2_dict.append([dict_name, dict_name_column_list])

        name_catalog_an1_merged = name_catalog_an1_dict + name_catalog_an1_initial
        name_catalog_an2_merged = name_catalog_an2_dict + name_catalog_an2_initial

        for an1_ind in range(len(name_catalog_an1_merged)):
            for an2_ind in range(len(name_catalog_an2_merged)):
                for stat_matrix_ind_line in name_catalog_an1_merged[an1_ind][1]:
                    for stat_matrix_ind_column in name_catalog_an2_merged[an2_ind][1]:
                        result_comparison.stat_matrix[an1_ind][an2_ind] += \
                            self.stat_matrix[stat_matrix_ind_line][stat_matrix_ind_column]

        result_comparison.name_catalog_an1 = [name[0] for name in name_catalog_an1_merged]
        result_comparison.name_catalog_an2 = [name[0] for name in name_catalog_an2_merged]

        # FileInfo actions BEGIN
        for file_an1 in self.analyzer1_info.info:
            file_to_attach = FileInfo(file=file_an1.file)
            for er_in_file_an1 in file_an1:
                ind = srch_list_ind(self.name_catalog_an1, er_in_file_an1.type)
                for name_merged_ind in range(len(name_catalog_an1_merged)):
                    if ind in name_catalog_an1_merged[name_merged_ind][1]:
                        file_to_attach.errors.append(ErrorInfo(lines=er_in_file_an1.lines,
                                                               type=name_catalog_an1_merged[name_merged_ind][0],
                                                               bindings=er_in_file_an1.bindings))
                        break

        for file_an2 in self.analyzer2_info.info:
            file_to_attach = FileInfo(file=file_an2.file)
            for er_in_file_an2 in file_an2:
                ind = srch_list_ind(self.name_catalog_an2, er_in_file_an2.type)
                for name_merged_ind in range(len(name_catalog_an2_merged)):
                    if ind in name_catalog_an2_merged[name_merged_ind][1]:
                        file_to_attach.errors.append(ErrorInfo(lines=er_in_file_an2.lines,
                                                               type=name_catalog_an2_merged[name_merged_ind][0],
                                                               bindings=er_in_file_an2.bindings))
                        break
        # FileInfo actions END
        return result_comparison

    def print_comparison(self, mode="stat"):
        if not self.check_both_FileInfo_format():
            return -1

        if mode == "stat":
            print_numpy(self.stat_matrix, self.name_catalog_an1, self.name_catalog_an2)
            return 0
        # FileInfo actions BEGIN
        if mode == "an1":
            only_analyzer1_errors = self.get_errors_only_in_analyzer_num(1)
            for file_info in only_analyzer1_errors.info:
                print(file_info)

                for error_info in file_info:
                    print(error_info)
            return 0

        if mode == "er2":
            only_analyzer2_errors = self.get_errors_only_in_analyzer_num(2)
            for file_info in only_analyzer2_errors.info:
                print(file_info)

                for error_info in file_info:
                    print(error_info)
            return 0

        if mode == "er_both":
            both_analyzers_errors = self.get_errors_in_all_analyzers()
            ind = 0
            for binding in both_analyzers_errors.info:
                print("binding number: {}".format(ind))
                ind += 1
                print(binding[0])
                print(binding[1])
            return 0
        # FileInfo actions END
        print("NO SUCH MODE")
        return -1

    def stat_matrix_fill_by_bindings(self):

        for file_info_an1 in self.analyzer1_info.info:
            for error_info_an1 in file_info_an1:

                name_catalog1_ind = srch_list_ind(self.name_catalog_an1, error_info_an1.type)
                self.stat_matrix[name_catalog1_ind, -1] += 1

                if not error_info_an1.has_bindings():
                    name_catalog1_ind = srch_list_ind(self.name_catalog_an1, error_info_an1.type)
                    self.stat_matrix[name_catalog1_ind, -2] += 1

                for binding in error_info_an1.bindings:
                    filename_to_search = file_info_an1.file
                    if binding.file:
                        filename_to_search = binding.file
                    file_info_an2 = self.analyzer2_info.search_by_file(filename_to_search)
                    error_info_an2 = file_info_an2[binding.ind]

                    name_catalog2_ind = srch_list_ind(self.name_catalog_an2, error_info_an2.type)

                    self.stat_matrix[name_catalog1_ind, name_catalog2_ind] += 1

        for file_info_an2 in self.analyzer2_info.info:
            for error_info_an2 in file_info_an2:

                name_catalog2_ind = srch_list_ind(self.name_catalog_an2, error_info_an2.type)
                self.stat_matrix[-1, name_catalog2_ind] += 1

                if not error_info_an2.has_bindings():
                    self.stat_matrix[-2, name_catalog2_ind] += 1

    def __subproc_fill_for_set_operations(self):
        result_comparison = Comparison()
        result_comparison.name_catalog_an1 = copy.deepcopy(self.name_catalog_an1)
        result_comparison.name_catalog_an2 = copy.deepcopy(self.name_catalog_an2)

        result_comparison.stat_matrix = np.zeros(self.stat_matrix.shape, dtype='int')
        result_comparison.stat_matrix[-1, :] = self.stat_matrix[-1, :]
        result_comparison.stat_matrix[:, -1] = self.stat_matrix[:, -1]
        result_comparison.stat_matrix[-2, -2] = -1

        result_comparison.analyzer1_info = AnalyzerInfo(analyzer_name=self.analyzer1_info.analyzer_name,
                                                        info_type=self.analyzer1_info.info_type)
        result_comparison.analyzer2_info = AnalyzerInfo(analyzer_name=self.analyzer2_info.analyzer_name,
                                                        info_type=self.analyzer2_info.info_type)

        return result_comparison

    def __subproc_comparison_union_form_info(self, another_comparison, result_comparison, analyzer_num):
        if analyzer_num == 1:
            self_analyzer_info = self.analyzer1_info
            another_comparison_analyzer_info = another_comparison.analyzer1_info
        else:
            self_analyzer_info = self.analyzer2_info
            another_comparison_analyzer_info = another_comparison.analyzer2_info

        for file_info_cmp1 in self_analyzer_info.info:
            file_info_to_add = FileInfo(file=file_info_cmp1.file)
            file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
            for error_info_ind in range(len(file_info_cmp1.errors)):
                bindings_to_add = copy.deepcopy(file_info_cmp1.errors[error_info_ind].bindings)
                for binding_cmp2 in file_info_cmp2.errors[error_info_ind].bindings:
                    if binding_cmp2 not in bindings_to_add:
                        bindings_to_add.append(binding_cmp2)
                file_info_to_add.append(ErrorInfo(lines=file_info_cmp1.errors[error_info_ind].lines,
                                                  type=file_info_cmp1.errors[error_info_ind].type,
                                                  bindings=bindings_to_add))
            if analyzer_num == 1:
                result_comparison.analyzer1_info.append(file_info_to_add)
            else:
                result_comparison.analyzer2_info.append(file_info_to_add)
        return 0

    def comparison_union(self, another_comparison):

        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN

        self.__subproc_comparison_union_form_info(another_comparison, result_comparison, 1)
        self.__subproc_comparison_union_form_info(another_comparison, result_comparison, 2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    def __same_error_extract_both(self, current_error_ind):
        result_list_an1 = []
        result_list_an2 = []
        current_error = self.error_list_both[current_error_ind]
        for error_ind in range(current_error_ind + 1, len(self.error_list_both)):
            error = self.error_list_both[error_ind]
            if current_error[0] != error[0]:
                break

            if current_error[1] == error[1] and \
               current_error[3] == error[3]:
                result_list_an1.append([error[2], error[4]])

            if current_error[2] == error[2] and \
               current_error[4] == error[4]:
                result_list_an2.append([error[1], error[3]])
        return result_list_an1, result_list_an2

    def __subproc_comparison_substraction_form_info(self, another_comparison, result_comparison, analyzer_num):
        if analyzer_num == 1:
            self_analyzer_info = self.analyzer1_info
            another_comparison_analyzer_info = another_comparison.analyzer1_info
        else:
            self_analyzer_info = self.analyzer2_info
            another_comparison_analyzer_info = another_comparison.analyzer2_info

        for file_info_cmp1 in self_analyzer_info.info:
            file_info_to_add = FileInfo(file=file_info_cmp1.file)
            file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
            for error_info_ind in range(len(file_info_cmp1.errors)):
                bindings_to_add = []
                for binding_cmp1 in file_info_cmp1[error_info_ind].bindings:
                    if binding_cmp1 not in file_info_cmp2[error_info_ind].bindings:
                        bindings_to_add.append(binding_cmp1)
                file_info_to_add.append(ErrorInfo(lines=file_info_cmp1[error_info_ind].lines,
                                                  type=file_info_cmp1[error_info_ind].type,
                                                  bindings=bindings_to_add))

            if analyzer_num == 1:
                result_comparison.analyzer1_info.append(file_info_to_add)
            else:
                result_comparison.analyzer2_info.append(file_info_to_add)

    def comparison_substraction(self, another_comparison):
        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN
        self.__subproc_comparison_substraction_form_info(another_comparison, result_comparison, analyzer_num=1)
        self.__subproc_comparison_substraction_form_info(another_comparison, result_comparison, analyzer_num=2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    def __subproc_comparison_intersection_form_info(self, another_comparison, result_comparison, analyzer_num):
        if analyzer_num == 1:
            self_analyzer_info = self.analyzer1_info
            another_comparison_analyzer_info = another_comparison.analyzer1_info
        else:
            self_analyzer_info = self.analyzer2_info
            another_comparison_analyzer_info = another_comparison.analyzer2_info

        for file_info_cmp1 in self_analyzer_info.info:
            file_info_to_add = FileInfo(file=file_info_cmp1.file)
            file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
            for error_info_ind in range(len(file_info_cmp1.errors)):
                bindings_to_add = []
                for binding_cmp1 in file_info_cmp1[error_info_ind].bindings:
                    if binding_cmp1 in file_info_cmp2[error_info_ind].bindings:
                        bindings_to_add.append(binding_cmp1)
                file_info_to_add.append(ErrorInfo(lines=file_info_cmp1.errors[error_info_ind].lines,
                                                  type=file_info_cmp1.errors[error_info_ind].type,
                                                  bindings=bindings_to_add))
            if analyzer_num == 1:
                result_comparison.analyzer1_info.append(file_info_to_add)
            else:
                result_comparison.analyzer2_info.append(file_info_to_add)
        return 0

    def comparison_intersection(self, another_comparison):
        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN
        self.__subproc_comparison_intersection_form_info(another_comparison, result_comparison, analyzer_num=1)
        self.__subproc_comparison_intersection_form_info(another_comparison, result_comparison, analyzer_num=2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    def heur_fill_for_heuristics(self, analyzer1_info: AnalyzerInfo, analyzer2_info: AnalyzerInfo):

        self.name_catalog_an1 = [warn[0] for warn in analyzer1_info.count_warnings()]
        self.name_catalog_an2 = [warn[0] for warn in analyzer2_info.count_warnings()]

        self.name_catalog_an1.append("ONLY_IN_ANALYZER2")
        self.name_catalog_an1.append("TOTAL_AMOUNT_AN2")

        self.name_catalog_an2.append("ONLY_IN_ANALYZER1")
        self.name_catalog_an2.append("TOTAL_AMOUNT_AN1")

        self.stat_matrix = np.zeros((len(self.name_catalog_an1), len(self.name_catalog_an2)), dtype="int")
        self.stat_matrix[-1][-1] = -1
        self.stat_matrix[-1][-2] = -1
        self.stat_matrix[-2][-1] = -1
        self.stat_matrix[-2][-2] = -1

        self.analyzer1_info = copy.deepcopy(analyzer1_info)
        self.analyzer2_info = copy.deepcopy(analyzer2_info)

        return 0

    def search_entities_in_lines(self, node: clang.cindex.Cursor, found_lines: list, result_set: set):
        #dump_ast(node)
        if node.kind == clang.cindex.CursorKind.VAR_DECL or \
           node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
           if node.location.line in found_lines:
            result_set.add(str(node.displayname))
        for c in node.get_children():
            self.search_entities_in_lines(c, found_lines, result_set)

    def present_entity_uses(self, node, lines_list, variable_set):
        if node.kind == clang.cindex.CursorKind.VAR_DECL or \
           node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            if node.location.line in lines_list:
                if str(node.displayname) in variable_set:
                    return True
        for c in node.get_children():
            if self.present_entity_uses(c, lines_list, variable_set):
                return True
        return False

    def analyze_comparison_buffer_overflow(self):

        if not self.check_both_FileInfo_format():
            return -1

        list_buf_overflow_types_an1 = type_groups[self.analyzer1_info.analyzer_name]["Buffer_overflow"]
        list_buf_overflow_types_an2 = type_groups[self.analyzer2_info.analyzer_name]["Buffer_overflow"]

        analyzer1_info_res = AnalyzerInfo(analyzer_name=self.analyzer1_info.analyzer_name,
                                          info_type=self.analyzer1_info.info_type)
        analyzer2_info_res = AnalyzerInfo(analyzer_name=self.analyzer2_info.analyzer_name,
                                          info_type=self.analyzer2_info.info_type)

    def analyze_comparison_buffer_overflow_old(self):

        list_buf_overflow_types_an1 = type_groups[self.analyzer1_info.analyzer_name]["Buffer_overflow"]
        list_buf_overflow_types_an2 = type_groups[self.analyzer2_info.analyzer_name]["Buffer_overflow"]

        found_corresponding_er_both_an1 = np.zeros((len(self.error_list_an1)), dtype=np.bool)
        found_corresponding_er_both_an2 = np.zeros((len(self.error_list_an2)), dtype=np.bool)

        error_list_an1_res = []
        error_list_an2_res = []
        error_list_both_res = []

        for found_error_an1 in self.error_list_both:
            if found_error_an1[3] in list_buf_overflow_types_an1:
                found_filename = found_error_an1[0]
                found_lines = found_error_an1[1]

                same_file_error_ind_list_an1 = []
                same_file_error_list_an1 = []

                same_file_error_ind_list_an2 = []
                same_file_error_list_an2 = []

                for unfound_error_an1_ind in range(len(self.error_list_an1)):
                    if self.error_list_an1[unfound_error_an1_ind][0] == found_filename and \
                       self.error_list_an1[unfound_error_an1_ind][2] in list_buf_overflow_types_an1:
                        same_file_error_ind_list_an1.append(unfound_error_an1_ind)
                        same_file_error_list_an1.append(self.error_list_an1[unfound_error_an1_ind])

                for unfound_error_an2_ind in range(len(self.error_list_an2)):
                    if self.error_list_an2[unfound_error_an2_ind][0] == found_filename and \
                       self.error_list_an2[unfound_error_an2_ind][2] in list_buf_overflow_types_an2:
                        same_file_error_ind_list_an2.append(unfound_error_an2_ind)
                        same_file_error_list_an2.append(self.error_list_an1[unfound_error_an2_ind])

                index = clang.cindex.Index.create()
                translation_unit = index.parse(found_filename, args=["-std=c++17"])
                cursor = translation_unit.cursor

                variable_set = set()
                self.search_entities_in_lines(cursor, found_lines, variable_set)

                for er_ind in range(len(same_file_error_list_an1)):
                    if self.present_entity_uses(cursor, same_file_error_list_an1[er_ind][1], variable_set):

                        error_name1 = same_file_error_list_an1[er_ind][2]
                        error_name2 = found_error_an1[4]

                        ind1 = srch_list_ind(self.name_catalog_an1, error_name1)
                        ind2 = srch_list_ind(self.name_catalog_an2, error_name2)

                        if not found_corresponding_er_both_an1[same_file_error_ind_list_an1[er_ind]]:
                            self.stat_matrix[ind1][-2] -= 1
                            found_corresponding_er_both_an1[same_file_error_ind_list_an1[er_ind]] = True

                        self.stat_matrix[ind1][ind2] += 1

                        error_list_both_res.append([found_filename,
                                                    same_file_error_list_an1[er_ind][1],
                                                    found_error_an1[2],
                                                    error_name1,
                                                    error_name2])

                for er_ind in range(len(same_file_error_list_an2)):
                    if self.present_entity_uses(cursor, same_file_error_list_an2[er_ind][1], variable_set):

                        error_name1 = found_error_an1[3]
                        error_name2 = same_file_error_list_an2[er_ind][2]

                        ind1 = srch_list_ind(self.name_catalog_an1, error_name1)
                        ind2 = srch_list_ind(self.name_catalog_an2, error_name2)

                        if not found_corresponding_er_both_an2[same_file_error_ind_list_an2[er_ind]]:
                            self.stat_matrix[-2][ind2] -= 1
                            found_corresponding_er_both_an2[same_file_error_ind_list_an2[er_ind]] = True

                        self.stat_matrix[ind1][ind2] += 1

                        error_list_both_res.append([found_filename,
                                                    found_error_an1[1],
                                                    same_file_error_list_an2[er_ind][1],
                                                    error_name1,
                                                    error_name2])

        for error_an1_ind in range(len(self.error_list_an1)):
            if not found_corresponding_er_both_an1[error_an1_ind]:
                error_list_an1_res.append(self.error_list_an1[error_an1_ind])

        for error_an2_ind in range(len(self.error_list_an2)):
            if not found_corresponding_er_both_an2[error_an2_ind]:
                error_list_an2_res.append(self.error_list_an2[error_an2_ind])

        self.error_list_an1 = error_list_an1_res
        self.error_list_an2 = error_list_an2_res
        self.error_list_both = error_list_both_res

        return


