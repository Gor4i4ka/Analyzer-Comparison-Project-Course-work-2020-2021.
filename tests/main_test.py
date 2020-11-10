# Internal imports
from projectLib.Classes.Comparison import Comparison
from projectLib.ProjectConfig import *

# INFO GENERATION PART START

# juliet_res_dir = xml_source_path["juliet"]
# svace_res_dir = xml_source_path["svace"]
# cwe_num_list = cwe_num_list
#
# juliet_info = AnalyzerInfo()
# juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, warnings_list["juliet"])
#
# svace_info = AnalyzerInfo()
# svace_info.mine_info("svace", svace_res_dir, cwe_num_list, warnings_list["svace"])
#
# svace_info.save_info(info_path["svace"], info_ind=0)
# juliet_info.save_info(info_path["juliet"], info_ind=0)

# INFO GENERATION PART END
# COMPARISON GENERATION PART START

# svace_info = AnalyzerInfo()
# svace_info.load_info(info_path["svace"], info_ind=0)
# juliet_info = AnalyzerInfo()
# juliet_info.load_info(info_path["juliet"], info_ind=0)
#
# comparison2 = Heuristic("lines", {"distance": 1}).\
#     compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))
#
# comparison1 = Heuristic("lines", {"distance": 0}).\
#     compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))
#
# comparison1.save_comparison(comp_results_path["svace"], 0)
# comparison2.save_comparison(comp_results_path["svace"], 1)

# COMPARISON GENERATION PART END
# COMPARISON LOADING PART START

comparison1 = Comparison()
comparison2 = Comparison()

comparison1.load_comparison(comp_results_path["svace"], 0)
comparison2.load_comparison(comp_results_path["svace"], 1)

# COMPARISON LOADING PART END
# COMPARISON UNION INTERSECTION SUBSTRACTION PART BEGIN

# print("COMPARISON 1")
# comparison1.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# print("COMPARISON 2")
# comparison2.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# print("UNION")
# comparison_u = comparison1.comparison_union(comparison2)
# comparison_u.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# comparison_u.save_comparison(comp_results_path["svace"], 2)
#
# comparison_i = comparison1.comparison_intersection(comparison2)
# comparison_i.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# comparison_i.save_comparison(comp_results_path["svace"], 3)
#
# comparison_s = comparison2.comparison_substraction(comparison1)
# comparison_s.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# comparison_s.save_comparison(comp_results_path["svace"], 4)


# COMPARISON UNION INTERSECTION SUBSTRACTION PART END
