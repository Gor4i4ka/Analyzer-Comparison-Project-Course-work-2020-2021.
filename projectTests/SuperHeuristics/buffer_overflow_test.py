# Internal imports
from projectLib.Comparison import Comparison
from ProjectConfig import *

comparison = Comparison()
comparison.load_comparison(comp_results_path["standard"], 0)

comparison.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison.analyze_comparison_buffer_overflow()
comparison.print_comparison()
comparison.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison.save_comparison(res_dir=comp_results_path["standard"], comparison_id=5)
