from operator import itemgetter

from allLibs import *
from euristics.Lines import lines, np
import copy

from projectLib.Common import srch_ind, srch_list_ind, save_list, load_list, print_numpy


class Comparison:

    def __init__(self):
        self.name_catalog_an1 = []
        self.name_catalog_an2 = []
        self.stat_matrix = None
        self.error_list_an1 = []
        self.error_list_an2 = []
        self.error_list_both = []

    def comparison_fill(self, orig):
        self.name_catalog_an1 = orig.name_catalog_an1
        self.name_catalog_an2 = orig.name_catalog_an2
        self.stat_matrix = orig.stat_matrix
        self.error_list_an1 = orig.error_list_an1
        self.error_list_an2 = orig.error_list_an2
        self.error_list_both = orig.error_list_both

    def compare_analyzers_info(self, analyzer1_info, analyzer2_info, eur, eur_params):

        if eur == "lines":
            if len(eur_params) == 1:
                self.comparison_fill(lines(analyzer1_info, analyzer2_info, eur_params))

        return None

    def save_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/stat_matrix" + str(comparison_id) + ".npy"
        error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(comparison_id) + ".data"
        error_list_an2_path = res_dir + "/error_list_an2_ind" + str(comparison_id) + ".data"
        error_list_both_path = res_dir + "/error_list_both_ind" + str(comparison_id) + ".data"

        save_list(self.name_catalog_an1, name_catalog_an1_path)
        save_list(self.name_catalog_an2, name_catalog_an2_path)
        np.save(stat_matrix_path, self.stat_matrix)
        save_list(self.error_list_an1, error_list_an1_path)
        save_list(self.error_list_an2, error_list_an2_path)
        save_list(self.error_list_both, error_list_both_path)

        return 0

    def load_comparison(self, res_dir, generation_ind):

        name_catalog_an1_path = res_dir + "/name_catalog_an1_ind" + str(generation_ind) + ".data"
        name_catalog_an2_path = res_dir + "/name_catalog_an2_ind" + str(generation_ind) + ".data"
        stat_matrix_path = res_dir + "/stat_matrix" + str(generation_ind) + ".npy"
        error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(generation_ind) + ".data"
        error_list_an2_path = res_dir + "/error_list_an2_ind" + str(generation_ind) + ".data"
        error_list_both_path = res_dir + "/error_list_both_ind" + str(generation_ind) + ".data"

        self.name_catalog_an1 = load_list(name_catalog_an1_path)
        self.name_catalog_an2 = load_list(name_catalog_an2_path)
        self.stat_matrix = np.load(stat_matrix_path)
        self.error_list_an1 = load_list(error_list_an1_path)
        self.error_list_an2 = load_list(error_list_an2_path)
        self.error_list_both = load_list(error_list_both_path)

        return 0

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

        result_comparison.error_list_both = copy.deepcopy(self.error_list_both)

        result_comparison.stat_matrix = np.zeros(self.stat_matrix.shape, dtype='int')
        result_comparison.stat_matrix[-1, :] = self.stat_matrix[-1, :]
        result_comparison.stat_matrix[:, -1] = self.stat_matrix[:, -1]

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
            er_both2_present_in_union = True
            for er_both1 in self.error_list_both:
                if er_both1 == er_both2:
                    er_both2_present_in_union = True
                    break
            if not er_both2_present_in_union:
                result_comparison.error_list_both.append(er_both2)
        result_comparison.error_list_both.sort(key=itemgetter(0))

        for er_both in result_comparison.error_list_both:
            ind1 = srch_list_ind(self.name_catalog_an1, er_both[2])
            ind2 = srch_list_ind(self.name_catalog_an2, er_both[3])
            result_comparison.stat_matrix[ind1][ind2] += 1

        return result_comparison

    def comparison_union1(self, comparison1, comparison2):
        name_catalog1 = comparison1[0]
        name_catalog2 = comparison1[1]

        er_an1_comp1 = comparison1[3]
        er_an2_comp1 = comparison1[4]
        er_an_both_comp1 = comparison1[5]

        er_an1_comp2 = comparison2[3]
        er_an2_comp2 = comparison2[4]
        er_an_both_comp2 = comparison2[5]

        er_an1_union = []
        er_an2_union = []
        er_both_union = copy.deepcopy(er_an_both_comp1)

        stat_matrix_union = np.zeros(comparison1[2].shape, dtype='int')
        stat_matrix_union[-1, :] = comparison1[2][-1, :]
        stat_matrix_union[:, -1] = comparison1[2][:, -1]

        for er_an1 in er_an1_comp1:
            if er_an1 in er_an1_comp2:
                er_an1_union.append(er_an1)
        er_an1_union.sort(key=itemgetter(0))

        for er_an1 in er_an1_union:
            ind = srch_list_ind(name_catalog1, er_an1[2])
            stat_matrix_union[ind, -2] += 1

        for er_an2 in er_an2_comp1:
            if er_an2 in er_an2_comp2:
                er_an2_union.append(er_an2)
        er_an2_union.sort(key=itemgetter(0))

        for er_an2 in er_an2_union:
            ind = srch_list_ind(name_catalog2, er_an2[2])
            stat_matrix_union[-2, ind] += 1

        for er_both2 in er_an_both_comp2:
            er_both2_present_in_union = True
            for er_both1 in er_an_both_comp1:
                if er_both1[0] == er_both2[0] and \
                    er_both1[2] == er_both2[2] and \
                    er_both1[3] == er_both2[3] and \
                    len(set(er_both1[1]).intersection(er_both2[1])):
                        er_both2_present_in_union = True
                        break
            if not er_both2_present_in_union:
                er_both_union.append(er_both2)
        er_both_union.sort(key=itemgetter(0))

        for er_both in er_both_union:
            ind1 = srch_list_ind(name_catalog1, er_both[2])
            ind2 = srch_list_ind(name_catalog2, er_both[3])
            stat_matrix_union[ind1][ind2] += 1

        return name_catalog1, name_catalog2, stat_matrix_union, \
                er_an1_union, er_an2_union, er_both_union

    def comparison_intersection(self, comparison1, comparison2):
        name_catalog1 = comparison1[0]
        name_catalog2 = comparison1[1]

        er_an1_comp1 = comparison1[3]
        er_an2_comp1 = comparison1[4]
        er_an_both_comp1 = comparison1[5]

        er_an1_comp2 = comparison2[3]
        er_an2_comp2 = comparison2[4]
        er_an_both_comp2 = comparison2[5]

        er_an1_intersection = copy.deepcopy(er_an1_comp1)
        er_an2_intersection = copy.deepcopy(er_an2_comp1)
        er_both_intersection = []

        stat_matrix_intersection = np.zeros(comparison1[2].shape, dtype='int')
        stat_matrix_intersection[-1, :] = comparison1[2][-1, :]
        stat_matrix_intersection[:, -1] = comparison1[2][:, -1]

        for er_an1 in er_an1_comp2:
            if er_an1 not in er_an1_intersection:
                er_an1_intersection.append(er_an1)
        er_an1_intersection.sort(key=itemgetter(0))

        for er_an1 in er_an1_intersection:
            ind = srch_list_ind(name_catalog1, er_an1[2])
            stat_matrix_intersection[ind, -2] += 1

        for er_an2 in er_an2_comp2:
            if er_an2 not in er_an2_intersection:
                er_an2_intersection.append(er_an2)
        er_an2_intersection.sort(key=itemgetter(0))

        for er_an2 in er_an2_intersection:
            ind = srch_list_ind(name_catalog2, er_an2[2])
            stat_matrix_intersection[-2, ind] += 1

        for er_both1 in er_an_both_comp1:
            for er_both2 in er_an_both_comp2:
                if er_both1[0] == er_both2[0] and \
                er_both1[2] == er_both2[2] and \
                er_both1[3] == er_both2[3] and \
                len(set(er_both1[1]).intersection(er_both2[1])):
                    er_both_intersection.append(er_both1)
                    ind1 = srch_list_ind(name_catalog1, er_both1[2])
                    ind2 = srch_list_ind(name_catalog2, er_both1[3])
                    stat_matrix_intersection[ind1][ind2] += 1
        er_both_intersection.sort(key=itemgetter(0))

        for er_both in er_both_intersection:
            ind1 = srch_list_ind(name_catalog1, er_both[2])
            ind2 = srch_list_ind(name_catalog2, er_both[3])
            stat_matrix_intersection[ind1][ind2] += 1


        return comparison1[0], comparison1[1], stat_matrix_intersection, er_an1_intersection, er_an2_intersection, er_both_intersection


