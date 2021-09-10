import getpass
import pathlib

project_source_dir = str(pathlib.Path(__file__).parent.absolute())
project_binary_dir = project_source_dir + "/build"
user = getpass.getuser()

info_path = {
    "svace": project_binary_dir + "/svace_info",
    "juliet": project_binary_dir + "/juliet_info"
}

code_project_source_path = project_source_dir + "/CSourceCode"
cwe_num_list = None
warnings_list = {
    "juliet": None,
    "svace": None
}
