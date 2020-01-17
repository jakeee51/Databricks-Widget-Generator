# -*- coding: utf-8 -*-
'''
Author: David J. Morfe
Application Name: Databricks Widget Code Generator
Functionality Purpose: A code generator for the Databricks platform that searches for function parameters and their properties
Version: Beta 0.1.0
'''
#1/17/20

import re
import os
import sys
import site

'''
OUTPUT TEMPLATE:

dbutils.widgets.dropdown("parse", "address", ["address", "street", "number"])
parse = dbutils.widgets.get("parse")
'''

for i in site.getsitepackages():
    if "site-packages" in i:
        site_packages_path = i
LIBRARY_NAME = ''; FUNCTION_NAME = ''; RET = {}; template = []
try:
    LIBRARY_NAME = "GeoLiberator"     # sys.argv[1]
    FUNCTION_NAME = "autoGeoLiberate"  # sys.argv[2]
except IndexError:
    print("Error, run from cli!\n\t(ex: `python param_finder.py pandas read_excel`)")

def comp(param: str, wType: int) -> list:
    if RET[param]['default_value'] != '':
        if wType == 0:                
            template.append(f"dbutils.widgets.dropdown('{param}', '{RET[param]['default_value']}', {RET[param]['possible_values']})"
                            f"\n{param} = dbutils.widgets.get('{param}')")
        elif wType == 1:
            template.append(f"dbutils.widgets.combobox('{param}', '{RET[param]['default_value']}', {RET[param]['possible_values']})"
                            f"\n{param} = dbutils.widgets.get('{param}')")
        elif wType == 0:
            template.append(f"dbutils.widgets.text('{param}', '{RET[param]['default_value']}')"
                            f"\n{param} = dbutils.widgets.get('{param}')")
    else:
        template.append(f"dbutils.widgets.text('{param}', '')"
                        f"\n{param} = dbutils.widgets.get('{param}')")
    return template

def possible_grab(code, param): # Parses the possible values of a parameter and returns Databricks Widget Type
    start = -1; Ln = 0
    for line in code:
        Ln += 1; space_check = re.search(r"^ *", line)
        get = re.search(fr"if .*{param}.*?==.*?(\w+)", line)
        if get:
            if get.group(1) not in RET[param]["possible_values"]:
                start = space_check.group().count(' ')
                RET[param]["possible_values"].append(get.group(1))
        elif space_check.group().count(' ') == start and "else" in line:
            return 1 #combobox
    if RET[param] == None:
        return 2 #textbox
    return 0 #dropdown

def func_grab(pyFile, func): # Parses the function from the code and returns a list
    start = -1; Ln = 0; ret = []
    with open(pyFile, 'r', encoding="utf8") as pf:
        for line in pf.readlines():
            Ln += 1; space_check = re.search(r"^ *", line)
            if re.search(fr"^def {func}\(", line):
                start = space_check.group().count(' ')
                ret.append(line.strip('\n'))
            elif space_check.group().count(' ') == start:
                return ret
            elif start != -1:
                ret.append(line.strip('\n'))

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
                RET[p_name.group()] = {'default_value': re.search(r"(?<==).+", param).group().strip("'\""), 'possible_values': []}
            else:
                RET[p_name.group()] = {'default_value': '', 'possible_values': []}

def recur_search(path, func): # If function found call build_dict() & return module path; If function not found in cwd return None
    for pyFile in os.listdir():
        if re.search(r"\.py$", pyFile):
            with open(pyFile, 'r', encoding="utf8") as pf:
                for line in pf.readlines():
                    if re.search(fr"^def {func}\(", line): # KEY FEATURE: Check if function exists
                        if re.search(r"\(.*\)", line):
                            lst = re.search(r"\(.*\)", line).group().strip("()").replace(' ', '').split(",")
                            build_dict(lst) # Populate 'ret' dictionary to be returned
                            return path + '/' + pyFile
    for folder in get_folders(os.listdir()):
        os.chdir(folder)
        mod = recur_search(path + '/' + folder, func)
        os.chdir("..")
        if mod != None:
            return mod

def feof(module): # Find End Of Function - Creates & counts list of left most lines of code and no code in a line
    with open(module, 'r', encoding="utf8") as f:
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
    LS = os.listdir(site_packages_path); line_marks = 0; lst = []
    if pckg in LS:
        os.chdir(site_packages_path + '/' + pckg)
        module = recur_search(site_packages_path + '/' + pckg, func)
        if module != None:
            for param in RET:
                func_code = func_grab(module, func)
                widget_type = possible_grab(func_code, param)
                RET[param]['default_value']
                lst = (comp(param, widget_type))
    return lst

if __name__ == "__main__":
    for line_of_Databricks_code in main(LIBRARY_NAME, FUNCTION_NAME):
        print(line_of_Databricks_code)
