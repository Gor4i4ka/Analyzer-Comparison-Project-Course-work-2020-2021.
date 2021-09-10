
import projectLib

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectTests.ProjectConfig_test import *

# Should see if all files are checked. The type and info consistency checked automatically

juliet_res_dir = project_source_dir + "/AnalyzerOutputs/juliet_output_mine.svres"
svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_mine.svres"

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

if isinstance(svace_info.info[0], projectLib.FileInfo.FileInfo):
    print("FileInfo type check: Pass")
else:
    print("FileInfo type check: Fail")

file_info_array = [
    str([[[3], 'DIVISION_BY_ZERO', 'DIVISION_ZERO', ["DIVISION'"], 3]])
]

for file_info_ind, file_info in enumerate(svace_info):
    print("Checking {}".format(file_info))
    if str(file_info.errors) != file_info_array[file_info_ind]:
        print("Correct mining: Fail")
        break
    if file_info_ind == len(svace_info) - 1:
        print("Correct mining: Pass")
print("Test finish.")