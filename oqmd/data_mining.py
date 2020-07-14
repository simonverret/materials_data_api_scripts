#%%
from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
OQMD_PKL = str(HERE / "oqmd.pkl")
OQMD_CSV = str(HERE / "oqmd.csv")

def fraction_composition(s):
    return not (("." in s) or ("(" in s))

if __name__ == "__main__":
    oqmd_df = pd.read_pickle(OQMD_PKL)
    oqmd_df_no_structure = oqmd_df.drop(columns=['_oqmd_unit_cell','_oqmd_sites'])
    oqmd_df.to_csv(OQMD_CSV) 
