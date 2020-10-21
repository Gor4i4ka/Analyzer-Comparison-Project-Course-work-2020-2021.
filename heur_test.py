import copy

# Internal imports
from projectLib.Comparison import Comparison
from projectLib.Info import Info
from projectLib.ProjectConfig import *
from projectLib.Heuristic import Heuristic

svace_info = Info()
svace_info.load_info(info_path["svace"])
juliet_info = Info()
juliet_info.load_info(info_path["juliet"])

path_test = "/home/nick/dummy/same_syntax_test_file.c"

svace_piece = [path_test, [[3]], ["SIMILAR_BRANCHES"]]
jul_piece = [path_test, [[5, 7]], ["CWE121"]]

svace_info.info.append(svace_piece)
juliet_info.info.append(jul_piece)

comparison1 = Heuristic(heuristic_union_list[0][0], heuristic_union_list[0][1]).compare_info_with_heuristic(svace_info, juliet_info)
comparison2 = Heuristic(heuristic_union_list[2][0], heuristic_union_list[2][1]).compare_info_with_heuristic(svace_info, juliet_info)

comparison = comparison1.comparison_union(comparison2)
comparison.print_comparison()

