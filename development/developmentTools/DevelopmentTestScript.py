import copy
# Internal imports

from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.Comparison import Comparison
from ProjectConfig import *
from projectLib.Heuristic import Heuristic

from development.developmentTools.JulietSpecific.JulietSpecificAnalyzerInfo import juliet_divide_files, juliet_divide_funcs_svace
# INFO GENERATION PART START
print("INFO GENERATION PART START")

juliet_res_dir = xml_source_path["juliet"]
svace_res_dir = xml_source_path["svace"]
cwe_num_list = cwe_num_list

juliet_info = AnalyzerInfo()
juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, warnings_list["juliet"])

svace_info = AnalyzerInfo()
svace_info.mine_info("svace", svace_res_dir, cwe_num_list, warnings_list["svace"])

# EXPERIMENTAL
svace_info, juliet_info = juliet_divide_files(svace_info, juliet_info)
svace_info = juliet_divide_funcs_svace(svace_info)

svace_info.save_info(info_path["svace"], info_ind=0)
juliet_info.save_info(info_path["juliet"], info_ind=0)

print("INFO GENERATION PART END")
# INFO GENERATION PART END
# COMPARISON GENERATION PART START
print("COMPARISON GENERATION PART START")

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"], info_ind=0)
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"], info_ind=0)

comparison2 = Heuristic("lines", {"distance": 1}).\
    compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))
#
#comparison1 = Heuristic("lines", {"distance": 0}).\
#     compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))


########################
comparison1 = Heuristic("reaching_defs", {}).\
    compare_info_with_heuristic(copy.deepcopy(svace_info), copy.deepcopy(juliet_info))


########################

comparison1.save_comparison(comp_results_path["standard"], 0)
comparison2.save_comparison(comp_results_path["standard"], 1)

print("COMPARISON GENERATION PART END")
# COMPARISON GENERATION PART END
# COMPARISON LOADING PART START
print("COMPARISON LOADING PART START")

comparison1 = Comparison()
comparison2 = Comparison()

comparison1.load_comparison(comp_results_path["standard"], 0)
comparison2.load_comparison(comp_results_path["standard"], 1)

print("COMPARISON LOADING PART END")
# COMPARISON LOADING PART END
# COMPARISON UNION INTERSECTION SUBSTRACTION PART BEGIN
print("COMPARISON UNION INTERSECTION SUBSTRACTION PART BEGIN")

print("COMPARISON 1")
comparison1.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
print("COMPARISON 2")
comparison2.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
print("UNION")
comparison_u = comparison1.comparison_union(comparison2)
comparison_u.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison_u.save_comparison(comp_results_path["standard"], 2)

print("INTERSECTION")
comparison_i = comparison1.comparison_intersection(comparison2)
comparison_i.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison_i.save_comparison(comp_results_path["standard"], 3)

print("SUBSTRACTION")
comparison_s = comparison2.comparison_substraction(comparison1)
comparison_s.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison_s.save_comparison(comp_results_path["standard"], 4)

print("COMPARISON UNION INTERSECTION SUBSTRACTION PART END")
# COMPARISON UNION INTERSECTION SUBSTRACTION PART END

# BUFFER OVERFLOW SUPERHEURISTIC PART BEGIN
print("BUFFER OVERFLOW SUPERHEURISTIC PART BEGIN")

# comparison_bo = copy.deepcopy(comparison1)
# comparison_bo.analyze_comparison_buffer_overflow()
# comparison_bo.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
# comparison_bo.save_comparison(comp_results_path["standard"], 5)

print("BUFFER OVERFLOW SUPERHEURISTIC PART END")
# BUFFER OVERFLOW SUPERHEURISTIC PART END

# SVRES GENERATION PART BEGIN (with superheuristic)
print("SVRES GENERATION PART BEGIN")

# comparison_bo.generate_svres_for_both(svres_gen_path["standard"], project_name_par=code_project_name,
#                                       project_src_dir_par=code_project_source_path, ind=0)

comparison2.generate_svres_for_both(svres_gen_path["standard"], project_name_par=code_project_name,
                                       project_src_dir_par=code_project_source_path, ind=0)

print("SVRES GENERATION PART END")
#SVRES GENERATION PART END
