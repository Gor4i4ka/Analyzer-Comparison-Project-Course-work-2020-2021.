import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

comparison = Comparison()
comparison.load_comparison(comp_results_path["svace"], 2)

comparison_grouped = comparison.group_comparison(type_groups["svace"], type_groups["juliet"])
comparison_grouped.print_comparison()
# for el in comparison_grouped.error_list_both:
#     print(el)

for el in comparison.get_list_by_type(type_groups["svace"]["Buffer_overflow"], "er_both"):
    print(el)

