# Internal imports

from projectLib.AnalyzerInfo import AnalyzerInfo
from ProjectConfig import *

# INFO GENERATION PART START
print("INFO GENERATION PART START")

juliet_res_dir = xml_source_path["juliet"]
svace_res_dir = xml_source_path["svace"]
cwe_num_list = cwe_num_list

print("INFO JULIET")

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, code_project_source_path, cwe_num_list, warnings_list["juliet"])

print("INFO SVACE")

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, code_project_source_path, cwe_num_list, warnings_list["svace"])

print("SAVING")

svace_info.save_info(info_path["svace"], info_ind=1)
juliet_info.save_info(info_path["juliet"], info_ind=1)