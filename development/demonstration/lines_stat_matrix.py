# Internal imports

from projectLib.Comparison import Comparison
from ProjectConfig import *

juliet_res_dir = xml_source_path["juliet"]
svace_res_dir = xml_source_path["svace"]
cwe_num_list = cwe_num_list

comparison = Comparison()
comparison.load_comparison(comp_results_path["standard"], 1)
comparison.print_comparison()