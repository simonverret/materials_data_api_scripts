#!/usr/bin/env python3

import warnings
import glob
from pathlib import Path  ## for os-agnostic paths

import pandas as pd
from mendeleev import get_table
from ase import data as ase_data
from pymatgen import Element


HERE = Path(__file__).parent


def gather_ptable_dataframe():
    df_list = []

    ## get properties in csv (retrieved from magpie project, imat project, and wikipedia) 
    all_files = glob.glob(str(HERE/"*"/"*.csv"))
    for filename in all_files:
        prop = str(Path(filename).stem)
        source = str(Path(filename).parent.stem)
        name = source + "_" + prop
        tmp_df = pd.read_csv(filename, names=[name])
        valid_0_list = [
            "valence",
            "valence_s",
            "valence_p",
            "valence_d",
            "valence_f",
            "unfilled",
            "unfilled_f",
            "unfilled_d",
            "electron_affinity",
            "electronegativity",
            "magnetic_moment",
        ]
            
        if not prop in valid_0_list:
            tmp_df = tmp_df[name].apply(lambda x: None if x==0 else x)
        df_list.append(tmp_df)

    ## get ase magnetic moments
    magmom_list = ase_data.ground_state_magnetic_moments
    tmp_df = pd.DataFrame(magmom_list, columns=["ase_magnetic_moment"])
    df_list.append(tmp_df)

    # concat in a single dataframe and drop the 0th entry (up to here, 
    # properties were savec with element 0 as dummy so the index corresponed 
    # to the atomic number)
    external_props = pd.concat(df_list, axis=1).drop(0)

    # concat with mendeleev's ptable (need reindexing with atomic number)
    ptable = get_table("elements")
    ptable = ptable.set_index('atomic_number', drop=False)
    ptable = pd.concat([ptable, external_props], axis=1)

    # add pymatgen properties
    ptable["pymg_atomic_radius"] = [Element(x).atomic_radius for x in ptable['symbol']]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ptable["pymg_electronegativity"] = [Element(x).X for x in ptable['symbol']]
    
    # add the first ionization energy from mendeleev
    tmp_df = get_table("ionizationenergies")
    ptable["ionization_energy"] = tmp_df.loc[tmp_df["degree"] == 1].set_index('atomic_number')['energy']
    
    # drop useless columns
    ptable = ptable.drop([
        'annotation',
        'description',
        'discoverers',
        'discovery_location',
        'geochemical_class',
        'goldschmidt_class',
        'uses',
        'sources',
        'name_origin',
    ],1)
    
    # reindex by symbol
    ptable = ptable.set_index('symbol')
    return ptable

def save_ptable():
    ptable = gather_ptable_dataframe()
    ptable.to_csv("ptable.csv")
    ptable.to_pickle("ptable.pkl")

if __name__ == "__main__":
    save_ptable()

