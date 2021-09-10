import sys
import io

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectTests.ProjectConfig_test import *

# REQUIRES: mine tests should be passed!

juliet_res_dir = project_source_dir + "/AnalyzerOutputs/juliet_output_mine.svres"
svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_mine.svres"

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

old_stdout = sys.stdout
new_stdout = io.StringIO()
sys.stdout = new_stdout

juliet_info.print_info()
jul_output = new_stdout.getvalue()

new_stdout = io.StringIO()
sys.stdout = new_stdout

svace_info.print_info()
sv_output = new_stdout.getvalue()

correct_output_jul = "/home/nick/PycharmProjects/analyzer_comparison_v1/sa_comparison/projectTests/CSourceCode/testcases/jultst_files/jultst_div_zero.c" + "\n" + \
str([[3], 'jultst', "juliet error: 'data'", ['CWE-396: Division by zero'], 3]) + "\n"

correct_output_sv = "/home/nick/PycharmProjects/analyzer_comparison_v1/sa_comparison/projectTests/CSourceCode/testcases/jultst_files/jultst_div_zero.c" + "\n" + \
str([[3], 'DIVISION_BY_ZERO', 'DIVISION_ZERO', ["DIVISION'"], 3]) + "\n"

sys.stdout = old_stdout

if correct_output_jul == jul_output:
    print("Check print output: Pass")
else:
    print("Check print output: Fail")

print("Test finish")