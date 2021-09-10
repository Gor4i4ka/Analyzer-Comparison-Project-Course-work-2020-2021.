# Internal imports
from projectLib.AnalyzerInfo import AnalyzerInfo
from ProjectConfig import *
from projectLib.Heuristic import Heuristic
from projectLib.FileInfo import FileInfo
from projectLib.ErrorInfo import ErrorInfo

svace_info = AnalyzerInfo()
svace_info.load_info(info_path["svace"], 0)
juliet_info = AnalyzerInfo()
juliet_info.load_info(info_path["juliet"], 0)

path_test = "./CSourceCode/jultst_same_syntax_test_file.c"

svace_piece = FileInfo(file=path_test, errors=[ErrorInfo(lines=[3], type="SIMILAR_BRANCHES")])
jul_piece = FileInfo(file=path_test, errors=[ErrorInfo(lines=[5, 7], type="CWE121")])

svace_info.info.append(svace_piece)
juliet_info.info.append(jul_piece)

comparison = Heuristic(heuristic_union_list[2][0], heuristic_union_list[2][1]).compare_info_with_heuristic(svace_info, juliet_info)
comparison.group_comparison(type_groups["svace"], type_groups["juliet"]).print_comparison()

comparison.save_comparison(comp_results_path["standard"], 5)







