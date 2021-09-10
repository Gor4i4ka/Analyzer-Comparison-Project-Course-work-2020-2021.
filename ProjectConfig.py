import getpass
import clang.cindex
import pathlib

project_source_dir = str(pathlib.Path(__file__).parent.absolute())
project_binary_dir = project_source_dir + "/build"
user = getpass.getuser()

# AnalyzerInfo related

# IMPORTANT: MODIFY FOR YOUR MACHINE
code_project_source_path = "/home/" + user + "/C"

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
code_project_name = "C"

# IMPORTANT: MODIFY FOR YOUR MACHINE
xml_source_path = {
    "juliet": "/home/" + user +"/C/manifest.xml",
    "svace": "/home/" + user + "/svc/C.svres"

}

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
cwe_num_list = [
                "CWE401_Memory_Leak",
                "CWE415_Double_Free",
                "CWE416_Use_After_Free",
                "CWE773_Missing_Reference_to_Active_File_Descriptor_or_Handle",
                "CWE775_Missing_Release_of_File_Descriptor_or_Handle",
                "CWE476_NULL_Pointer_Dereference",
                "CWE675_Duplicate_Operations_on_Resource",
                "CWE690_NULL_Deref_From_Return",
                "CWE761_Free_Pointer_Not_at_Start_of_Buffer"
                ]

#cwe_num_list = [
#"CWE415_Double_Free",
#    "CWE416_Use_After_Free"

    #             ]

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
info_path = {
    "juliet": project_binary_dir + "/juliet_info",
    "svace": project_binary_dir + "/svace_info"

}

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
# warnings_list = {
#     "juliet": None,
#     "svace": None
#
# }

warnings_list = {
    "juliet": None,
    "svace": None

}

# Comparison related

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
comp_results_path = {
    "standard": project_binary_dir + "/comparison_results"

}

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
svres_gen_path = {
    "standard": project_binary_dir + "/svres_generates"
}

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
type_groups = {
    "svace":    {"Buffer_overflow": ["BUFFER_SHIFT", "BUFFER_OVERFLOW.EX",
                                         "DYNAMIC_OVERFLOW.EX", "BUFFER_OVERFLOW.STRING",
                                         "OVERFLOW_AFTER_CHECK.EX", "OVERFLOW_UNDER_CHECK",
                                         "STRING_OVERFLOW", "DYNAMIC_OVERFLOW",
                                        "TAINTED_ARRAY_INDEX.EX", "TAINTED_ARRAY_INDEX.MIGHT",
                                        "BUFFER_SIZE_MISMATCH", "STRING_OVERFLOW",
                                        "TAINTED_ARRAY_INDEX", "BUFFER_UNDERFLOW",
                                        "STATIC_OVERFLOW", "STATIC_OVERFLOW.LOCAL"
                                         ],
                 "TOTAL_COMPRESSION": 15},
    "juliet":   {"Buffer_overflow": ["CWE121", "CWE122", "CWE123", "CWE124", "CWE126", "CWE127"],
                "Integer_overflow": ["CWE190", "CWE191"],
                "Memory_leak": ["CWE401", "CWE415", "CWE416"],
                 "TOTAL_COMPRESSION": 8}
}

# Heuristic related

# DO NOT TOUCH (DEVELOPMENT IN PROCESS)
heuristic_union_list = [
    ["lines", {"distance": 0}],
    ["lines", {"distance": 1}],
    ["same_syntax_construct", {"statement_list": [clang.cindex.CursorKind.IF_STMT],
                                  "analyzer1_warn_types_list": ["SIMILAR_BRANCHES"],
                                  "analyzer2_warn_types_list": ["CWE121"],
                                  "c++_version": "-std=c++17"}]
]





