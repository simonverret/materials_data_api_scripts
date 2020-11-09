#%% IMPORTING THE FULL DATAFRAME
from pathlib import Path  ## for os-agnostic paths
import pandas as pd  ## provides a fast spreadsheet object (DataFrame)
import matplotlib.pyplot as plt  ## standard python plotting tool

HERE = Path(__file__).parent
PARENT = Path(__file__).parent.parent
PLOTS_DIR = HERE/"plots"

MATERIALS_PROJECT_PKL = str(HERE/"mp"/"materials_project.pkl")
SUBSET_MPIDS_CSV = str(HERE/"mp"/"subset_ids.csv")
CITRINE_MP_PKL = str(HERE/"mp"/"citrine_mp.pkl")

ICSD_AUG_PKL = str(HERE/"icsd"/"all_icsd_cifs_augmented.pkl")

OQMD_PKL = str(HERE/"oqmd"/"oqmd.pkl")
OQMD_CSV = str(HERE/"oqmd"/"oqmd.csv")

PTBL_PKL = str(HERE/"ptable"/"ptable.pkl")

mpdf = pd.read_pickle(MATERIALS_PROJECT_PKL)
icsdf = pd.read_pickle(ICSD_AUG_PKL)
oqmdf = pd.read_pickle(OQMD_PKL)
ptable = pd.read_pickle(PTBL_PKL)


#%% PARSING FORMULA TO DICT
import collections
import re


def get_symbol_dict(f, factor):
    symbol_dict = collections.defaultdict(float)
    for regex in re.finditer(r"([A-Z][a-z]*)\s*([-*\.e\d]*)", f):
        element = regex.group(1)
        amount = 1
        if regex.group(2).strip() != "":
            amount = float(regex.group(2))
        symbol_dict[element] += amount * factor
        f = f.replace(regex.group(), "", 1)
    if f.strip():
        raise ValueError("{} is an invalid formula!".format(f))
    return symbol_dict


def parse_formula_recursive(formula):
    formula = formula.replace("@", "")  # for Metallofullerene like "Y3N@C80"
    regex = re.search(r"\(([^\(\)]+)\)\s*([\.e\d]*)", formula)
    if regex:
        factor = 1
        if regex.group(2) != "":
            factor = float(regex.group(2))
        unit_symbol_dict = get_symbol_dict(regex.group(1), factor)
        expanded_symbol = "".join([
            f"{element}{amount}" for element, amount in unit_symbol_dict.items()
        ])
        expanded_formula = formula.replace(regex.group(), expanded_symbol)
        return parse_formula_recursive(expanded_formula)
    return get_symbol_dict(formula, 1)


def parse_formula(formula):
    return dict(parse_formula_recursive(formula))


formula = mpdf.full_formula[123456]
parse_formula(formula)


#%% COMPUTING DESCRIPTORS
import numpy as np

def prop_array(formula, prop):
    prop_arr = np.array([])
    for symbol, amount in parse_formula(formula).items(): 
        prop_val = ptable[prop].loc[symbol]
        prop_arr = np.append(prop_arr, prop_val*np.ones(int(amount)))
    return prop_arr

for col in ptable.columns: print(col)

prop_arr = prop_array(formula, "imat_electronegativity")
print(prop_arr)
print(prop_arr.max())
print(prop_arr.min())
print(prop_arr.mean())
print(prop_arr.var())


#%% RANDOM FOREST




