#!/usr/bin/env python3

import pandas as pd
from pathlib import Path  ## for os-agnostic paths

HERE = Path(__file__).parent
CITRINE_MP_JSON = str(HERE/"citrine_MP_ICSD_compounds_PIFs.json")
CITRINE_MP_PKL = str(HERE/"citrine_mp.pkl")

def unfold_ids(ids_list):
    return pd.Series({id_dict['name']:id_dict['value'] for id_dict in ids_list})

def unfold_properties(prop_list):
    return pd.Series({prop['name']:prop['scalars'] for prop in prop_list})

def main():
    print("reading PIF file")
    citrine_mp_df = pd.read_json(CITRINE_MP_JSON)
    print("unfolding ids")
    citrine_mp_df = citrine_mp_df.merge(
        citrine_mp_df["ids"].apply(unfold_ids),
        left_index=True,
        right_index=True
    )

    print("unfolding properties")
    citrine_mp_df = citrine_mp_df.merge(
        citrine_mp_df["properties"].apply(unfold_properties),
        left_index=True,
        right_index=True
    )
    print("saving")
    citrine_mp_df.pop("ids")
    citrine_mp_df.pop("properties")
    citrine_mp_df.pop("tags")
    citrine_mp_df.pop("references")
    citrine_mp_df.to_pickle(CITRINE_MP_PKL)
    print("done")

if __name__ == "__main__":
    main()
