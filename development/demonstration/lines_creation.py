import copy
# Internal imports

from projectLib.AnalyzerInfo import AnalyzerInfo
from ProjectConfig import *
from projectLib.Heuristic import Heuristic

# LINES GENERATION PART START
print("COMPARISON GENERATION PART START")

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"], info_ind=0)
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"], info_ind=0)

comparison = Heuristic("lines", {"distance": 0}).\
    compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))

comparison.save_comparison(comp_results_path["standard"], 1)

print("COMPARISON GENERATION PART END")
print("SVRES GENERATION PART BEGIN")

comparison.generate_svres_for_both(svres_gen_path["standard"], project_name_par=code_project_name,
                                   project_src_dir_par=code_project_source_path, ind=1)

print("SVRES GENERATION PART END")
