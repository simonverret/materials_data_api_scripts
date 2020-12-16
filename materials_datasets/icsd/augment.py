#!/usr/bin/env python3

from pathlib import Path
import re  #regular expressions

import pandas as pd

HERE = Path(__file__).parent
PARENT = Path(__file__).parent.parent
ORIG_PKL = str(HERE/"all_icsd_cifs.pkl")
AUGMENTED_PKL = str(HERE/"all_icsd_cifs_augmented.pkl")
FORMULA_CSV = str(HERE/"icsd_all_formulas.csv")
INT_FORMULA_SUM_CSV = str(HERE/"icsd_formula_sum_integer.csv")
INT_FORMULA_STRUCT_CSV = str(HERE/"icsd_formula_structural_integer.csv")


def robust_str_split(s):
    ''' split a string `s` at its whitespaces without breaking quoted substrings
    from https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
    '''
    def strip_quotes(s):
        if s and (s[0] == '"' or s[0] == "'") and s[0] == s[-1]:
            return s[1:-1]
        return s
    return [strip_quotes(p).replace('\\"', '"').replace("\\'", "'") \
            for p in re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|[^\s]+', s)]


def find_str_between(left, right, input_str):
    ''' isolate the substring between two specified substrings
    from: https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
    with modification: https://stackoverflow.com/questions/24867342/regex-get-string-between-two-strings-that-has-line-breaks
    try it here: https://regex101.com/r/qqbZqh/30
    '''
    out = re.search(left+"(.*?)"+right, input_str, flags=re.S)
    return out.group(1)


def get_cif_field(field_name, cif_str):
    value = find_str_between(field_name, "\n_", cif_str)
    value = value.replace(" ","")
    value = value.replace("loop_","")
    value = value.replace("\n","")
    return value


def get_cif_formula_field(field_name, cif_str):
    value = get_cif_field(field_name, cif_str)
    value = value.replace(";","")
    value = value.replace("'","")
    return value


def get_cif_float_field(field_name, cif_str):
    return float(get_cif_field(field_name, cif_str))


def extract_cif_columns(df):
    field_list = [
        "_database_code_ICSD",
    ]
    formula_list = [
        "_chemical_formula_structural",
        "_chemical_formula_sum",
    ]
    float_list = [
        "_cell_length_a",
        "_cell_length_b",
        "_cell_length_c",
        "_cell_angle_alpha",
        "_cell_angle_beta",
        "_cell_angle_gamma",
        "_cell_volume"
    ]
    for field in field_list:
        tmp_function = lambda s: get_cif_field(field, s)
        df[field] = df['cif'].apply(tmp_function)
    
    for field in formula_list:
        tmp_function = lambda s: get_cif_formula_field(field, s)
        df[field] = df['cif'].apply(tmp_function)

    for field in float_list:
        tmp_function = lambda s: get_cif_float_field(field, s)
        df[field] = df['cif'].apply(tmp_function)
    return df


def fraction_composition(s):
    return not (("." in s) or ("(" in s))


if __name__=="__main__":
    orig_df = pd.read_pickle(ORIG_PKL)
    
    icsd_df = extract_cif_columns(orig_df)
    icsd_df.to_pickle(AUGMENTED_PKL)
    
    icsd_df_no_cif = icsd_df.drop(columns=['cif'])
    icsd_df_no_cif.to_csv(FORMULA_CSV)    
    
    icsd_df_formulas_sum_int = icsd_df_no_cif.loc[icsd_df['_chemical_formula_sum'].apply(fraction_composition)]
    icsd_df_formulas_sum_int.to_csv(INT_FORMULA_SUM_CSV)    
    
    icsd_df_formulas_struct_int = icsd_df_no_cif.loc[icsd_df['_chemical_formula_structural'].apply(fraction_composition)]
    icsd_df_formulas_struct_int.to_csv(INT_FORMULA_STRUCT_CSV)    
    