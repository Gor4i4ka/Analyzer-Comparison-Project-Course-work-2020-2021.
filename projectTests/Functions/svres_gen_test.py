from projectLib.Comparison import Comparison
from ProjectConfig import *

comparison = Comparison()
comparison.load_comparison(comp_results_path["standard"], 0)

comparison.generate_svres_for_both(svres_gen_path["standard"],
                                   project_name_par="C",
                                   project_src_dir_par="/home/nick/C",
                                   ind=0)