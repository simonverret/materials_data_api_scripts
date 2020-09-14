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

mpdf = pd.read_pickle(MATERIALS_PROJECT_PKL)
icsdf = pd.read_pickle(ICSD_AUG_PKL)
oqmdf = pd.read_pickle(OQMD_PKL)


#%% PRINT BASIC INFO ABOUT THE DATASETS
for name, dataset in {'MP':mpdf, 'OQMD':oqmdf, 'ICSD':icsdf}.items():
    print(f"\nloaded {len(dataset)} materials from {name}")
    print("available columns")
    for column in list(dataset.columns): 
        print(" ",column)


#%% ICSD WITH INTEGER FORMULA DOPING ONLY
def fraction_composition(s):
    return not ("." in s)

int_sum_icsdf = icsdf.loc[ icsdf['_chemical_formula_sum'].apply(lambda s: not (("." in s) or ("(" in s))) ]
print(f"{len(int_sum_icsdf)}/{len(icsdf)} materials from OQMD have no '.' in their sum formula")
int_struct_icsdf = icsdf.loc[ icsdf['_chemical_formula_structural'].apply(lambda s: not (("." in s) or ("(" in s))) ]
print(f"{len(int_struct_icsdf)}/{len(icsdf)} materials from OQMD have no '.' in their structural formula")


#%% SUBSET and CITRINE
print("CITRINE:")

print("\n\nSUBSET:")
subset_ids = pd.read_csv(SUBSET_MPIDS_CSV, names=["material_id"])
print(len(subset_ids), "material_ids")
subset_mpdf = mpdf[mpdf["material_id"].isin(subset_ids["material_id"])]
print(len(subset_mpdf), "materials selected")
print(len(subset_mpdf)-len(subset_ids), "missing; all subset ids were found")
print(len(mpdf)-len(subset_mpdf), "missing from subset")

print("\n\nCITRINE:")
citrine_df = pd.read_pickle(CITRINE_MP_PKL)
print(f"loaded {len(citrine_df)} materials")
print("\navailable columns:")
for name in list(citrine_df.columns): print(" ",name)

mpdf_in_citrine = mpdf[mpdf["material_id"].isin(citrine_df["material_id"])]
print(f"\n{len(mpdf_in_citrine)} in mpdf/{len(citrine_df)} in citrine, {len(citrine_df)-len(mpdf_in_citrine)} ids of citrine are not in mpdf") 

subset_mpdf_in_citrine = mpdf[mpdf["material_id"].isin(citrine_df["material_id"])]
print(f"{len(subset_mpdf_in_citrine)} in mpdf/{len(citrine_df)} in citrine, {len(citrine_df)-len(subset_mpdf_in_citrine)} ids of citrine are not in subset") 

citrine_in_mpdf = citrine_df[citrine_df["material_id"].isin(mpdf_in_citrine["material_id"])]
citrine_not_in_mpdf = citrine_df[~citrine_df["material_id"].isin(mpdf_in_citrine["material_id"])]

print("\ncommon columns")
for name in list(citrine_in_mpdf.columns):
    if name in list(mpdf_in_citrine.columns):
        print(" ",name)

print("\nSorting...")
citrine_in_mpdf = citrine_in_mpdf.sort_values("material_id", ignore_index=True)
mpdf_in_citrine = mpdf_in_citrine.sort_values("material_id", ignore_index=True)
print(f"{all(citrine_in_mpdf['material_id']==mpdf_in_citrine['material_id'])} : all ids are the same")
print(f"{all(citrine_in_mpdf['pretty_formula']==mpdf_in_citrine['pretty_formula'])} : all pretty_formula are the same")

print("\nICSD ids")
print(f"{len(citrine_df[citrine_df['icsd_ids'].astype(bool)])}/{len(citrine_df)} of CITRINE have ICSD ids (all of them)")
print(f"{len(mpdf[mpdf['icsd_ids'].astype(bool)])}/{len(mpdf)} of current MP have ICSD ids")
print(f"{len(citrine_df[citrine_df['icsd_ids'].astype(bool)])-len(mpdf[mpdf['icsd_ids'].astype(bool)])} have no ICSD id anymore")
print(f"Probably has to do with CITRINE being from January 2019")

for column in [
    "final_energy",
    "final_energy_per_atom",
    "volume",
    "nsites",
    "formation_energy_per_atom",
    "e_above_hull",
    "band_gap",
    "total_magnetization",
]:
    x = citrine_in_mpdf[column].rename(f"updated_{column}")
    y = mpdf_in_citrine[column].rename(f"citrine_{column}")
    plot_df = pd.concat([x, y], axis=1)
    plot_df.plot.scatter(f"citrine_{column}",f"updated_{column}")
    plt.title(f"{column}\nonly {len(citrine_in_mpdf[citrine_in_mpdf[column]==mpdf_in_citrine[column]])}/{len(citrine_in_mpdf)} are the same")
    plt.savefig(PLOTS_DIR/f"updated_citrine_{column}")


#%% ICSD? Stable?
have_icsd = mpdf[mpdf['icsd_ids'].astype(bool)]
print(f"\n{len(have_icsd)} entries have ICSD IDs")
stable_icsd = mpdf[ (mpdf['icsd_ids'].astype(bool)) & (mpdf["e_above_hull"] <= 0)]
print(f"{len(stable_icsd)} entries have ICSD IDs and are stable")

no_warnings = mpdf[(~mpdf['warnings'].astype(bool)) & (mpdf["e_above_hull"] <= 0)]
print(f"{len(no_warnings)} entries have no warnings and are stable")


#%% ARE THE STRUCRURES VERmpdf_in_citrine DIFFERENT IN OQMD, ICSD, MP?






#%% ################ 
# ADVANCED MINING
####################




#%% ISCD CIF CONTAINS SUBSTRING with CIF example
substr = "abin"
icsdf_with_substr = icsdf['cif'].loc[ icsdf['cif'].apply(lambda cif: substr in cif) ]
print(f"{len(icsdf_with_substr)} contains the string '{substr}'")
print("\nexample:\n")
print(icsdf_with_substr.iloc[0])
print("\nsubstr in lines:", [line for line in icsdf_with_substr.iloc[0].split('\n') if substr in line])



# ISOLATING THE MOST STABLE COMPOUNDS
print()
stable = mpdf.loc[mpdf['e_above_hull'] <= 0]
print(f"{len(stable)} are strictly stable (e_above_hull <= 0)")
stable05 = mpdf.loc[mpdf['e_above_hull'] <= 0.1]
print(f"{len(stable05)} are weakly stable (e_above_hull <= 0.05; arbitrary criteria)")


#%% COUNTING HOW MANY COMPOUNDS WITH THE SAME FORMULA
print()
print(f"{len(mpdf.groupby('pretty_formula').size())} unique formulas in total")
print(f"{len(stable.groupby('pretty_formula').size())}/{len(stable)} unique formulas for strictly stable ")
print(f"{len(stable05.groupby('pretty_formula').size())}/{len(stable05)} unique formulas for weakly stable")


#%% WHICH ONES HAVE STABLE DUPLICATES ?
print()
print("the duplicates are")
stable_counts = stable.groupby('pretty_formula').size()
print(stable_counts.loc[lambda s: s>1])


#%% AMONG THEM EXPLORE SIO2
print()
SiO2df = mpdf.loc[mpdf["pretty_formula"] == "SiO2"]
print(f"{len(SiO2df)} instances of SiO2")


#%% WHAT IS THE FORMATION ENERGY OF SrTiO3
mpdf.loc[mpdf["pretty_formula"] == "SrTiO3"]["formation_energy_per_atom"]

#%% AMONG THEM EXPLORE F2
print()
F2df = mpdf.loc[mpdf["pretty_formula"] == "F2"]
print("nsites of the 5 F2")
for nsites in F2df['nsites']:
    print(nsites)
print("_cell_lenght_a of the 5 F2")
for cif in F2df['cif']:
    print(cif.split()[cif.split().index('_cell_length_a')+1])


#%% HOW MANY FORMULAS ARE NOT IN THE STABLE SUBSET ONES?
print()
unstable_only = mpdf[ ~mpdf['pretty_formula'].isin(stable['pretty_formula']) ]
unstable_counts = unstable_only.groupby('pretty_formula').size()
print(f"{len(unstable_only)} strictly unstable materials (e_above_hull > 0)")
print(f"{len(unstable_counts)}/{len(unstable_only)} unique formulas among those")
print(f"Thus covers {len(unstable_counts)} + {len(stable_counts)} = {len(unstable_counts)+len(stable_counts)}/{len(mpdf)} materials (consistency check)")


#%% HOW MANY FERROMAGNETS, FERRIMAGNETS AND PARAMAGNETS?
print()
ferromagnets = mpdf.loc[mpdf["ordering"] == "FM"]
ferrimagnets = mpdf.loc[mpdf["ordering"] == "FiM"]
paramagnets = mpdf.loc[mpdf["ordering"] == "NM"]
afm = mpdf.loc[mpdf["ordering"] == "AFM"]
print(f"{len(ferromagnets)} ferromagnets")
print(f"{len(ferrimagnets)} ferrimagnets")
print(f"{len(paramagnets)} paramagnets")
print(f"{len(afm)} afm")

print()
stable_ferromagnets = mpdf.loc[(mpdf["ordering"] == "FM") & (mpdf["e_above_hull"] <= 0)]
stable_ferrimagnets = mpdf.loc[(mpdf["ordering"] == "FiM") & (mpdf["e_above_hull"] <= 0)]
stable_paramagnets = mpdf.loc[(mpdf["ordering"] == "NM") & (mpdf["e_above_hull"] <= 0)]
stable_afm = mpdf.loc[(mpdf["ordering"] == "AFM") & (mpdf["e_above_hull"] <= 0)]
hubbard_stable_ferromagnets = mpdf.loc[mpdf["is_hubbard"] & (mpdf["ordering"] == "FM") & (mpdf["e_above_hull"] <= 0)]
hubbard_stable_ferrimagnets = mpdf.loc[mpdf["is_hubbard"] & (mpdf["ordering"] == "FiM") & (mpdf["e_above_hull"] <= 0)]
hubbard_stable_paramagnets = mpdf.loc[mpdf["is_hubbard"] & (mpdf["ordering"] == "NM") & (mpdf["e_above_hull"] <= 0)]
hubbard_stable_afm = mpdf.loc[mpdf["is_hubbard"] & (mpdf["ordering"] == "AFM") & (mpdf["e_above_hull"] <= 0)]
print(f"{len(stable_ferromagnets)} stable ferromagnets, {len(hubbard_stable_ferromagnets)} computed with hubbard U")
print(f"{len(stable_ferrimagnets)} stable ferrimagnets, {len(hubbard_stable_ferrimagnets)} computed with hubbard U")
print(f"{len(stable_paramagnets)} stable paramagnets, {len(hubbard_stable_paramagnets)} computed with hubbard U")
print(f"{len(stable_afm)} stable antiferromagnets, {len(hubbard_stable_afm)} computed with hubbard U")


#%%
print("example of an afm magmoms:")
mpdf['magmoms'].iloc[125959]


#%% MULTIPLE FILTERS EXAMPLES
print()
hubbard_stable     = mpdf.loc[(mpdf["is_hubbard"]==True) & (mpdf["e_above_hull"] <= 0)]
not_hubbard_stable = mpdf.loc[(mpdf["is_hubbard"]==False) & (mpdf["e_above_hull"] <= 0)]
print(f"{len(hubbard_stable)} stable with U")
print(f"{len(not_hubbard_stable)} stable without U") 
magnetic = mpdf.loc[(mpdf["ordering"] == "FM") | (mpdf["ordering"] == "FiM")]
mag_stable             = magnetic.loc[mpdf["e_above_hull"] <= 0]
mag_hubbard_stable     = magnetic.loc[(mpdf["is_hubbard"]==True) & (mpdf["e_above_hull"] <= 0)]
mag_not_hubbard_stable = magnetic.loc[(mpdf["is_hubbard"]==False) & (mpdf["e_above_hull"] <= 0)]
print(f"{len(magnetic)} magnetic") 
print(f"{len(mag_stable)} magnetic stable") 
print(f"{len(mag_hubbard_stable)} magnetic stable with U") 
print(f"{len(mag_not_hubbard_stable)} magnetic stable without U") 

#%% SCATTER PLOT

mpdf.plot.scatter(x='e_above_hull', y='nelements')
plt.show()


#%%
mpdf.columns

#%% PLOTS_DIR ENERGY HUBBARD
bins = 200
prop = 'formation_energy_per_atom'
plt.suptitle(prop)
# plt.yscale('log')
plt.hist(mpdf[prop], bins=2*bins, fc=(0, 0, 0, 0.7), label='all')
plt.hist(stable[prop], bins=bins, fc=(0.9, 0.8, 0, 0.8), label='stable (ab. hull <= 0)')
plt.hist(not_hubbard_stable[prop], bins=bins, fc=(0, 0.8, 0, 0.7), label='stable no U')
plt.hist(mag_stable[prop], bins=bins, fc=(1, 0, 0, 0.8), label='magnetic stable')
plt.hist(mag_not_hubbard_stable[prop], bins=bins, fc=(0, 1, 0, 1), label='mag stable no U')
plt.hist(hubbard_stable[prop], bins=bins, fc=(0, 0, 1, 0.5), label='stable with U')
plt.hist(mag_hubbard_stable[prop], bins=bins, fc=(0, 0.8, 1, 0.5), label='mag stable with U')
plt.legend()
plt.show()


#%% NUMBER OF MATERIALS CONTAINING EACH ELEMENT
list_of_elements = [
    'H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S',
    'Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga',
    'Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd',
    'Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm',
    'Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os',
    'Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa',
    'U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm','Md','No','Lr'
]

list_of_counts = [
    mag_stable.elements[mpdf.elements.apply(lambda lst: el in lst)].count()
    for el in list_of_elements
]

plt.figure(figsize=(20,4))
plt.bar(list_of_elements, list_of_counts)
plt.xlim([-0.5,len(list_of_elements)-0.5])
plt.tight_layout()
plt.savefig(PLOTS_DIR/'element_bar.png')

#%% CIF ACCESS EXAMPLE:

cif_list = mpdf["cif"][0].split()
print(f"cell parameter a: {cif_list[cif_list.index('_cell_length_a')+1]}")
print(f"cell parameter b: {cif_list[cif_list.index('_cell_length_b')+1]}")
print(f"cell parameter c: {cif_list[cif_list.index('_cell_length_c')+1]}")
