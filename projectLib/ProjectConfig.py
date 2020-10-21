import clang
import clang.cindex

# juliet_related
juliet_work_path = "/home/nick/C"

# Info related

xml_source_path = {
    "juliet": "/home/nick/C/manifest.xml",
    "svace": "/home/nick/svc/C.svres"

}

cwe_num_list = ["CWE121_Stack_Based_Buffer_Overflow",
                "CWE122_Heap_Based_Buffer_Overflow",
                "CWE134_Uncontrolled_Format_String",
                "CWE190_Integer_Overflow",
                "CWE191_Integer_Underflow",
                "CWE252_Unchecked_Return_Value",
                "CWE369_Divide_by_Zero",
                "CWE401_Memory_Leak",
                "CWE415_Double_Free",
                "CWE416_Use_After_Free"
                ]

info_path = {
    "juliet": "/home/nick/svc/juliet_info",
    "svace": "/home/nick/svc/svace_info"

}

warnings_list = {
    "juliet": None,
    "svace": None

}

# Comparison related

comp_results_path = {
    "juliet": "/home/nick/svc/juliet_results",
    "svace": "/home/nick/svc/svace_results"

}

type_groups = {
    "svace":    {"Buffer_overflow": ["BUFFER_SHIFT", "BUFFER_OVERFLOW.EX",
                                         "DYNAMIC_OVERFLOW.EX", "BUFFER_OVERFLOW.STRING",
                                         "OVERFLOW_AFTER_CHECK.EX", "OVERFLOW_UNDER_CHECK",
                                         "STRING_OVERFLOW", "DYNAMIC_OVERFLOW",
                                         ],
                 "TOTAL_COMPRESSION": 7},
    "juliet":   {"Buffer_overflow": ["CWE121", "CWE122"],
                "Integer_overflow": ["CWE190", "CWE191"],
                "Memory_leak": ["CWE401", "CWE415", "CWE416"],
                 "TOTAL_COMPRESSION": 4}
}

# Heuristic related

heuristic_union_list = [
    ["lines", {"distance": 0}],
    ["lines", {"distance": 1}],
    ["same_syntax_construct", {"statement_list": [clang.cindex.CursorKind.IF_STMT],
                                  "analyzer1_warn_types_list": ["SIMILAR_BRANCHES"],
                                  "analyzer2_warn_types_list": None,
                                  "c++_version": "-std=c++17"}]
]





