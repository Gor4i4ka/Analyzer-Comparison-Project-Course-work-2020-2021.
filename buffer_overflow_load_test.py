import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

comparison = Comparison()
comparison.load_comparison(comp_results_path["svace"], 1)

comparison.print_comparison()
comparison_grouped = comparison.group_comparison(type_groups["svace"], type_groups["juliet"])
comparison_grouped.print_comparison()