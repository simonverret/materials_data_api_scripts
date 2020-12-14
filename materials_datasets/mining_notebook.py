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



#%% MERGE THE MP and ICSD DATAFRAME (didn't find a pandas way to do it)
icsdf_idx = icsdf.set_index(icsdf['_database_code_ICSD'].astype(int))  ## rows are now indexed by icsd_id
mpdf_idx = mpdf.set_index(mpdf['material_id'])  ## rows are now indexed by material_id

combined_rows = []
used_icsd_ids = []
wrong_icsd_ids = []
mp_rows = mpdf_idx.to_dict('records')
for mp_row in mp_rows:
    if mp_row['icsd_ids']:
        for icsd_id in mp_row['icsd_ids']:
            try: ## sometimes the icsd_id doesn't exist
                icsd_row = icsdf_idx.loc[icsd_id].to_dict()
                used_icsd_ids.append(icsd_id)
            except KeyError as e:
                wrong_icsd_ids.append(e)
                continue
            tmp_dict = {}
            for k,v in mp_row.items():
                tmp_dict['mp_'+k] = v
            for k,v in icsd_row.items():
                tmp_dict['icsd_'+k] = v
            combined_rows.append(tmp_dict)
    else:
        tmp_dict = {}
        for k,v in mp_row.items():
            tmp_dict['mp_'+k] = v
        combined_rows.append(tmp_dict)

remaining_icsd_rows = icsdf_idx.loc[~icsdf_idx.index.isin(used_icsd_ids)].to_dict('records')
for icsd_row in remaining_icsd_rows:
    tmp_dict = {}
    for k,v in icsd_row.items():
        tmp_dict['icsd_'+k] = v
    combined_rows.append(tmp_dict)

super_df = pd.DataFrame(combined_rows)


#%% PRINT BASIC INFO ABOUT THE DATASETS
for name, dataset in {'MP':mpdf, 'OQMD':oqmdf, 'ICSD':icsdf, 'super':super_df}.items():
    print(f"\nloaded {len(dataset)} materials from {name}")
    print("available columns")
    for column in list(dataset.columns): 
        print(" ",column)

#%%
icsd_mask = ~super_df['icsd__database_code_ICSD'].isna()
mp_mask = ~super_df['mp_material_id'].isna()
grouped_icsd = super_df.loc[icsd_mask & mp_mask].groupby('icsd__database_code_ICSD')
grouped_mp = super_df.loc[icsd_mask & mp_mask].groupby('mp_material_id')


#%%
print(f"{len(wrong_icsd_ids)} bad icsd_ids in the icsd_ids list in MP")
print(f"{len(grouped_mp)} materials from MP map to ICSD entries")
print(f"with maximum {grouped_mp['mp_material_id'].agg('count').max()} ICSD entries for one MP entry")
print(f"{len(grouped_icsd)} materials from ICSD map to MP entries")
print(f"with maximum {grouped_icsd['mp_material_id'].agg('count').max()} MP entries for one ICSD entry")


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
print(f"\n{len(have_icsd)} entries have ICSD ids")
stable = mpdf[mpdf["e_above_hull"] <= 0]
print(f"{len(stable)} entries are stable")
warnings = mpdf[mpdf['warnings'].astype(bool)]
print(f"{len(warnings)} entries have warnings")
stable_icsd = mpdf[ (mpdf['icsd_ids'].astype(bool)) & (mpdf["e_above_hull"] <= 0) & (~mpdf['warnings'].astype(bool))]
print(f"{len(stable_icsd)} entries have ICSD ids, are stable, and have no warnings")



#%% ARE THE STRUCRURES VERY DIFFERENT IN OQMD, ICSD, MP?

have_many_icsd = have_icsd[have_icsd['icsd_ids'].apply(lambda l: len(l)>1)]
print(f"{len(have_many_icsd)}/{len(have_icsd)} have many ICSD ids")
ii = 2024
print(f"example {ii}: {have_many_icsd['pretty_formula'].iloc[ii]}")
print(have_many_icsd['cif'].iloc[ii])
for icsd_id in have_many_icsd['icsd_ids'].iloc[ii]:
    print("\n",icsd_id)
    print(icsdf['_chemical_formula_sum'].loc[icsdf['_database_code_ICSD']==str(icsd_id)])
    try:
        print(icsdf['cif'].loc[icsdf['_database_code_ICSD']==str(icsd_id)].iloc[0])
    except :
        pass
