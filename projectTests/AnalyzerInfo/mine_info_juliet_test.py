import projectLib

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectTests.ProjectConfig_test import *

# Should see if all files are checked. The type and info consistency checked automatically

juliet_res_dir = project_source_dir + "/AnalyzerOutputs/juliet_output_mine.svres"
svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_mine.svres"

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

if isinstance(juliet_info.info[0], projectLib.FileInfo.FileInfo):
    print("FileInfo type check: Pass")
else:
    print("FileInfo type check: Fail")

file_info_array = [
    str([[[3], 'jultst', "juliet error: 'data'", ['CWE-396: Division by zero'], 3]])
]

for file_info_ind, file_info in enumerate(juliet_info):
    print("Checking {}".format(file_info))
    if str(file_info.errors) != file_info_array[file_info_ind]:
        print("Correct mining: Fail")
        break
    if file_info_ind == len(juliet_info) - 1:
        print("Correct mining: Pass")
print("Test finish.")