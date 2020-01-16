import re
import os
import sys

'''
OUTPUT TEMPLATE:

dbutils.widgets.dropdown("parse", "address", ["address", "street", "number"])
parse = dbutils.widgets.get("parse")
'''

site_packages_path = r"C:\Users\wmorfed\AppData\Local\Programs\Python\Python37\Lib\site-packages" # Change path here!
LIBRARY_NAME = ''; FUNCTION_NAME = ''; RET = {}
try:
    LIBRARY_NAME = "lxml" # sys.argv[1]
    FUNCTION_NAME = "html_annotate" # sys.argv[2]
except IndexError:
    print("Error, run from cli!\n\t(ex: `python param_finder.py pandas read_excel`)")


def code_parser(var_name):
    pass

def get_folders(lst):
    nlst = []
    for i in lst:
        if '.' not in str(i) and not re.search(r"^__\w+__$", str(i)):
            try:
                os.chdir(str(i))
                os.chdir("..")
                nlst.append(str(i))
            except FileNotFoundError:
                pass
    return nlst

def build_dict(params): # Populate 'ret' dictionary to be returned
    for param in params:
        p_name = re.search(r"^\w+", param)
        if p_name:
            if '=' in param:
                RET[p_name.group()] = {'default_value': None, 'possible_values': []}
            else:
                RET[p_name.group()] = None

def search_cwd(path, func): # If function found call build_dict() & return module path; If function not found in cwd return None
    for pyFile in os.listdir():
        if re.search(r".py$", pyFile):
            with open(pyFile, 'r') as pf:
                for line in pf.readlines():
                    if re.search(fr"^def {func}\(", line): # KEY FEATURE: Check if function exists
                        if re.search(r"\(.*\)", line):
                            lst = re.search(r"\(.*\)", line).group().strip("()").replace(' ', '').split(",")
                            build_dict(lst) # Populate 'ret' dictionary to be returned
                            return path + '/' + pyFile
    for folder in get_folders(os.listdir()):
        os.chdir(folder)
        search_cwd(path + '/' + folder, func)
        os.chdir("..")

def recur_find(path, func): # Return relavent module path
    return search_cwd(path, func)

def feof(module):
    with open(module, 'r') as f:
        lines = f.readlines()
        ind = 0; Ln = 0; ret = []
        for line in lines:
            Ln += 1
            line = fr"{line}".strip('\n')
            get = re.search(r"^( |\t)+", line)
            if line == '':
                ret.append(-1)
            elif get != None:
                if len(get.group()) > ind:
                    ind = len(get.group())
                ret.append(0)
            else:
                ind = 0
                ret.append(Ln)
        return ret

def main(pckg, func):
    LS = os.listdir(site_packages_path); line_marks = 0
    if pckg in LS:
        os.chdir(site_packages_path + '/' + pckg)
        module = recur_find(site_packages_path, func)
        print(module)
        if module != None:
            line_marks = feof(module)

if __name__ == "__main__":
    main(LIBRARY_NAME, FUNCTION_NAME)
    print(RET)