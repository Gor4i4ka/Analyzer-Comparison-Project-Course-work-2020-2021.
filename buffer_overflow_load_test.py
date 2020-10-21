import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

comparison = Comparison()
comparison.load_comparison(comp_results_path["svace"], 2)

comparison.print_comparison(mode="er2")