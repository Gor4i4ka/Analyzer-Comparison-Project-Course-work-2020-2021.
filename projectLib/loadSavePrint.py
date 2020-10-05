import numpy as np

from allLibs import *

#########FOR INFO#########


def save_info(info, path):
    with open(path, "wb") as filehandle:
        # store the data as binary data stream
        pickle.dump(info, filehandle)
    return None


def load_info(path):
    with open(path, 'rb') as filehandle:
        # read the data as binary data stream
        return pickle.load(filehandle)


def print_info(lst):
    for el in lst:
        print("{}".format(el))
    return None


#########FOR COMPARISON#########


def save_comparison(res_dir, generation_ind, results):

    name_catalog1_path = res_dir + "/name_catalog1_ind" + str(generation_ind) + ".data"
    name_catalog2_path = res_dir + "/name_catalog2_ind" + str(generation_ind) + ".data"
    stat_matrix_path = res_dir + "/stat_matrix" + str(generation_ind) + ".npy"
    error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(generation_ind) + ".data"
    error_list_an2_path = res_dir + "/error_list_an2_ind" + str(generation_ind) + ".data"
    error_list_both_path = res_dir + "/error_list_both_ind" + str(generation_ind) + ".data"

    save_info(results[0], name_catalog1_path)
    save_info(results[1], name_catalog2_path)
    np.save(stat_matrix_path, results[2])
    save_info(results[3], error_list_an1_path)
    save_info(results[4], error_list_an2_path)
    save_info(results[5], error_list_both_path)


def load_comparison(res_dir, generation_ind):

    name_catalog1_path = res_dir + "/name_catalog1_ind" + str(generation_ind) + ".data"
    name_catalog2_path = res_dir + "/name_catalog2_ind" + str(generation_ind) + ".data"
    stat_matrix_path = res_dir + "/stat_matrix" + str(generation_ind) + ".npy"
    error_list_an1_path = res_dir + "/error_list_an1_path_ind" + str(generation_ind) + ".data"
    error_list_an2_path = res_dir + "/error_list_an2_ind" + str(generation_ind) + ".data"
    error_list_both_path = res_dir + "/error_list_both_ind" + str(generation_ind) + ".data"

    return load_info(name_catalog1_path), \
        load_info(name_catalog2_path), \
        np.load(stat_matrix_path), \
        load_info(error_list_an1_path), \
        load_info(error_list_an2_path), \
        load_info(error_list_both_path)


def print_comparison(comparison_results, mode="stat"):
    if mode == "stat":
        print_numpy(comparison_results[2], comparison_results[0], comparison_results[1])
        return
    error_list = None
    if mode == "er1":
        error_list = comparison_results[3]
    if mode == "er2":
        error_list = comparison_results[4]
    if mode == "er_both":
        error_list = comparison_results[5]

    if error_list:
        for el in error_list:
            print(el)

    return None