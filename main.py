import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

# INFO GENERATION PART START

juliet_res_dir = xml_source_path["juliet"]
svace_res_dir = xml_source_path["svace"]
cwe_num_list = cwe_num_list

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, warnings_list["juliet"])

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, cwe_num_list, warnings_list["svace"])

svace_info.save_info(info_path["svace"])
juliet_info.save_info(info_path["juliet"])

# INFO GENERATION PART END
# COMPARISON GENERATION PART START

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"])
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"])

comparison_list = []
for heuristic_params in heuristic_union_list:
    comparison_list.append(Heuristic(heuristic_params[0], heuristic_params[1]).
                           compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info)))

comparison = Comparison()
comparison.comparison_copy(comparison_list[0])

comparison.save_comparison(comp_results_path["svace"], 0)

for comparison_el in comparison_list[1:]:
    comparison = comparison.comparison_union(comparison_el)


comparison.save_comparison(comp_results_path["svace"], 1)

# COMPARISON GENERATION PART END
# COMPARISON LOADING PART START

comparison1 = Comparison()
comparison2 = Comparison()

comparison1.load_comparison(comp_results_path["svace"], 0)
comparison2.load_comparison(comp_results_path["svace"], 1)

print("COMPARISON 1")
comparison1.print_comparison()
comparison1.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
print("COMPARISON 2")
comparison2.print_comparison()
comparison2.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()

# COMPARISON LOADING PART END