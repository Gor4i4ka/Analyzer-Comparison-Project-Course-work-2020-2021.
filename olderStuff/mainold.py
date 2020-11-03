from allLibs import *
from projectLib.Comparison import Comparison
from projectLib.AnalyzerInfo import AnalyzerInfo
from projectLib.ProjectConfig import *

# juliet_res_dir = juliet_res_dir
# svace_res_dir = svace_res_dir
# cwe_num_list = cwe_num_list
#
# svace_info = Info()
# svace_info.mine_info("svace", svace_res_dir, cwe_num_list, svace_warning_list)
#
# juliet_info = Info()
# juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, cwe_num_list)
#
# svace_info.save_info(svace_data_path)
# juliet_info.save_info(juliet_data_path)

# svace_info = Info()
# svace_info.load_info(svace_data_path)
# juliet_info = Info()
# juliet_info.load_info(juliet_data_path)
#
# svinf = svace_info.info
# julinf = juliet_info.info


comparison1 = Comparison()
comparison2 = Comparison()
comparison1.load_comparison(save_comp_results_dir, 0)
comparison2.load_comparison(save_comp_results_dir, 1)

#
#comp_union = comparison1.comparison_union(comparison2)
comp_intersection = comparison1.comparison_intersection(comparison2)
comparison1.print_comparison()
comp_intersection.print_comparison()

#print(len(comparison1.error_list_an2))
# print(len(comparison2.error_list_an1))
# print(len(comparison2.error_list_an2))
# comparison2.print_comparison()
# comparison = Comparison()
# comparison.compare_analyzers_info(copy.deepcopy(svace_info), copy.deepcopy(juliet_info), "lines",
#                                   eur_params=lines_params)
# comparison.save_comparison(save_comp_results_dir, 1)

# print(len(comparison.error_list_an1))
# print(comparison.stat_matrix[:, 3].sum())
# comparison.print_comparison()
#comparison.load_comparison(save_comp_results_dir, 0)

