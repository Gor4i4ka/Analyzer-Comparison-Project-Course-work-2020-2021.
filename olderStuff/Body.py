import subprocess as sb
import bs4
import re
import sys
from lxml import etree as et
from lxml import html as ht
import lxml
from os import walk
import os
def rename():
    i=0
    for file in os.listdir("/home/nick/aaout"):
        os.rename("/home/nick/aaout/" + file, "/home/nick/aaout/" + str(i))
        i+=1

def analyze ():
    sb.run(args="clang --analyze -Xanalyzer -analyzer-output=html -o ~/aaout ~/apack/test1.c", shell=True)
    rename()

def parsing():

    dir = "/home/nick/aaout/"
    tree = et.parse(dir + "0.html", parser=et.HTMLParser(remove_blank_text=True))
    root = ht.tostring(tree)
    soup = bs4.BeautifulSoup(root)
    found = soup.find(text="Warning:")
    info1 = found.parent.parent.contents[1].contents[0].text
    line = (re.search(r"line [0-9]+", info1)).group(0)[4:]
    column = (re.search(r"column [0-9]+", info1)).group(0)[6:]
    print(line)
    print(column)
def parse_manifest(cwename, jul_path):
    man_path = jul_path + "/" + "manifest.xml"

    with open(man_path, "r") as file:
        #content = file.readlines()
        #content = "".join(content)

        tree = et.parse(man_path, parser=et.XMLParser(remove_blank_text=True))
        root = ht.tostring(tree)

        soup = bs4.BeautifulSoup(root, features="lxml")

        #found = soup.find(attrs={"name": "CWE-114: Process Control"})
        #found = soup.find(attrs={"file path": cwename})
        #found = soup.find(name="testcase")
        found = soup.find(attrs={"path": cwename})
        #print(found.contents[0])
        for flaw in found.contents:
            print("FLAW IN LINE " + flaw.attrs["line"])


def cwetool(cwename, jul_path):
    #parse_manifest(cwename, jul_path)

    testcase_path = jul_path + "/testcases"

    case_type = 0
    for dir in os.listdir(testcase_path):
        if dir[3:6] == cwename[3:6]:
            case_type = dir
            break

    if case_type == 0:
        print("CWE TYPE NOT FOUND \n")
        return 1

    testcase_path += "/" + case_type
    file_is_found = False

    for file in os.listdir(testcase_path):
        if os.path.isdir(testcase_path + "/" + file):
            for subfile in os.listdir(testcase_path + "/" + file):
                if subfile == cwename:
                    file_is_found = True
                    testcase_path += "/" + file + "/" + subfile
                    break
        if file_is_found:
            break

    if not file_is_found:
        print("CASE NOT FOUND")
        return 1

    cmd = "code " + testcase_path
    return sb.run(args=cmd, shell=True)

jul_path = "/home/nick/C"
man_path = jul_path + "/" + "manifest.xml"
tree = et.parse(man_path, parser=et.XMLParser(remove_blank_text=True))
root = ht.tostring(tree)
soup = bs4.BeautifulSoup(root, features="lxml")

cwename = input("Write your CWE ")
cwetool(cwename, jul_path)

#while True:
 #   cwename = input("Write your CWE ")
#
 #   found = soup.find(attrs={"path": cwename})
  #  for flaw in found.contents:
        #print("FLAW IN LINE " + flaw.attrs["line"])
   #     i = 1

    #cwetool("CWE121_Stack_Based_Buffer_Overflow__char_type_overrun_memcpy_01.c",
     #       jul_path
      #      )
    #proc = cwetool(cwename, jul_path)
    #while True:
     #   if proc.returncode == 0:
      #      break

#func()
#parsing()