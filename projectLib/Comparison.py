from allLibs import *
from euristics.lines import lines, np
import copy

from projectLib.common import srch_ind


def compare_analyzers_info(analyzer1_info, analyzer2_info, eur, eur_params):

    if eur == "lines":
        if len(eur_params) == 1:
            return lines(analyzer1_info, analyzer2_info, eur_params)

    return None


def comparison_union(comparison1, comparison2):
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


def comparison_intersection(comparison1, comparison2):
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


