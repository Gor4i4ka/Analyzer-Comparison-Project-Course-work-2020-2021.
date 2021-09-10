import copy
# Internal imports

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.Comparison import Comparison
from ProjectConfig import *
from projectLib.Heuristic import Heuristic

# LINES GENERATION PART START
print("COMPARISON GENERATION PART START")

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"], info_ind=0)
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"], info_ind=0)

comparison_initital = Comparison()
comparison_initital.load_comparison(comp_results_path["standard"], 1)

comparison = Heuristic("vars", {"type_groups": type_groups}).\
    compare_info_with_heuristic(used_comparison=comparison_initital)

comparison_initital.save_comparison(comp_results_path["standard"], 2)

print("COMPARISON GENERATION PART END")
print("SVRES GENERATION PART BEGIN")

comparison_initital.generate_svres_for_both(svres_gen_path["standard"], project_name_par=code_project_name,
                                   project_src_dir_par=code_project_source_path, ind=2)

print("SVRES GENERATION PART END")

