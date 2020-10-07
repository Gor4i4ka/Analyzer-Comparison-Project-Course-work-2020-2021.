from allLibs import *
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *

juliet_res_dir = xml_source_path["juliet"]
svace_res_dir = xml_source_path["svace"]
cwe_num_list = cwe_num_list

svace_info = Info()
svace_info.mine_info("svace", svace_res_dir, cwe_num_list, warnings_list["svace"])

juliet_info = Info()
juliet_info.mine_info("juliet", juliet_res_dir, cwe_num_list, warnings_list["juliet"])

svace_info.save_info(data_path["svace"])
juliet_info.save_info(data_path["juliet"])

svace_info = Info()
svace_info.load_info(data_path["svace"])
juliet_info = Info()
juliet_info.load_info(data_path["juliet"])

svinf = svace_info.info
julinf = juliet_info.info

comparison = Comparison()
comparison.compare_analyzers_info(copy.deepcopy(svace_info), copy.deepcopy(juliet_info), "lines",
                                  eur_params=euristics_params["Lines"])
comparison.save_comparison(comp_results_path["svace"], 0)


comparison.print_comparison()
