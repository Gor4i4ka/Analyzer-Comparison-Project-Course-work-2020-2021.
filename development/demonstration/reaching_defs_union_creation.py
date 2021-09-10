from copy import deepcopy as dc
# Internal imports

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.Comparison import Comparison
from ProjectConfig import *
from projectLib.Heuristic import Heuristic

# LINES GENERATION PART START
print("COMPARISON GENERATION PART START")

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"], info_ind=1)
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"], info_ind=1)

comparison_lines = Heuristic("lines", {"distance": 0}).\
    compare_info_with_heuristic(dc(svace_info), dc(juliet_info))


comparison_reaching_defs = Comparison()
comparison_reaching_defs.load_comparison(comp_results_path["standard"], 3)

comparison_union = comparison_reaching_defs.comparison_union(comparison_lines)

comparison_lines.print_comparison()
comparison_union.print_comparison()

comparison_union.save_comparison(comp_results_path["standard"], 4)

print("COMPARISON GENERATION PART END")
print("SVRES GENERATION PART BEGIN")

comparison_union.generate_svres_for_both(svres_gen_path["standard"], project_name_par=code_project_name,
                                         project_src_dir_par=code_project_source_path, ind=3)

print("SVRES GENERATION PART END")