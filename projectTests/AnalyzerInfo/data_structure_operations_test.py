from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.FileInfo import FileInfo
from projectLib.ErrorInfo import ErrorInfo
from projectTests.ProjectConfig_test import *

# REQUIRES: svace_mine test should be passed!

svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_mine.svres"

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

file_info = svace_info[0]
file_info_to_append = FileInfo(file="proxy", errors=[ErrorInfo()])

svace_info.append(file_info_to_append)

if file_info_to_append in svace_info:
    print("Check append: Pass")
else:
    print("Check append: Fail")

file_search = svace_info.search_by_file(filename="proxy")

if file_search == file_info_to_append:
    print("Check search_by_file: Pass")
else:
    print("Check search_by_file: Fail")

svace_info.remove(file_info_to_append)

if file_info_to_append not in svace_info:
    print("Check remove: Pass")
else:
    print("Check remove: Fail")

print("Test finish")