import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic
print(str(["a", 1, "b"]))
# INFO GENERATION PART START

juliet_res_dir = xml_source_path["juliet"]
cwe_num_list = cwe_num_list

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, warnings_list["juliet"])

