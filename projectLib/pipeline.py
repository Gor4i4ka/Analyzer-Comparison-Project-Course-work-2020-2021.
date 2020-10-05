from allLibs import *
from euristics.lines import lines, np
import copy

from projectLib.common import srch_ind


def mine_info(analyzer_name, xml_path, dir_list, defect_type_list):
    # 1)file 2)info 3)error type
    result_list = []

    ### Initial parsing
    manifest_tree = et.parse(xml_path, parser=et.XMLParser(remove_blank_text=True))
    manifest_root = ht.tostring(manifest_tree)
    manifest_soup = bs4.BeautifulSoup(manifest_root, features="lxml")

    ### File check re expr
    re_expr = ""
    len_def = len(dir_list)
    for ind in range(len_def):
        re_expr += dir_list[ind] + "*"
        if (ind != (len_def - 1)):
            re_expr += "|.*"

    ############################
    #########JULIET#############
    ############################

    if analyzer_name == "juliet":

        testcases = manifest_soup.find_all("testcase")

        for case in testcases:
            testcase_list = []
            border = 0
            found = case.find_all(attrs={"path": re.compile(re_expr)})
            for file in found:

                has_flaw = False
                testcase_list.append([file["path"], [], juliet_shorten(file["path"])])
                flaws = file.find_all("flaw")
                for flaw in flaws:
                    has_flaw = True
                    for ind in range(border, len(testcase_list)):
                        testcase_list[ind][1].append(int(flaw["line"]))
                if has_flaw:
                    border = len(testcase_list)

            for file in testcase_list:
                if len(file[1]):
                    result_list.append(file)

    ############################
    #########SVACE#############
    ############################

    if analyzer_name == "svace":
        list_warn_sv = []
        loc_warn_sv = []

        found = manifest_soup.find_all("warninfo", attrs={"file": re.compile(re_expr)})
        foundloc = manifest_soup.find_all("warninfoex")

        for warnloc in foundloc:


            loc_warn = []
            loc_lines = []
            name = ""

            buffer_found = warnloc.find_all("roletraceinfo")

            for trace in buffer_found:
                if trace["role"] != "counter-example":
                    for locinf in trace.find_all("locinfo", attrs={"file": re.compile(re_expr)}):
                        if name == "":
                            name = remove_parent_dirs(locinf["file"])
                            loc_warn.append(name)
                        loc_lines.append(int(locinf["line"]))

            if len(loc_warn) > 0:
                loc_warn.append(loc_lines)
                loc_warn_sv.append(loc_warn)

        for warn in found:
            warning = []
            warning.append(remove_parent_dirs(warn["file"]))
            warning.append(None)
            warning.append(warn['warnclass'])
            list_warn_sv.append(warning)

        loc_warn_sv.sort(key=itemgetter(0))
        list_warn_sv.sort(key=itemgetter(0))
        for ind in range(len(list_warn_sv)):
            list_warn_sv[ind][1] = loc_warn_sv[ind][1]
            if (not defect_type_list) or (list_warn_sv[ind][2] in defect_type_list):
                result_list.append(list_warn_sv[ind])

    ############################
    #########COMMON#############
    ############################

    result_list.sort(key=itemgetter(0))

    res = []

    for el in result_list:
        if len(res) == 0 or el[0] != res[-1][0]:
            res.append([el[0], [el[1]], [el[2]]])
        else:
            res[-1][1].append(el[1])
            res[-1][2].append(el[2])

    return res


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


