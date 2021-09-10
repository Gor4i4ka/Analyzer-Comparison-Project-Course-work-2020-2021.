from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.Comparison import Comparison
from projectLib.Heuristic import Heuristic
from projectTests.ProjectConfig_test import *

# REQUIRES: mine tests should be passed!

juliet_res_dir = project_source_dir + "/AnalyzerOutputs/juliet_output_lines.svres"
svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_lines.svres"

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

lines_heuristic = Heuristic(heuristic_name="lines", heuristic_params=dict({"distance": 0}))
lines_comparison = lines_heuristic.compare_info_with_heuristic(svace_info, juliet_info)

print("ANALYZER 1")
lines_comparison.print_comparison("an1")
print("ANALYZER 2")
lines_comparison.print_comparison("an2")
print("ANALYZER BOTH")
lines_comparison.print_comparison("an_both")
print("Test Finish")

