from projectLib.AnalyzerInfo import AnalyzerInfo
from projectTests.ProjectConfig_test import *

# REQUIRES: mining tests should be passed!
# Automatically checks if information is not lost during save/load

juliet_res_dir = project_source_dir + "/AnalyzerOutputs/juliet_output_mine.svres"
svace_res_dir = project_source_dir + "/AnalyzerOutputs/svace_output_mine.svres"

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

svace_info.save_info(info_path["svace"], info_ind=0)
juliet_info.save_info(info_path["juliet"], info_ind=0)

svace_info_new = AnalyzerInfo()
svace_info_new.load_info(info_path["svace"], info_ind=0)

juliet_info_new = AnalyzerInfo()
juliet_info_new.load_info(info_path["juliet"], info_ind=0)

if svace_info_new == svace_info and juliet_info_new == juliet_info:
    print("Check save/load: Pass")
else:
    print("Check save/load: Fail")

print("Test finish.")