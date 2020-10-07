xml_source_path = {
    "juliet": "/home/nick/C/manifest.xml",
    "svace": "/home/nick/C.svres"

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

data_path = {
    "juliet": "/home/nick/svace/save_info/juliet_info.data",
    "svace": "/home/nick/svace/save_info/svc_info.data"

}

comp_results_path = {
    "juliet": "/home/nick/svace/save_results",
    "svace": "/home/nick/svace/save_results"

}

warnings_list = {
    "juliet": None,
    "svace": None

}

type_groups = {
    "svace":    None,
    "juliet":   {"Buffer_overflow.jul": ["CWE121", "CWE122"],
                "Integer_overflow.jul": ["CWE190", "CWE191"],
                "Memory_leak.jul": ["CWE401", "CWE151", "CWE416"]}
}

euristics_params = {
    "Lines": {"distance": 0}

}
