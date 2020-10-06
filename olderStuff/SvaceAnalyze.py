import bs4
import requests
#from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support import ui
from lxml import etree as et
from lxml import html as ht
import re
import string
import numpy as np
import lxml
from operator import itemgetter
print("ANALYSIS START")
print(6081 + 12 + 198 + 285 + 166 + 184 + 71 + 10 + 563 + 12 + 396 + 344 + 192 + 228 + 32 + 20 + 604 + 250 + 100 + 55 + 150)

def rm_extra_info(cwe_str):
    pathlen = 23
    cwe_str = cwe_str[pathlen:]
    sind = 0
    for ind in range(len(cwe_str)):
        if cwe_str[sind] == "/":
            break
        sind += 1

    return cwe_str[sind + 5:]

#print(rm_extra_info("/home/nick/C/testcases/CWE483_Incorrect_Block_Delimitation/s01/CWE483_Incorrect_Block_Delimitation__if_without_braces_multiple_lines_01.c"))

def lists_compile (juliet_dir, svace_res_dir, cwe_num_list):

    manifest_path = juliet_dir + "/" + "manifest.xml"

    manifest_tree = et.parse(manifest_path, parser=et.XMLParser(remove_blank_text=True))
    manifest_root = ht.tostring(manifest_tree)
    manifest_soup = bs4.BeautifulSoup(manifest_root, features="lxml")
    re_expr = str(
        cwe_num_list[0][0] + "*" + "|" +
        cwe_num_list[1][0] + "*" + "|" +
        cwe_num_list[2][0] + "*"
    )
    testcases = manifest_soup.find_all("testcase")
    list_Warn_man = []
    list_cmp = []
    for case in testcases:
        testcase_list = []
        border = 0
        found = case.find_all(attrs={"path": re.compile(re_expr)})
        for file in found:

            has_flaw = False
            testcase_list.append([file["path"]])
            flaws = file.find_all("flaw")
            for flaw in flaws:
                has_flaw = True
                for ind in range(border, len(testcase_list)):
                    testcase_list[ind].append(int(flaw["line"]))
            if has_flaw:
                border = len(testcase_list)

        for file in testcase_list:
            list_Warn_man.append(file)

    list_Warn_man.sort(key=itemgetter(0))

    res_tree = et.parse(svace_res_dir, parser=et.XMLParser(remove_blank_text=True))
    res_root = ht.tostring(res_tree)
    res_soup = bs4.BeautifulSoup(res_root, features="lxml")

    list_warn_sv = []
    loc_warn_sv = []
    #print(res_soup)
    sum = 0
    for ls in cwe_num_list:
        re_expr = "/home/nick/" + "C" + "/" + "testcases/" + ls[0] + "/" + ls[1] + "/" + ls[0] + "*"

        found = res_soup.find_all("warninfo", attrs={"file": re.compile(re_expr)})
        sum += len(found)
        #print(found)
        foundloc = res_soup.find_all("warninfoex")
        for warnloc in foundloc:
            loc_warn = []
            loc_lines = []
            name = ""

            buffer_found = warnloc.find_all("roletraceinfo")

            for trace in buffer_found:
                if trace["role"] != "counter-example":
                    for locinf in trace.find_all("locinfo", attrs={"file": re.compile(re_expr)}):
                        if locinf["file"][23:] == 'CWE121_Stack_Based_Buffer_Overflow__CWE129_connect_socket_51a.c':
                            print("{} GODLIKE".format(locinf["line"]))
                        if name == "":
                            name = rm_extra_info(locinf["file"])

                            #if name == "CWE121_Stack_Based_Buffer_Overflow__CWE129_connect_socket_01.c":
                             #   print(locinf["line"])

                            loc_warn.append(name)
                        loc_lines.append(int(locinf["line"]))
            #print("END")

            if len(loc_warn) > 0 and loc_warn[0][0:3] == "CWE":
                loc_warn.append(loc_lines)
                loc_warn_sv.append(loc_warn)


        #print(loc_warn_sv[3])
        #for el in loc_warn_sv:
            #print(el[0][0:2])
            #if el[0][0:3] != "CWE":
         #       print(el)
        #print(len(loc_warn_sv))


        for warn in found:
            warning = []

            warning.append(rm_extra_info(warn["file"]))
            #warning.append(int(warn["line"]))
            warning.append(None)
            warning.append(warn['warnclass'])
            list_warn_sv.append(warning)

    loc_warn_sv.sort(key=itemgetter(0))
    list_warn_sv.sort(key=itemgetter(0))
    for ind in range(len(list_warn_sv)):
        list_warn_sv[ind][1] = loc_warn_sv[ind][1]
    #print(len(list_warn_sv))
    return list_Warn_man, list_warn_sv, list_cmp

def srch_lines(lst, targ):
    res_lst = []

    #print(len(lst))
    #print(targ)
    for el_ind in range(len(lst)):
        #print(lst[el_ind])
        if lst[el_ind][0] == targ:
            res_lst.append(el_ind)
   
    return res_lst
    #         if len(manelem) > 1:
    #             if manelem[1] == svelem[1]:
    #                 return 0
    #         else:
    #             return 1
    # if len(manelem) < 2:
    #     return 0
    # return -1

def gen_s(num):
    res = '('
    for i in range(1, num+1):
        if i < 10:
            res += "s0"
        else:
            res += "s"
        res += str(i)
        if i < num:
            res += "|"
    res += ')'
    return res

def lists_compare(manlist, svlist, cmplist):

    for warning_ind in range(len(cmplist)):

        man_warn_lines = []
        if len(manlist[warning_ind]) > 1:
            for ln in range(1, len(manlist[warning_ind])):
                man_warn_lines.append(manlist[warning_ind][ln])

        man_warn_lines.sort()
        #print('ELEM')
        #print(man_warn_lines)

        sv_warn_lines = []
        sv_inds = srch_lines(svlist, manlist[warning_ind][0])

        for ind in sv_inds:
            sv_warn_lines.append(svlist[ind][1])

        #print(sv_warn_lines)
        true_pos_count = 0

        for line in man_warn_lines:
            if line in sv_warn_lines:
                #print("PEPEGA")
                true_pos_count += 1
                sv_warn_lines.remove(line)
                man_warn_lines.remove(line)

        # how many false negatives
        cmplist[warning_ind].append(len(man_warn_lines))
        # how many false positives
        cmplist[warning_ind].append(len(sv_warn_lines))
        #how many true positives
        cmplist[warning_ind].append(true_pos_count)

    return cmplist

def analyze_cmp_list(cmp_list):

    result = [["CWE121", 0, 0, 0, 0],
              ["CWE122", 0, 0, 0, 0],
              ["CWE134", 0, 0, 0, 0]]

    for el in cmp_list:
        if el[0][:6] == "CWE121":
            result[0][1] += 1
            result[0][2] += el[1]
            result[0][3] += el[2]
            result[0][4] += el[3]
        if el[0][:6] == "CWE122":
            result[1][1] += 1
            result[1][2] += el[1]
            result[1][3] += el[2]
            result[1][4] += el[3]
        if el[0][:6] == "CWE134":
            result[2][1] += 1
            result[2][2] += el[1]
            result[2][3] += el[2]
            result[2][4] += el[3]

    return result

def srch_single_list(lst, targ):
    for el in lst:
        if el[0] == targ[0]:
            return el
    return None
def precision_compare(manlist, svlist):

    cmpl_list = []
    for svwarning in svlist:
        verdict = 'FalsePos'
        srch = srch_single_list(manlist, svwarning)
        if srch == None:
            print(svwarning)
        if srch:
            if len(srch) > 1:
                man_lines = srch[1:]
            #print("PEPEGA")
            #print(svwarning[1])
            #print(man_lines)
                for pos_line in svwarning[1]:
                    if pos_line in man_lines:
                        verdict = 'TruePos'
                        break
            cmpl_list.append([svwarning[0], svwarning[1], svwarning[2], verdict])



    print(len(svlist))
    print(len(cmpl_list))
    return cmpl_list

def recall_compare(manlist, svlist):
    cmpl_list = []
    for testcase in manlist:
        man_lines = testcase[1:]

        sv_warn_lines = []
        sv_warn_types = []
        sv_inds = srch_lines(svlist, testcase[0])

        for ind in sv_inds:
            for line in svlist[ind][1]:
                sv_warn_lines.append(line)
            sv_warn_types.append(svlist[ind][2])

        for line in man_lines:
            if line in sv_warn_lines:
                # print("PEPEGA")
                sv_warn_lines.remove(line)
                man_lines.remove(line)

        verdict = 'FalseNegative'
        if len(man_lines) == 0:
            verdict = 'TrueNegative'
        cmpl_list.append([manlist[0], sv_warn_types, verdict])

    return cmpl_list

def analyze(mode, lst):

    if mode == 0:
        truepos = 0
        falsepos = 0
        for el in lst:
            if el[3] == "TruePos":
                truepos += 1
            else:
                falsepos += 1
    if mode == 1:
        errors = set()
        lst121 = []
        lst122 = []
        lst134 = []

        lst121er = []
        lst122er = []
        lst134er = []
        for warn in lst:
            if warn[0][0:6] == "CWE121":
                if warn[2] not in lst121er:
                    lst121er.append(warn[2])
                    lst121.append([0, 0])
                for ind in range(len(lst121)):
                    if warn[2] == lst121er[ind]:
                        lst121[ind][1] += 1
                        if warn[3] == "TruePos":
                            lst121[ind][0] += 1
                        break
            if warn[0][0:6] == "CWE122":
                if warn[2] not in lst122er:
                    lst122er.append(warn[2])
                    lst122.append([0, 0])
                for ind in range(len(lst122)):
                    if warn[2] == lst122er[ind]:
                        lst122[ind][1] += 1
                        if warn[3] == "TruePos":
                            lst122[ind][0] += 1
                        break
            if warn[0][0:6] == "CWE134":
                if warn[2] not in lst134er:
                    lst134er.append(warn[2])
                    lst134.append([0, 0])
                for ind in range(len(lst134)):
                    if warn[2] == lst134er[ind]:
                        lst134[ind][1] += 1
                        if warn[3] == "TruePos":
                            lst134[ind][0] += 1
                        break

        sum = 0
        sumers = 0
        print("CWE121 ERRORS:")
        for ind in range(len(lst121)):
            sum += lst121[ind][1]
            sumers += lst121[ind][0]
            print("{}: {}/{} {}".format(lst121er[ind], lst121[ind][0], lst121[ind][1], lst121[ind][1] - lst121[ind][0]))
        print("CWE122 ERRORS:")
        for ind in range(len(lst122)):
            sum += lst122[ind][1]
            sumers += lst122[ind][0]
            print("{}: {}/{} {}".format(lst122er[ind], lst122[ind][0], lst122[ind][1], lst122[ind][1] - lst122[ind][0]))
        print("CWE134 ERRORS:")
        for ind in range(len(lst134)):
            sum += lst134[ind][1]
            sumers += lst134[ind][0]
            print("{}: {}/{} {}".format(lst134er[ind], lst134[ind][0], lst134[ind][1], lst134[ind][1] - lst134[ind][0]))

        return sumers, sum

    if mode == 2:
        lst121 = []
        lst122 = []
        lst134 = []

        lst121er = []
        lst122er = []
        lst134er = []
        for warn in lst:
            if warn[0][0:6] == "CWE121":
                if warn[2] not in lst121er:
                    lst121er.append(warn[2])
                    lst121.append([])
                for ind in range(len(lst121er)):
                    if warn[2] == lst121er[ind]:
                        if warn[3] == "FalsePos":
                            lst121[ind].append([warn[0], warn[1]])
                        break
            if warn[0][0:6] == "CWE122":
                if warn[2] not in lst122er:
                    lst122er.append(warn[2])
                    lst122.append([])
                for ind in range(len(lst122er)):
                    if warn[2] == lst122er[ind]:
                        if warn[3] == "FalsePos":
                            lst122[ind].append([warn[0], warn[1]])
                        break
            if warn[0][0:6] == "CWE134":
                if warn[2] not in lst134er:
                    lst134er.append(warn[2])
                    lst134.append([])
                for ind in range(len(lst134er)):
                    if warn[2] == lst134er[ind]:
                        if warn[3] == "FalsePos":
                            lst134[ind].append([warn[0], warn[1]])
                        break
        for err in range(len(lst121)):
            print(" {}: {}".format(lst121er[err], len(lst121[err])))
            for el in lst121[err]:
                print(el)
        for err in range(len(lst122)):
            print(" {}: {}".format(lst122er[err], len(lst122[err])))
            for el in lst122[err]:
                print(el)
        for err in range(len(lst134)):
            print(" {}: {}".format(lst134er[err], len(lst134[err])))
            for el in lst134[err]:
                print(el)

        return 0
    return truepos, falsepos



#driver = webdriver.Firefox()
#driver.get(url)

#python_button = driver.find_element_by_xpath("//a[3]")
#python_button.click()

#python_button = driver.find_element_by_class_name(name="Select-placeholder")
#all_options = python_button.find_elements_by_tag_name("option")
#for option in all_options:
 #   print("Value is: %s" % option.get_attribute("value"))
  #  option.click()
#driver.find_element_by_xpath("//select[@name='element_name']/option[text()='option_text']").click()
#python_button = driver.find_elements_by_xpath("//*[contains(text(), 'Choose project')]")
#python_button.click()

#url = 'http://127.0.0.1:8060' # url для второй страницы

#r = requests.get(url)
#with open('/home/nick/test.html', 'w') as output_file:
 #   r.encoding='utf-8'
  #  output_file.write(r.text)

#page = requests.get(url)
#soup = bs4.BeautifulSoup(page.text, "html.parser")
#print(soup)
