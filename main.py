from allLibs import *
from projectLib.Comparison import Comparison
from projectLib.Info import Info
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

#svace_info = Info()
#svace_info.load_info(svace_data_path)
#juliet_info = Info()
#juliet_info.load_info(juliet_data_path)

comparison1 = Comparison()
comparison2 = Comparison()
comparison1.load_comparison(save_comp_results_dir, 0)
comparison2.load_comparison(save_comp_results_dir, 1)

comp_union = comparison1.comparison_union(comparison2)
#comparison.compare_analyzers_info(copy.deepcopy(svace_info), copy.deepcopy(juliet_info), "lines",
#                                  eur_params=lines_params)
#comparison.save_comparison(save_comp_results_dir, 0)
#comparison.load_comparison(save_comp_results_dir, 0)

#comparison1.print_comparison()
#comparison2.print_comparison()
comp_union.print_comparison()
