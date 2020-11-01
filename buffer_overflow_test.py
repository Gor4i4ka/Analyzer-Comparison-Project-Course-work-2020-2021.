import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

comparison = Comparison()
comparison.load_comparison(comp_results_path["svace"], 0)

comparison.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison.analyze_comparison_buffer_overflow()
#comparison.print_comparison()
comparison.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()
comparison.save_comparison(res_dir=comp_results_path["svace"], comparison_id=2)
