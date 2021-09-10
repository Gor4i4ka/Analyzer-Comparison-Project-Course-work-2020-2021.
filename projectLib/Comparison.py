import numpy as np
import copy
import clang
import clang.cindex

from lxml import etree as et
from copy import deepcopy as dc

# Internal imports
from projectLib.Binding import Binding
from Common import srch_list_ind, save_list, load_list, print_numpy, list_intersect
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ErrorInfo import ErrorInfo


class Comparison:

    def __init__(self,
                 analyzer1_info: AnalyzerInfo=AnalyzerInfo(),
                 analyzer2_info: AnalyzerInfo=AnalyzerInfo()):

        self.name_catalog_an1 = []
        self.name_catalog_an2 = []
        self.stat_matrix = None

        self.analyzer1_info = copy.deepcopy(analyzer1_info)
        self.analyzer2_info = copy.deepcopy(analyzer2_info)

    # # Data structure operations BEGIN

    def check_both_FileInfo_format(self):
        if self.analyzer1_info.info_type != "FileInfo" or \
           self.analyzer2_info.info_type != "FileInfo":
            print("GROUP COMPARISON ONLY SUPPORTED FOR FileInfo info_type")
            return False
        return True

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
            file_to_attach = dc(file_an1)
            file_to_attach.errors = []

            for er_in_file_an1 in file_an1:
                ind = srch_list_ind(self.name_catalog_an1, er_in_file_an1.type)
                for name_merged_ind in range(len(name_catalog_an1_merged)):
                    if ind in name_catalog_an1_merged[name_merged_ind][1]:
                        error_to_attach = copy.deepcopy(er_in_file_an1)
                        error_to_attach.type = name_catalog_an1_merged[name_merged_ind][0]
                        file_to_attach.errors.append(error_to_attach)
                        break

        for file_an2 in self.analyzer2_info.info:
            file_to_attach = dc(file_an2)
            file_to_attach.errors = []

            for er_in_file_an2 in file_an2:
                ind = srch_list_ind(self.name_catalog_an2, er_in_file_an2.type)
                for name_merged_ind in range(len(name_catalog_an2_merged)):
                    if ind in name_catalog_an2_merged[name_merged_ind][1]:
                        error_to_attach = copy.deepcopy(er_in_file_an2)
                        error_to_attach.type = name_catalog_an2_merged[name_merged_ind][0]
                        file_to_attach.errors.append(error_to_attach)
                        break
        # FileInfo actions END
        return result_comparison

    def stat_matrix_fill_by_bindings(self):
        for file_info_an1 in self.analyzer1_info.info:
            for error_info_an1 in file_info_an1:

                name_catalog1_ind = srch_list_ind(self.name_catalog_an1, error_info_an1.type)
                self.stat_matrix[name_catalog1_ind, -1] += 1

                if not error_info_an1.has_bindings():
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

    # # Data structure operations END

    # I/O Operations BEGIN

    def save_comparison(self, res_dir, comparison_id):

        name_catalog_an1_path = res_dir + "/cmp_name_catalog_an1_ind" + str(comparison_id) + ".data"
        name_catalog_an2_path = res_dir + "/cmp_name_catalog_an2_ind" + str(comparison_id) + ".data"
        stat_matrix_path = res_dir + "/cmp_stat_matrix" + str(comparison_id) + ".npy"
        analyzer1_info_path = res_dir + "/analyzer1_info"
        analyzer2_info_path = res_dir + "/analyzer2_info"

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
        analyzer1_info_path = res_dir + "/analyzer1_info"
        analyzer2_info_path = res_dir + "/analyzer2_info"

        self.name_catalog_an1 = load_list(name_catalog_an1_path)
        self.name_catalog_an2 = load_list(name_catalog_an2_path)
        self.stat_matrix = np.load(stat_matrix_path)
        self.analyzer1_info.load_info(analyzer1_info_path, comparison_id)
        self.analyzer2_info.load_info(analyzer2_info_path, comparison_id)

        return 0

    def print_comparison(self, mode="stat"):

        def get_errors_only_in_analyzer_num(comparison, analyzer_num: int):
            if not comparison.check_both_FileInfo_format():
                return -1

            if analyzer_num == 1:
                analyzer_info = comparison.analyzer1_info
            else:
                if analyzer_num == 2:
                    analyzer_info = comparison.analyzer2_info
                else:
                    print("NO SUCH ANALYZER_NUM")
                    return -1

            result_analyzer_info = copy.deepcopy(analyzer_info)
            result_analyzer_info.info = []

            # FileInfo actions BEGIN
            for file_info in analyzer_info.info:
                file_to_add = copy.deepcopy(file_info)
                file_to_add.errors = []
                for error_info in file_info.errors:
                    if not error_info.has_bindings():
                        file_to_add.append(error_info)
                if file_to_add.has_errors():
                    result_analyzer_info.append(file_to_add)

            # FileInfo actions END
            return result_analyzer_info

        def get_errors_in_all_analyzers(comparison):
            if not comparison.check_both_FileInfo_format():
                return -1

            result_analyzer_info = AnalyzerInfo(info_type="COMBINED")

            # FileInfo actions BEGIN

            for file_info_an1 in comparison.analyzer1_info.info:
                for error_info_an1 in file_info_an1:
                    for binding in error_info_an1.bindings:
                        filename_to_search = file_info_an1.file
                        if binding.file:
                            filename_to_search = binding.file
                        file_info_an2 = comparison.analyzer2_info.search_by_file(filename_to_search)
                        error_info_an2 = file_info_an2[binding.ind]

                        error_info_to_add_an1 = copy.deepcopy(error_info_an1)
                        error_info_to_add_an1.file = file_info_an1.file
                        error_info_to_add_an2 = copy.deepcopy(error_info_an2)
                        error_info_to_add_an2.file = file_info_an2.file

                        result_analyzer_info.append([error_info_to_add_an1, error_info_to_add_an2])

            # FileInfo actions END
            return result_analyzer_info

        if not self.check_both_FileInfo_format():
            return -1

        if mode == "stat":
            print_numpy(self.stat_matrix, self.name_catalog_an1, self.name_catalog_an2)
            return 0
        # FileInfo actions BEGIN
        if mode == "an1":
            only_analyzer1_errors = get_errors_only_in_analyzer_num(self, 1)
            for file_info in only_analyzer1_errors.info:
                print(file_info)

                for error_info in file_info:
                    print(error_info)
            return 0

        if mode == "an2":
            only_analyzer2_errors = get_errors_only_in_analyzer_num(self, 2)
            for file_info in only_analyzer2_errors.info:
                print(file_info)

                for error_info in file_info:
                    print(error_info)
            return 0

        if mode == "an_both":
            both_analyzers_errors = get_errors_in_all_analyzers(self)
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

    # I/O Operations END

    # Set Operations BEGIN

    def __subproc_fill_for_set_operations(self):
        result_comparison = Comparison()
        result_comparison.name_catalog_an1 = copy.deepcopy(self.name_catalog_an1)
        result_comparison.name_catalog_an2 = copy.deepcopy(self.name_catalog_an2)

        result_comparison.stat_matrix = np.zeros(self.stat_matrix.shape, dtype='int')

        result_comparison.analyzer1_info = dc(self.analyzer1_info)
        result_comparison.analyzer1_info.info = []

        result_comparison.analyzer2_info = dc(self.analyzer2_info)
        result_comparison.analyzer2_info.info = []

        return result_comparison

    def comparison_union(self, another_comparison):

        def __subproc_comparison_union_form_info(comparison, another_comparison, result_comparison, analyzer_num):
            if analyzer_num == 1:
                self_analyzer_info = comparison.analyzer1_info
                another_comparison_analyzer_info = another_comparison.analyzer1_info
            else:
                self_analyzer_info = comparison.analyzer2_info
                another_comparison_analyzer_info = another_comparison.analyzer2_info

            for file_info_cmp1 in self_analyzer_info.info:
                file_info_to_add = dc(file_info_cmp1)
                file_info_to_add.errors = []

                file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
                for error_info_ind in range(len(file_info_cmp1.errors)):
                    bindings_to_add = copy.deepcopy(file_info_cmp1.errors[error_info_ind].bindings)
                    for binding_cmp2 in file_info_cmp2.errors[error_info_ind].bindings:
                        if binding_cmp2 not in bindings_to_add:
                            bindings_to_add.append(binding_cmp2)
                    error_to_add = dc(file_info_cmp1.errors[error_info_ind])
                    error_to_add.bindings = bindings_to_add
                    file_info_to_add.append(error_to_add)
                if analyzer_num == 1:
                    result_comparison.analyzer1_info.append(file_info_to_add)
                else:
                    result_comparison.analyzer2_info.append(file_info_to_add)
            return 0

        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN

        __subproc_comparison_union_form_info(self, another_comparison, result_comparison, analyzer_num=1)
        __subproc_comparison_union_form_info(self, another_comparison, result_comparison, analyzer_num=2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    def comparison_substraction(self, another_comparison):

        def __subproc_comparison_substraction_form_info(comparison, another_comparison, result_comparison, analyzer_num):
            if analyzer_num == 1:
                self_analyzer_info = comparison.analyzer1_info
                another_comparison_analyzer_info = another_comparison.analyzer1_info
            else:
                self_analyzer_info = comparison.analyzer2_info
                another_comparison_analyzer_info = another_comparison.analyzer2_info

            for file_info_cmp1 in self_analyzer_info.info:

                file_info_to_add = dc(file_info_cmp1)
                file_info_to_add.errors = []

                file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
                for error_info_ind in range(len(file_info_cmp1.errors)):
                    bindings_to_add = []
                    for binding_cmp1 in file_info_cmp1[error_info_ind].bindings:
                        if binding_cmp1 not in file_info_cmp2[error_info_ind].bindings:
                            bindings_to_add.append(binding_cmp1)
                    error_to_add = dc(file_info_cmp1[error_info_ind])
                    error_to_add.bindings = bindings_to_add
                    file_info_to_add.append(error_to_add)

                if analyzer_num == 1:
                    result_comparison.analyzer1_info.append(file_info_to_add)
                else:
                    result_comparison.analyzer2_info.append(file_info_to_add)

        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN
        __subproc_comparison_substraction_form_info(self, another_comparison, result_comparison, analyzer_num=1)
        __subproc_comparison_substraction_form_info(self, another_comparison, result_comparison, analyzer_num=2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    def comparison_intersection(self, another_comparison):

        def __subproc_comparison_intersection_form_info(comparison, another_comparison, result_comparison, analyzer_num):
            if analyzer_num == 1:
                self_analyzer_info = comparison.analyzer1_info
                another_comparison_analyzer_info = another_comparison.analyzer1_info
            else:
                self_analyzer_info = comparison.analyzer2_info
                another_comparison_analyzer_info = another_comparison.analyzer2_info

            for file_info_cmp1 in self_analyzer_info.info:

                file_info_to_add = dc(file_info_cmp1)
                file_info_to_add.errors = []

                file_info_cmp2 = another_comparison_analyzer_info.search_by_file(file_info_cmp1.file)
                for error_info_ind in range(len(file_info_cmp1.errors)):
                    bindings_to_add = []
                    for binding_cmp1 in file_info_cmp1[error_info_ind].bindings:
                        if binding_cmp1 in file_info_cmp2[error_info_ind].bindings:
                            bindings_to_add.append(binding_cmp1)

                    error_to_add = dc(file_info_cmp1.errors[error_info_ind])
                    error_to_add.bindings = bindings_to_add
                    file_info_to_add.append(error_to_add)
                if analyzer_num == 1:
                    result_comparison.analyzer1_info.append(file_info_to_add)
                else:
                    result_comparison.analyzer2_info.append(file_info_to_add)
            return 0

        if not self.check_both_FileInfo_format():
            return -1

        result_comparison = self.__subproc_fill_for_set_operations()

        # FileInfo actions BEGIN
        __subproc_comparison_intersection_form_info(self, another_comparison, result_comparison, analyzer_num=1)
        __subproc_comparison_intersection_form_info(self, another_comparison, result_comparison, analyzer_num=2)

        result_comparison.stat_matrix_fill_by_bindings()
        # FileInfo actions END

        return result_comparison

    # Set Operations END

    # SvRes generation BEGIN

    def generate_svres_for_both(self, svres_save_dir: str, project_name_par: str, project_src_dir_par: str, ind: int):

        def __subproc_generate_svres_skeleton(project_name_par, project_src_dir_par):

            # SvRes skeleton
            object_stream = et.Element(b"object-stream")

            sv_res_version = et.Element(b"SvResVersion")
            sv_res_version.text = b"2.4:Svace results format"
            object_stream.append(sv_res_version)

            # Primary results (defect lines)

            sv_res_results = et.Element(b"SvResResults")
            results = et.Element(b"results")
            sv_res_proj_results = et.Element(b"SvResProjResults")

            project_name = et.Element(b"projectName")
            project_name.text = bytes(project_name_par, encoding="utf8")
            sv_res_proj_results.append(project_name)

            project_src_dir = et.Element(b"projectSrcDir")
            project_src_dir.text = bytes(project_src_dir_par, encoding="utf8")
            sv_res_proj_results.append(project_src_dir)

            warnings = et.Element(b"warnings")

            # Cycle to append HERE

            sv_res_proj_results.append(warnings)

            results.append(sv_res_proj_results)

            sv_res_results.append(results)

            object_stream.append(sv_res_results)

            # Extended results (traces)

            sv_res_results_ex = et.Element(b"SvResResultsEx")
            results = et.Element(b"results")
            sv_res_proj_results_ex = et.Element(b"SvResProjResultsEx")

            project_name = et.Element(b"projectName")
            project_name.text = bytes(project_name_par, encoding="utf8")
            sv_res_proj_results_ex.append(project_name)

            warnings = et.Element(b"warnings")

            # Cycle to append HERE

            sv_res_proj_results_ex.append(warnings)

            results.append(sv_res_proj_results_ex)

            sv_res_results_ex.append(results)

            object_stream.append(sv_res_results_ex)

            return object_stream

        def __subproc_generate_warn_info_and_ex_sole(filepath: str, error_info: ErrorInfo, ind: int):

            # Generating WarnInfo
            warning = et.Element(b"WarnInfo", attrib={b"id": bytes(str(ind), encoding="utf8"),
                                                      b"warnClass": bytes(error_info.type, encoding="utf8"),
                                                      b"line": bytes(str(error_info.main_line), encoding="utf8"),
                                                      b"file": bytes(filepath, encoding="utf8"),
                                                      b"msg": bytes(error_info.msg, encoding="utf8"),
                                                      b"status": b"",
                                                      b"details": b"",
                                                      b"comment": b"",
                                                      b"function": b"",
                                                      b"mtid": b"",
                                                      b"tool": b"",
                                                      b"lang": b"",
                                                      b"flags": b"0"})
            # Generating WarnInfoEx
            warning_ex = et.Element(b"WarnInfoEx", attrib={b"id": bytes(str(ind), encoding="utf8"),
                                                           b"zRate": b"0.0",
                                                           })

            traces = et.Element(b"traces")
            warning_ex.append(traces)

            # Inside traces BEGIN

            role_trace_info = et.Element(b"RoleTraceInfo", attrib={b"role": b"defect"})
            traces.append(role_trace_info)

            locations = et.Element(b"locations")
            role_trace_info.append(locations)

            # Generating every trace

            for trace_ind in range(len(error_info.traces_info)):
                line = error_info.lines[trace_ind]
                info = error_info.traces_info[trace_ind]
                loc_info = et.Element(b"LocInfo", attrib={b"file": bytes(filepath, encoding="utf8"),
                                                          b"line": bytes(str(line), encoding="utf8"),
                                                          b"spec": b"",
                                                          b"info": bytes(info, encoding="utf8"),
                                                          b"col": b"0"})
                locations.append(loc_info)

            # Inside traces END

            user_attributes = et.Element(b"userAttributes", attrib={b"class": b"tree-map"})
            warning_ex.append(user_attributes)

            entry = et.Element(b"entry")
            string1 = et.Element(b"string")
            string1.text = b".comment"
            string2 = et.Element(b"string")
            string2.text = b""
            entry.append(string1)
            entry.append(string2)

            user_attributes.append(dc(entry))
            string1.text = b".status"
            string2.text = b"Default"
            user_attributes.append(dc(entry))

            return warning, warning_ex

        def __subproc_generate_warn_info_and_ex_merged(filepath: str, error_info_an1: ErrorInfo,
                                                       error_info_an2: ErrorInfo, ind: int):

            # The main defect will be determined by an1
            # Generating WarnInfo

            warning_an1 = et.Element(b"WarnInfo", attrib={
                b"id": bytes(str(ind), encoding="utf8"),
                b"warnClass": bytes(error_info_an1.type, encoding="utf8") + b"|" + bytes(error_info_an2.type,
                                                                                         encoding="utf8"),
                b"line": bytes(str(error_info_an1.main_line), encoding="utf8"),
                b"file": bytes(filepath, encoding="utf8"),
                b"msg": bytes(error_info_an1.msg, encoding="utf8") + b"|" + bytes(error_info_an2.msg, encoding="utf8"),
                b"status": b"",
                b"details": b"",
                b"comment": b"",
                b"function": b"",
                b"mtid": b"",
                b"tool": b"",
                b"lang": b"",
                b"flags": b"0"})

            # Generating WarnInfoEx
            warning_ex_an1 = et.Element(b"WarnInfoEx", attrib={b"id": bytes(str(ind), encoding="utf8"),
                                                               b"zRate": b"0.0",
                                                               })

            traces = et.Element(b"traces")
            warning_ex_an1.append(traces)

            # Inside traces BEGIN

            role_trace_info = et.Element(b"RoleTraceInfo", attrib={b"role": b"defect"})
            traces.append(role_trace_info)

            locations = et.Element(b"locations")
            role_trace_info.append(locations)

            # Generating every trace

            for trace_ind in range(len(error_info_an1.traces_info)):
                line = error_info_an1.lines[trace_ind]
                info = error_info_an1.traces_info[trace_ind]
                loc_info = et.Element(b"LocInfo", attrib={b"file": bytes(filepath, encoding="utf8"),
                                                          b"line": bytes(str(line), encoding="utf8"),
                                                          b"spec": b"",
                                                          b"info": b"AN1: " + bytes(info, encoding="utf8"),
                                                          b"col": b"0"})
                locations.append(loc_info)

            for trace_ind in range(len(error_info_an2.traces_info)):
                line = error_info_an2.lines[trace_ind]
                info = error_info_an2.traces_info[trace_ind]
                loc_info = et.Element(b"LocInfo", attrib={b"file": bytes(filepath, encoding="utf8"),
                                                          b"line": bytes(str(line), encoding="utf8"),
                                                          b"spec": b"",
                                                          b"info": b"AN2: " + bytes(info, encoding="utf8"),
                                                          b"col": b"0"})
                locations.append(loc_info)

            # Inside traces END

            user_attributes = et.Element(b"userAttributes", attrib={b"class": b"tree-map"})
            warning_ex_an1.append(user_attributes)

            entry = et.Element(b"entry")
            string1 = et.Element(b"string")
            string1.text = b".comment"
            string2 = et.Element(b"string")
            string2.text = b""
            entry.append(string1)
            entry.append(string2)

            user_attributes.append(dc(entry))
            string1.text = b".status"
            string2.text = b"Default"
            user_attributes.append(dc(entry))

            return warning_an1, warning_ex_an1

        if not self.check_both_FileInfo_format():
            return -1

        object_stream1 = __subproc_generate_svres_skeleton(project_name_par, project_src_dir_par)
        object_stream2 = dc(object_stream1)
        object_stream_both = dc(object_stream1)

        # Getting links to warnings in SvRes and SvResEx
        warnings_stream1 = object_stream1[1][0][0][2]
        warnings_ex_stream1 = object_stream1[2][0][0][1]

        warnings_stream2 = object_stream2[1][0][0][2]
        warnings_ex_stream2 = object_stream2[2][0][0][1]

        warnings_stream_both = object_stream_both[1][0][0][2]
        warnings_ex_stream_both = object_stream_both[2][0][0][1]

        # Hardcoded svres values
        id_counter_svres1 = 1000
        id_counter_svres2 = 1000
        id_counter_svres_both = 1000

        # FileInfo actions BEGIN
        for file_info_an1 in self.analyzer1_info:
            for error_info_an1 in file_info_an1:
                if not error_info_an1.has_bindings():
                    warning, warning_ex = __subproc_generate_warn_info_and_ex_sole(file_info_an1.file,
                                                                                        error_info_an1,
                                                                                        id_counter_svres1)
                    warnings_stream1.append(warning)
                    warnings_ex_stream1.append(warning_ex)
                    id_counter_svres1 += 1

                file_info_an2 = self.analyzer2_info.search_by_file(file_info_an1.file)

                for binding in error_info_an1.bindings:
                    error_info_an2 = file_info_an2[binding.ind]
                    warning_an1, warning_ex_an1 = __subproc_generate_warn_info_and_ex_merged(file_info_an1.file,
                                                                                                  error_info_an1,
                                                                                                  error_info_an2,
                                                                                                  id_counter_svres1)
                    warning_an2, warning_ex_an2 = __subproc_generate_warn_info_and_ex_merged(file_info_an1.file,
                                                                                                  error_info_an1,
                                                                                                  error_info_an2,
                                                                                                  id_counter_svres2)
                    warnings_stream1.append(warning_an1)
                    warnings_stream2.append(warning_an2)
                    warnings_stream_both.append(dc(warning_an1))
                    warnings_ex_stream1.append(warning_ex_an1)
                    warnings_ex_stream2.append(warning_ex_an2)
                    warnings_ex_stream_both.append(dc(warning_ex_an1))
                    id_counter_svres1 += 1
                    id_counter_svres2 += 1
                    id_counter_svres_both += 1

        for file_info_an2 in self.analyzer2_info:
            for error_info_an2 in file_info_an2:
                if not error_info_an2.has_bindings():
                    warning, warning_ex = __subproc_generate_warn_info_and_ex_sole(file_info_an2.file, error_info_an2,
                                                                                        id_counter_svres2)
                    warnings_stream2.append(warning)
                    warnings_ex_stream2.append(warning_ex)
                    id_counter_svres2 += 1

        # FileInfo actions END

        # Saving svres
        svres_string_an1 = et.tostring(object_stream1, pretty_print=True, encoding="unicode")
        file_to_write_in_an1 = open(svres_save_dir + "/" + project_name_par + "_AN1_" + str(ind) + ".svres", "w")
        file_to_write_in_an1.write(svres_string_an1)
        file_to_write_in_an1.close()

        svres_string_an2 = et.tostring(object_stream2, pretty_print=True, encoding="unicode")
        file_to_write_in_an2 = open(svres_save_dir + "/" + project_name_par + "_AN2_" + str(ind) + ".svres", "w")
        file_to_write_in_an2.write(svres_string_an2)
        file_to_write_in_an2.close()

        svres_string_both = et.tostring(object_stream_both, pretty_print=True, encoding="unicode")
        file_to_write_in_both = open(svres_save_dir + "/" + project_name_par + "_BOTH_" + str(ind) + ".svres", "w")
        file_to_write_in_both.write(svres_string_both)
        file_to_write_in_both.close()

        return 0

    # SvRes generation END



