from operator import itemgetter

import numpy as np
import copy
import clang
import clang.cindex

# Internal imports
from projectLib.Common import srch_list_ind, save_list, load_list, print_numpy, dump_ast
from projectLib.Info import Info
from projectLib.ProjectConfig import type_groups


class Comparison:

    def __init__(self):
        self.name_catalog_an1 = []
        self.name_catalog_an2 = []
        self.stat_matrix = None
        self.error_list_an1 = []
        self.error_list_an2 = []
        self.error_list_both = []

        self.analyzer1_name = ""
        self.analyzer2_name = ""

    def comparison_copy(self, orig):
        self.name_catalog_an1 = orig.name_catalog_an1
        self.name_catalog_an2 = orig.name_catalog_an2
        self.stat_matrix = orig.stat_matrix
        self.error_list_an1 = orig.error_list_an1
        self.error_list_an2 = orig.error_list_an2
        self.error_list_both = orig.error_list_both

        self.analyzer1_name = orig.analyzer1_name
        self.analyzer2_name = orig.analyzer2_name

    def save_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/stat_matrix" + str(comparison_id) + ".npy"
        error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(comparison_id) + ".data"
        error_list_an2_path = res_dir + "/error_list_an2_ind" + str(comparison_id) + ".data"
        error_list_both_path = res_dir + "/error_list_both_ind" + str(comparison_id) + ".data"
        analyzer1_name_path = res_dir + "/analyzer1_name_ind" + str(comparison_id) + ".data"
        analyzer2_name_path = res_dir + "/analyzer2_name_ind" + str(comparison_id) + ".data"

        save_list(self.name_catalog_an1, name_catalog_an1_path)
        save_list(self.name_catalog_an2, name_catalog_an2_path)
        np.save(stat_matrix_path, self.stat_matrix)
        save_list(self.error_list_an1, error_list_an1_path)
        save_list(self.error_list_an2, error_list_an2_path)
        save_list(self.error_list_both, error_list_both_path)
        save_list(self.analyzer1_name, analyzer1_name_path)
        save_list(self.analyzer2_name, analyzer2_name_path)

        return 0

    def load_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/stat_matrix" + str(comparison_id) + ".npy"
        error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(comparison_id) + ".data"
        error_list_an2_path = res_dir + "/error_list_an2_ind" + str(comparison_id) + ".data"
        error_list_both_path = res_dir + "/error_list_both_ind" + str(comparison_id) + ".data"
        analyzer1_name_path = res_dir + "/analyzer1_name_ind" + str(comparison_id) + ".data"
        analyzer2_name_path = res_dir + "/analyzer2_name_ind" + str(comparison_id) + ".data"

        self.name_catalog_an1 = load_list(name_catalog_an1_path)
        self.name_catalog_an2 = load_list(name_catalog_an2_path)
        self.stat_matrix = np.load(stat_matrix_path)
        self.error_list_an1 = load_list(error_list_an1_path)
        self.error_list_an2 = load_list(error_list_an2_path)
        self.error_list_both = load_list(error_list_both_path)
        self.analyzer1_name = load_list(analyzer1_name_path)
        self.analyzer2_name = load_list(analyzer2_name_path)

        return 0

    def group_comparison(self, an1_type_groups, an2_type_groups):
        result_comparison = Comparison()

        result_comparison.stat_matrix = np.zeros((self.stat_matrix.shape[0] - an1_type_groups["TOTAL_COMPRESSION"],
                                                  self.stat_matrix.shape[1] - an2_type_groups["TOTAL_COMPRESSION"]),
                                                  dtype=np.int)

        result_comparison.analyzer1_name = self.analyzer1_name
        result_comparison.analyzer2_name = self.analyzer2_name

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

        for er_an1 in self.error_list_an1:
            error_name = er_an1[2]
            ind = srch_list_ind(self.name_catalog_an1, error_name)
            for name_merged_ind in range(len(name_catalog_an1_merged)):
                if ind in name_catalog_an1_merged[name_merged_ind][1]:
                    result_comparison.error_list_an1.append([er_an1[0],
                                                            er_an1[1],
                                                            name_catalog_an1_merged[name_merged_ind][0]])

        for er_an2 in self.error_list_an2:
            error_name = er_an2[2]
            ind = srch_list_ind(self.name_catalog_an2, error_name)
            for name_merged_ind in range(len(name_catalog_an2_merged)):
                if ind in name_catalog_an2_merged[name_merged_ind][1]:
                    result_comparison.error_list_an2.append([er_an2[0],
                                                            er_an2[1],
                                                            name_catalog_an2_merged[name_merged_ind][0]])
                    break

        for er_both in self.error_list_both:
            error_name1 = er_both[3]
            ind1 = srch_list_ind(self.name_catalog_an1, error_name1)
            error_name2 = er_both[4]
            ind2 = srch_list_ind(self.name_catalog_an2, error_name2)

            error_name_merged1 = None
            error_name_merged2 = None

            for name_merged_ind in range(len(name_catalog_an1_merged)):
                if ind1 in name_catalog_an1_merged[name_merged_ind][1]:
                    error_name_merged1 = name_catalog_an1_merged[name_merged_ind][0]
                    break

            for name_merged_ind in range(len(name_catalog_an2_merged)):
                if ind2 in name_catalog_an2_merged[name_merged_ind][1]:
                    error_name_merged2 = name_catalog_an2_merged[name_merged_ind][0]
                    break

            result_comparison.error_list_both.append([er_both[0],
                                                      er_both[1],
                                                      er_both[2],
                                                      error_name_merged1,
                                                      error_name_merged2])

        return result_comparison

    def print_comparison(self, mode="stat"):
        if mode == "stat":
            print_numpy(self.stat_matrix, self.name_catalog_an1, self.name_catalog_an2)
            return
        error_list = None
        if mode == "er1":
            error_list = self.error_list_an1
        if mode == "er2":
            error_list = self.error_list_an2
        if mode == "er_both":
            error_list = self.error_list_both

        if error_list:
            for el in error_list:
                print(el)

        return 0

    def comparison_union(self, another_comparison):

        result_comparison = Comparison()
        result_comparison.name_catalog_an1 = copy.deepcopy(self.name_catalog_an1)
        result_comparison.name_catalog_an2 = copy.deepcopy(self.name_catalog_an2)

        result_comparison.error_list_both = copy.deepcopy(self.error_list_both)

        result_comparison.stat_matrix = np.zeros(self.stat_matrix.shape, dtype='int')
        result_comparison.stat_matrix[-1, :] = self.stat_matrix[-1, :]
        result_comparison.stat_matrix[:, -1] = self.stat_matrix[:, -1]
        result_comparison.stat_matrix[-2, -2] = -1

        result_comparison.analyzer1_name = self.analyzer1_name
        result_comparison.analyzer2_name = self.analyzer2_name

        for er_an1 in self.error_list_an1:
            if er_an1 in another_comparison.error_list_an1:
                result_comparison.error_list_an1.append(er_an1)
        result_comparison.error_list_an1.sort(key=itemgetter(0))

        for er_an1 in result_comparison.error_list_an1:
            ind = srch_list_ind(self.name_catalog_an1, er_an1[2])
            result_comparison.stat_matrix[ind, -2] += 1

        for er_an2 in self.error_list_an2:
            if er_an2 in another_comparison.error_list_an2:
                result_comparison.error_list_an2.append(er_an2)
        result_comparison.error_list_an2.sort(key=itemgetter(0))

        for er_an2 in result_comparison.error_list_an2:
            ind = srch_list_ind(self.name_catalog_an2, er_an2[2])
            result_comparison.stat_matrix[-2, ind] += 1

        for er_both2 in another_comparison.error_list_both:
            er_both2_present_in_union = False
            for er_both1 in self.error_list_both:
                if er_both1 == er_both2:
                    er_both2_present_in_union = True
                    break
            if not er_both2_present_in_union:
                result_comparison.error_list_both.append(er_both2)
        result_comparison.error_list_both.sort(key=itemgetter(0))

        for er_both in result_comparison.error_list_both:
            ind1 = srch_list_ind(self.name_catalog_an1, er_both[3])
            ind2 = srch_list_ind(self.name_catalog_an2, er_both[4])
            result_comparison.stat_matrix[ind1][ind2] += 1

        return result_comparison

    def comparison_intersection(self, another_comparison):
        result_comparison = Comparison()
        result_comparison.name_catalog_an1 = copy.deepcopy(self.name_catalog_an1)
        result_comparison.name_catalog_an2 = copy.deepcopy(self.name_catalog_an2)

        result_comparison.error_list_an1 = copy.deepcopy(self.error_list_an1)
        result_comparison.error_list_an2 = copy.deepcopy(self.error_list_an2)

        result_comparison.stat_matrix = np.zeros(self.stat_matrix.shape, dtype='int')
        result_comparison.stat_matrix[-1, :] = self.stat_matrix[-1, :]
        result_comparison.stat_matrix[:, -1] = self.stat_matrix[:, -1]
        result_comparison.stat_matrix[-2, -2] = -1

        result_comparison.analyzer1_name = self.analyzer1_name
        result_comparison.analyzer2_name = self.analyzer2_name

        for er_an1 in another_comparison.error_list_an1:
            if er_an1 not in result_comparison.error_list_an1:
                result_comparison.error_list_an1.append(er_an1)
        result_comparison.error_list_an1.sort(key=itemgetter(0))

        for er_an1 in result_comparison.error_list_an1:
            ind = srch_list_ind(result_comparison.name_catalog_an1, er_an1[2])
            result_comparison.stat_matrix[ind, -2] += 1

        for er_an2 in another_comparison.error_list_an2:
            if er_an2 not in result_comparison.error_list_an2:
                result_comparison.error_list_an2.append(er_an2)
        result_comparison.error_list_an2.sort(key=itemgetter(0))

        for er_an2 in result_comparison.error_list_an2:
            ind = srch_list_ind(result_comparison.name_catalog_an2, er_an2[2])
            result_comparison.stat_matrix[-2, ind] += 1

        for er_both1 in self.error_list_both:
            for er_both2 in another_comparison.error_list_both:
                if er_both1 == er_both2:
                    result_comparison.error_list_both.append(er_both1)
                    # ind1 = srch_list_ind(result_comparison.name_catalog_an1, er_both1[2])
                    # ind2 = srch_list_ind(result_comparison.name_catalog_an2, er_both1[3])
                    # result_comparison.stat_matrix[ind1][ind2] += 1
                    break
        result_comparison.error_list_both.sort(key=itemgetter(0))

        for er_both in result_comparison.error_list_both:
            ind1 = srch_list_ind(result_comparison.name_catalog_an1, er_both[3])
            ind2 = srch_list_ind(result_comparison.name_catalog_an2, er_both[4])
            result_comparison.stat_matrix[ind1][ind2] += 1

        return result_comparison

    def fill_for_euristics(self, analyzer1_info: Info, analyzer2_info: Info):

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

        self.error_list_both = []
        self.error_list_an1 = []
        self.error_list_an2 = []

        self.analyzer1_name = analyzer1_info.analyzer_name
        self.analyzer2_name = analyzer2_info.analyzer_name

        return 0

    def compare_list_generation(self, analyzer1_info: Info, analyzer2_info: Info):

        analyzer1_info_field = analyzer1_info.info
        analyzer2_info_field = analyzer2_info.info

        cmp_list = []

        found_counterpart_an2 = np.zeros((len(analyzer2_info_field)), dtype=np.bool)
        for defect1_file_ind in range(len(analyzer1_info_field)):
            found_counterpart_an1 = False

            for err_ind in range(len(analyzer1_info_field[defect1_file_ind][2])):
                self.stat_matrix[srch_list_ind(self.name_catalog_an1,
                                               analyzer1_info_field[defect1_file_ind][2][err_ind])][-1] += 1

            for defect2_file_ind in range(len(analyzer2_info_field)):
                if analyzer1_info_field[defect1_file_ind][0] == analyzer2_info_field[defect2_file_ind][0]:
                    cmp_list.append([analyzer1_info_field[defect1_file_ind][0],
                                     analyzer1_info_field[defect1_file_ind][1],
                                     analyzer2_info_field[defect2_file_ind][1],
                                     analyzer1_info_field[defect1_file_ind][2],
                                     analyzer2_info_field[defect2_file_ind][2]])

                    found_counterpart_an1 = True
                    found_counterpart_an2[defect2_file_ind] = True
                    break

            if not found_counterpart_an1:
                for err_ind in range(len(analyzer1_info_field[defect1_file_ind][2])):
                    self.stat_matrix[srch_list_ind(self.name_catalog_an1,
                                                   analyzer1_info_field[defect1_file_ind][2][err_ind])][-2] += 1
                    self.error_list_an1.append([analyzer1_info_field[defect1_file_ind][0],
                                                analyzer1_info_field[defect1_file_ind][1][err_ind],
                                                analyzer1_info_field[defect1_file_ind][2][err_ind]]
                                                )

        for defect2_file_ind2 in range(found_counterpart_an2.shape[0]):

            for err_ind in range(len(analyzer2_info_field[defect2_file_ind2][2])):
                ind2 = srch_list_ind(self.name_catalog_an2,
                                     analyzer2_info_field[defect2_file_ind2][2][err_ind])
                self.stat_matrix[-1][ind2] += 1

            if not found_counterpart_an2[defect2_file_ind2]:
                for err_ind in range(len(analyzer2_info_field[defect2_file_ind2][2])):
                    ind2 = srch_list_ind(self.name_catalog_an2,
                                         analyzer2_info_field[defect2_file_ind2][2][err_ind])
                    self.stat_matrix[-2][ind2] += 1
                    self.error_list_an2.append([analyzer2_info_field[defect2_file_ind2][0],
                                                analyzer2_info_field[defect2_file_ind2][1][err_ind],
                                                analyzer2_info_field[defect2_file_ind2][2][err_ind]]
                                                )

        return cmp_list

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

        list_buf_overflow_types_an1 = type_groups[self.analyzer1_name]["Buffer_overflow"]
        list_buf_overflow_types_an2 = type_groups[self.analyzer2_name]["Buffer_overflow"]

        error_list_both_res = copy.deepcopy(self.error_list_both)
        error_list_an1_res = []
        error_list_an2_res = []

        found_corresponding_er_both_an1 = np.zeros((len(self.error_list_an1)), dtype=np.bool)
        found_corresponding_er_both_an2 = np.zeros((len(self.error_list_an2)), dtype=np.bool)

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
