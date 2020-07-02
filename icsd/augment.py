#%%
from pathlib import Path
import pandas as pd
import re  #regular expressions


HERE = Path(__file__).parent
PARENT = Path(__file__).parent.parent
ORIG_PKL = str(HERE/"all_icsd_cifs.pkl")
AUGMENTED_PKL = str(HERE/"all_icsd_cifs_augmented.pkl")


def robust_str_split(s):  # from https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
    def strip_quotes(s):
        if s and (s[0] == '"' or s[0] == "'") and s[0] == s[-1]:
            return s[1:-1]
        return s
    return [strip_quotes(p).replace('\\"', '"').replace("\\'", "'") \
            for p in re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|[^\s]+', s)]


def find_str_between(left, right, input_str):
    ''' isolate the substring between two string
    from: https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
    with modification: https://stackoverflow.com/questions/24867342/regex-get-string-between-two-strings-that-has-line-breaks
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

if __name__=="__main__":
    orig_df = pd.read_pickle(ORIG_PKL)
    augmented_df = extract_cif_columns(orig_df)
    print(augmented_df)
     # augmented_df.to_pickle(AUGMENTED_PKL)

#%%

# MP_PKL = str(PARENT/"mp"/"materials_project_all.pkl")
# mpdf = pd.read_pickle(MP_PKL)


#%%

# #%%
# for ii in range(len(mpdf)):
#     if mpdf.icsd_ids[ii]:

#         mp_formula = mpdf.pretty_formula[ii]
#         icsd_ids = mpdf.icsd_ids[ii]
#         print(f"MP {mp_formula}  in ICSD:")
#         # print(f"  icsd_ids: {icsd_ids}")
#         for icsd_id in icsd_ids:
#             entry = icsd_df.loc[icsd_df['_database_code_ICSD']==str(icsd_id)]
#             try:
#                 cif = entry.iloc[0]['cif']  ## it is complicated to extract the string from a dataframe
#                 cif_as_list = robust_str_split(cif)
#                 icsd_formula = cif_as_list[cif_as_list.index('_chemical_formula_structural')+1]
#                 print(f"  {icsd_formula}")
#             except:
#                 pass
#         # break
