from allLibs import *

juliet_res_dir = juliet_res_dir
svace_res_dir = svace_res_dir
cwe_num_list = cwe_num_list

#svace_info = mine_info("svace", svace_res_dir, cwe_num_list, svace_warning_list)
#juliet_info = mine_info("juliet", juliet_res_dir, cwe_num_list, cwe_num_list)

#save_info(svace_info, svace_data_path)
#save_info(juliet_info, juliet_data_path)

svace_info = load_info(svace_data_path)
juliet_info = load_info(juliet_data_path)
8397
6491

comparison = compare_analyzers_info(copy.deepcopy(svace_info), copy.deepcopy(juliet_info), "lines",
                                  eur_params=lines_params)
#save_comparison(save_comp_results_dir, 1, comparison)
#comparison = load_comparison(save_comp_results_dir, 0)
#print(len(comparison[4]))
#comparison = comparison_intersection(load_comparison(save_comp_results_dir, 0), load_comparison(save_comp_results_dir, 1))
print_comparison(comparison, "stat")
#print(comparison[2])
#print(len(comparison[4]))
# print(comparison[7])