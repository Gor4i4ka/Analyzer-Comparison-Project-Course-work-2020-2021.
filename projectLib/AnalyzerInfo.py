from lxml import etree as et
from lxml import html as ht
from operator import itemgetter

import bs4
import re
import copy

# Internal imports
from Common import save_list, load_list
from development.developmentTools.JulietSpecific.JulietSpecificCommon import find_in_juliet, juliet_shorten
from projectLib.ErrorInfo import ErrorInfo
from projectLib.FileInfo import FileInfo


class AnalyzerInfo:

    def __init__(self, analyzer_name="", info=[], info_type=""):
        self.analyzer_name = copy.deepcopy(analyzer_name)
        self.info = copy.deepcopy(info)
        self.info_type = copy.deepcopy(info_type)

    # Data structure operations BEGIN

    def append(self, element):
        self.info.append(copy.deepcopy(element))

    def remove(self, value):
        self.info.remove(value)

    def search_by_file(self, filename: str):
        if self.info_type == "FileInfo":
            for file in self.info:
                if file.file == filename:
                    return file
            return -1
        if self.info_type == "ErrorInfo":
            error_list = []
            for error in self.info:
                if error.file == filename:
                    error_list.append(error)

            if len(error_list) == 0:
                return -1
            return error_list
        print("NO SUCH info_type")
        return -2

    def __getitem__(self, item):
        return self.info[item]

    def __setitem__(self, key, value):
        self.info[key] = value
        return 0

    def __eq__(self, other):
        if self.info == other.info:
            return True
        return False

    def __len__(self):
        return len(self.info)

    # Data structure operations END

    # I/O Operations BEGIN

    def save_info(self, path, info_ind):
        save_list(self.analyzer_name, path + "/inf_analyzer_name_ind" + str(info_ind) + ".data")
        save_list(self.info, path + "/inf_info_ind" + str(info_ind) + ".data")
        save_list(self.info_type, path + "/inf_info_type_ind" + str(info_ind) + ".data")
        return 0

    def load_info(self, path, info_ind):
        self.analyzer_name = load_list(path + "/inf_analyzer_name_ind" + str(info_ind) + ".data")
        self.info = load_list(path + "/inf_info_ind" + str(info_ind) + ".data")
        self.info_type = load_list(path + "/inf_info_type_ind" + str(info_ind) + ".data")
        return 0

    def print_info(self):
        if self.info_type == "FileInfo":

            for file_info in self.info:
                print(file_info)
                for error_info in file_info.errors:
                    print(error_info)
            return 0

        if self.info_type == "COMBINED":
            for el in self.info:
                print("{}\n{}".format(el[0], el[1]))
            return 0

        print("NO SUCH info_type")
        return -1

    def __str__(self):
        return self.analyzer_name + ": " + self.info_type

    # I/O Operations END

    # Analyzer's xml document mining operations BEGIN

    def mine_info(self, analyzer_name, xml_path, code_project_source_path, dir_list, defect_type_list, info_type="FileInfo"):

        # File check re expr
        re_expr = ""

        if dir_list:
            len_def = len(dir_list)
            for ind in range(len_def):
                re_expr += dir_list[ind] + "*"
                if ind != (len_def - 1):
                    re_expr += "|.*"
        else:
            re_expr = ".*"

        # Initial parsing
        manifest_tree = et.parse(xml_path, parser=et.XMLParser(remove_blank_text=True))
        manifest_root = ht.tostring(manifest_tree)
        manifest_soup = bs4.BeautifulSoup(manifest_root, features="lxml")

        # Choose the analyzer
        if analyzer_name == "juliet":
            self.analyzer_name = analyzer_name
            analyzer_output = self.__juliet_mine(re_expr, manifest_soup, code_project_source_path)
        elif analyzer_name == "svace":
            self.analyzer_name = analyzer_name
            analyzer_output = self.__svace_mine(re_expr, manifest_soup, defect_type_list)
        else:
            print("NO SUCH ANALYZER")
            return -1

        # PostProcess analyzer's output
        analyzer_output.sort(key=itemgetter(0))

        if info_type == "ErrorInfo":
            self.__error_info_postproc(analyzer_output)
            return 0
        elif info_type == "FileInfo":
            self.__file_info_postproc(analyzer_output)
            return 0
        else:
            print("NO SUCH INFO MODE")
            return -1

    def __svace_mine(self, re_expr, manifest_soup, defect_type_list):

        # 0 - file
        # 1 - traces + main line array
        # 2 - defect class
        # 3 - message
        # 4 - traces info array
        # 5 - main line

        result_list = []

        list_warn_sv = []
        loc_warn_sv = []

        found = manifest_soup.find_all("warninfo", attrs={"file": re.compile(re_expr)})
        foundloc = manifest_soup.find_all("warninfoex")

        for warnloc in foundloc:

            loc_warn = []
            loc_lines = []
            loc_info = []
            name = ""

            buffer_found = warnloc.find_all("roletraceinfo")

            for trace in buffer_found:
                if trace["role"] != "counter-example":
                    for locinf in trace.find_all("locinfo", attrs={"file": re.compile(re_expr)}):
                        if name == "":
                            name = locinf["file"]
                            loc_warn.append(name)
                        loc_lines.append(int(locinf["line"]))
                        loc_info.append(locinf["info"])

            if len(loc_warn) > 0:
                loc_warn.append(loc_lines)
                loc_warn.append(loc_info)
                loc_warn_sv.append(loc_warn)

        for warn in found:
            warning = [warn["file"], None, warn['warnclass'], warn["msg"], None, int(warn["line"])]
            list_warn_sv.append(warning)

        loc_warn_sv.sort(key=itemgetter(0))
        list_warn_sv.sort(key=itemgetter(0))
        for ind in range(len(list_warn_sv)):
            list_warn_sv[ind][1] = loc_warn_sv[ind][1]
            list_warn_sv[ind][4] = loc_warn_sv[ind][2]
            if (not defect_type_list) or (list_warn_sv[ind][2] in defect_type_list):
                result_list.append(list_warn_sv[ind])

        return result_list

    def __juliet_mine(self, re_expr, manifest_soup, code_project_source_path):

        # 0 - file
        # 1 - traces + main line array
        # 2 - defect class
        # 3 - message
        # 4 - traces info array
        # 5 - main line

        result_list = []
        testcases = manifest_soup.find_all("testcase")

        for case in testcases:

            found = case.find_all(attrs={"path": re.compile(re_expr)})
            for file in found:

                found_file = find_in_juliet(file["path"], code_project_source_path)
                if found_file == -1:
                    continue

                flaws = file.find_all("flaw")
                if not len(flaws):
                    continue

                for flaw in flaws:
                    testcase_to_append = [found_file, [], juliet_shorten(file["path"]), "", [], None]
                    testcase_to_append[1].append(int(flaw["line"]))
                    testcase_to_append[3] = "juliet error: 'data'"
                    testcase_to_append[5] = int(flaw["line"])
                    if len(flaw["name"]):
                        testcase_to_append[4].append(flaw["name"])

                    result_list.append(testcase_to_append)

        return result_list

    def __file_info_postproc(self, analyzer_output):
        self.info_type = "FileInfo"

        for el in analyzer_output:

            if len(self.info) == 0 or el[0] != self.info[-1].file:
                self.append(FileInfo(file=el[0], errors=[ErrorInfo(lines=el[1], type=el[2],
                                                                   msg=el[3], traces_info=el[4],
                                                                   main_line=el[5])
                                                                   ]))
            else:
                self.info[-1].append(ErrorInfo(lines=el[1], type=el[2],
                                               msg=el[3], traces_info=el[4],
                                               main_line=el[5]))

        return 0

    def __error_info_postproc(self, analyzer_output):
        self.info_type = "ErrorInfo"

        for el in analyzer_output:
            self.append(ErrorInfo(file=el[0], lines=el[1], type=el[2], msg=el[3], traces_info=el[4], main_line=el[5]))

        return 0

    # Analyzer's xml document mining operations BEGIN
