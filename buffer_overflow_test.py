import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

comparison = Comparison()
comparison.load_comparison(comp_results_path["svace"], 0)

comparison.print_comparison(group_by_type_groups=True)
comparison.analyze_comparison_buffer_overflow()
#comparison.print_comparison()
comparison.print_comparison(group_by_type_groups=True)
comparison.save_comparison(res_dir=comp_results_path["svace"], comparison_id=2)
