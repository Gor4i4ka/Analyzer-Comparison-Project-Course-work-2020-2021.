from lxml import etree as et
from lxml import html as ht
from operator import itemgetter

import bs4
import re

# Internal imports
from projectLib.Common import save_list, load_list, print_list, juliet_shorten, remove_parent_dirs


class Info:

    def __init__(self):
        self.analyzer_name = ""
        self.info = []
        self.info_type = ""

    def mine_info(self, analyzer_name, xml_path, dir_list, defect_type_list, output_mode="combined"):

        # File check re expr
        re_expr = ""
        len_def = len(dir_list)
        for ind in range(len_def):
            re_expr += dir_list[ind] + "*"
            if ind != (len_def - 1):
                re_expr += "|.*"

        # Initial parsing
        manifest_tree = et.parse(xml_path, parser=et.XMLParser(remove_blank_text=True))
        manifest_root = ht.tostring(manifest_tree)
        manifest_soup = bs4.BeautifulSoup(manifest_root, features="lxml")

        # Choose the analyzer
        if analyzer_name == "juliet":
            self.analyzer_name = analyzer_name
            analyzer_output = self.__juliet_mine(re_expr, manifest_soup, defect_type_list)
        elif analyzer_name == "svace":
            self.analyzer_name = analyzer_name
            analyzer_output = self.__svace_mine(re_expr, manifest_soup, defect_type_list)
        else:
            print("NO SUCH ANALYZER")
            return -1

        # PostProcess analyzer's output
        analyzer_output.sort(key=itemgetter(0))

        if output_mode == "separated":
            self.__separated_postproc(analyzer_output)
            return 0
        elif output_mode == "combined":
            self.__combined_postproc(analyzer_output)
            return 0
        else:
            print("NO SUCH OUTPUT MODE")
            return -1

    def save_info(self, path):
        save_list(self.analyzer_name, path + "/analyzer_name.data")
        save_list(self.info, path + "/info.data")
        save_list(self.info_type, path + "/info_type.data")
        return 0

    def load_info(self, path):
        self.analyzer_name = load_list(path + "/analyzer_name.data")
        self.info = load_list(path + "/info.data")
        self.info_type = load_list(path + "/info_type.data")
        return 0

    def print_info(self):
        print_list(self.info)
        return 0

    def count_warnings(self):
        warning_list = []
        for file in self.info:
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

    def __svace_mine(self, re_expr, manifest_soup, defect_type_list):
        result_list = []

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
            warning = [remove_parent_dirs(warn["file"]), None, warn['warnclass']]
            list_warn_sv.append(warning)

        loc_warn_sv.sort(key=itemgetter(0))
        list_warn_sv.sort(key=itemgetter(0))
        for ind in range(len(list_warn_sv)):
            list_warn_sv[ind][1] = loc_warn_sv[ind][1]
            if (not defect_type_list) or (list_warn_sv[ind][2] in defect_type_list):
                result_list.append(list_warn_sv[ind])

        return result_list

    def __juliet_mine(self, re_expr, manifest_soup, defect_type_list):
        result_list = []
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
        return result_list

    def __combined_postproc(self, analyzer_output):
        self.info_type = "combined"

        for el in analyzer_output:
            if len(self.info) == 0 or el[0] != self.info[-1][0]:
                self.info.append([el[0], [el[1]], [el[2]]])
            else:
                self.info[-1][1].append(el[1])
                self.info[-1][2].append(el[2])

        return 0

    def __separated_postproc(self, analyzer_output):
        self.info_type = "separated"

        for el in analyzer_output:
            self.info.append(el)

        return 0

