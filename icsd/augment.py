#%%
import pandas as pd
import re  #regular expressions

def robust_str_split(s):  # from https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
    def strip_quotes(s):
        if s and (s[0] == '"' or s[0] == "'") and s[0] == s[-1]:
            return s[1:-1]
        return s
    return [strip_quotes(p).replace('\\"', '"').replace("\\'", "'") \
            for p in re.findall(r'"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\'|[^\s]+', s)]

def find_str_between(left, right, in_str):  # from https://stackoverflow.com/questions/3368969/find-string-between-two-substrings
    return re.search(f'{left}(.*){right}', in_str).group(1)

def get_database_code(cif_str):
    return find_str_between("_database_code_ICSD ", "\n", cif_str)

def get_formula(cif_str):
    return find_str_between("_chemical_formula_sum ", "\n", cif_str).remove(" ")


icdf = pd.read_pickle("all_icsd_cifs.pkl")
mpdf = pd.read_pickle("../MP/materials_project_full_dataframe.pkl")

new_column_list = [
    '_database_code_ICSD',
    # '_chemical_name_common',
    '_chemical_formula_structural',
    '_chemical_formula_sum',
    # '_chemical_name_structure_type',
    # '_exptl_crystal_density_diffrn',
    # '_diffrn_ambient_pressure',
    # '_cell_length_a',
    # '_cell_length_b',
    # '_cell_length_c',
    # '_cell_angle_alpha',
    # '_cell_angle_beta',
    # '_cell_angle_gamma',
    # '_cell_volume',
    # '_cell_formula_units_Z',
    # '_space_group_name_H-M_alt',
    # '_space_group_IT_number',
]

for cif_row_str in new_column_list:
    tmp_function = lambda s: find_str_between(cif_row_str, "\n", s)
    icdf[cif_row_str] = icdf['cif'].apply(tmp_function)

icdf



# #%%
# for ii in range(len(mpdf)):
#     if mpdf.icsd_ids[ii]:

#         mp_formula = mpdf.pretty_formula[ii]
#         icsd_ids = mpdf.icsd_ids[ii]
#         print(f"MP {mp_formula}  in ICSD:")
#         # print(f"  icsd_ids: {icsd_ids}")
#         for icsd_id in icsd_ids:
#             entry = icdf.loc[icdf['_database_code_ICSD']==str(icsd_id)]
#             try:
#                 cif = entry.iloc[0]['cif']  ## it is complicated to extract the string from a dataframe
#                 cif_as_list = robust_str_split(cif)
#                 icsd_formula = cif_as_list[cif_as_list.index('_chemical_formula_structural')+1]
#                 print(f"  {icsd_formula}")
#             except:
#                 pass
#         # break
