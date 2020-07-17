#%%
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
PARENT = Path(__file__).parent.parent
AUGMENTED_PKL = str(HERE/"all_icsd_cifs_augmented.pkl")

icsd_df = pd.read_pickle(AUGMENTED_PKL)


#%%
print("example of a cif string:")
print(icsd_df['cif'].loc[0])
print()


#%%
def check_theory(cif_str):
    return "ABIN" in cif_str

contains_abin = icsd_df['cif'].loc[ icsd_df['cif'].apply(check_theory) ]
print(f"{len(contains_abin)} contains the string 'ABIN'")
