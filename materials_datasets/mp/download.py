#!/usr/bin/env python3

from pymatgen.ext.matproj import MPRester  ## to access MP database
import pandas as pd  ## provides a fast spreadsheet object (DataFrame)
from pathlib import Path  ## for os-agnostic paths
from copy import deepcopy
import numpy as np
import json


HERE = Path(__file__).parent
MATERIALS_PROJECT_PKL = str(HERE/"materials_project.pkl")
API_KEY_JSON = str(HERE/"api_key.json")


# available properties and description are hard to find, see:
# https://github.com/materialsproject/mapidoc/tree/master/materials
# https://materialsproject.org/docs/api
# For some reason `print(MPRester.supported_properties)` and
# `print(MPRester.supported_task_properties)` are incomplete. Below is a list of
# everything found so far. the commented properties caused problem when exporting
# to parquet so we excludeed them (gain in speed). If you choose to restore them
# you might need to change the chunk_size value.
ALL_KNOWN_PROPERTIES = [
    "material_id",  # str
    "anonymous_formula",  # dict
    "band_gap",  # float  # The calculated band gap
    "band_structure",  # The calculated "line mode" band structure (along selected symmetry lines -- aka "branches", e.g. \Gamma to Z -- in the Brillouin zone) in the pymatgen json representation
    "bandstructure_uniform",  # The calculated uniform band structure in the pymatgen json representation
    "blessed_tasks",  # dict
    "bond_valence",
    "chemsys",  # str
    "cif",  # str  # A string containing the structure in the CIF format.
    # "cifs",  # dict
    "created_at",  # str
    "delta_volume",
    "density",  # float  # Final relaxed density of the material
    "diel",  # Dielectric properties. Contains a tensor (one each for total and electronic contribution) and derived properties, e.g. dielectric constant, refractive index, and recognized potential for ferroelectricity.
    "doi",
    "doi_bibtex",
    "dos",  # The calculated density of states in the pymatgen json representation
    "e_above_hull",  # int  # Calculated energy above convex hull for structure. Please see Phase Diagram Manual for the interpretation of this quantity.
    "efermi",  # float
    "elasticity",  # Mechanical properties in the elastic limit. Contains the full elastic tensor as well as derived properties, e.g. Poisson ratio and bulk (K) and shear (G) moduli. Consult our hierarchical documentation for the particular names of sub-keys.
    # "elasticity_third_order",
    "elements",  # list  # A array of the elements in the material
    "encut",  # int
    "energy",  # float  # Calculated vasp energy for structure
    "energy_per_atom",  # float  # Calculated vasp energy normalized to per atom in the unit cell
    "entry",  # This is a special property that returns a pymatgen ComputedEntry in the json representation. ComputedEntries are the basic unit for many structural and thermodynamic analyses in the pymatgen code base.
    "exp",  # dict
    "final_energy",  # float
    "final_energy_per_atom",  # float
    "formation_energy_per_atom",  # float  # Calculated formation energy from the elements normalized to per atom in the unit cell
    "formula_anonymous",  # str
    "full_formula",  # str
    "has",  # list
    "has_bandstructure",  # bool
    # "hubbards",  # dict  # An array of Hubbard U values, where applicable.
    "icsd_ids",  # list  # List of Inorganic Crystal Structure Database (ICSD) ids for structures that have been deemed to be structurally similar to this material based on pymatgen's StructureMatcher algorithm, if any.
    # "initial_structure",  # pymatgen.core.structure.Structure  # The initial input structure for the calculation in the pymatgen json representation (see later section).
    # "input",  # dict
    "is_compatible",  # bool  # Whether this calculation is considered compatible under the GGA/GGA+U mixing scheme.
    "is_hubbard",  # bool  # A boolean indicating whether the structure was calculated using the Hubbard U extension to DFT
    "is_ordered",  # bool
    "last_updated",  # str
    "magnetic_type",  # str
    "magnetism",  # dict
    "nelements",  # int  # The number of elements in the material
    "nkpts",
    "nsites",  # int  # Number of sites in the unit cell
    "ntask_ids",  # int
    "original_task_id",  # str
    "oxide_type",  # str
    "pf_ids",  # list
    # "piezo",  # Piezoelectric properties. Contains a tensor and derived properties. Again, consult our repository for the names of sub-keys.
    "pretty_formula",  # A nice formula where the element amounts are normalized
    "pseudo_potential",  # dict
    "reduced_cell_formula",  # dict
    "run_type",  # str
    # "snl",  ## causes ModuleNotFoundError: No module named 'pybtex'
    # "snl_final",  ## causes ModuleNotFoundError: No module named 'pybtex'
    "spacegroup",  # dict  # An associative array containing basic space group information.
    # "structure",  # pymatgen.core.structure.Structure  # An alias for final_structure. # The final relaxed structure in the pymatgen json representation (see later section).
    "task_id",  # str
    "task_ids",  # list
    "total_magnetization",  # float  # total magnetic moment of the unit cell
    "unit_cell_formula",  # dict  # The full explicit formula for the unit cell
    "volume",  # float  # Final relaxed volume of the material
    "warnings",  # list
    # "xrd",  # dict
]


def download_all_materials_project(
    apikey, 
    min_nelements=1, 
    max_nelements=10, 
    max_nsites=500, 
    nsites_step=500,
    chunk_size=5000,
    properties=ALL_KNOWN_PROPERTIES,
):
    """ Download all data from the materials project and returns a list of
    dictionnary.
    
    Only 124 331 out of 124 515 materials claimed on the website are obtainable.
    the database is downloaded by a sequence of queries, each one is for a given
    number of elements in the materials and then number of sites. Queries are
    broken into chunks to prevent exceeding the limit size allowed.

    Parameters:
    - max_nelements: the maximum value of nelements used in query loop
    - max_nsites: the maximum value of nsites used for each nvalues
    - nsites_step: number of different value taken by nsites in each queries
    - chunk_size: size to break queries
    - properties: the properties to be downloaded (affect the size of queries)
    some properties are dictionnary themselves and may require to be unrolled
    (magnetism as an example in the source file of this function)

    """
    rester = MPRester(apikey)
    list_of_dict = []
    print("downloading items (multiple queries required)")
    for nelements in range(min_nelements, max_nelements+1):
        for nsites in range(1, max_nsites, nsites_step+1):
            query = rester.query(
                criteria= {
                    "nelements": nelements, 
                    "nsites": {
                        "$gt": nsites,
                        "$lt": nsites+nsites_step+1, 
                    }
                },
                properties=properties,
                chunk_size=chunk_size,
            )
            list_of_dict.extend(query)
    return list_of_dict


def unfold_magnetism(mp_list):
    mp_list = deepcopy(mp_list)
    new_list = []
    print("unfolding magnetism")
    for mat in mp_list:
        try:
            magnetism = mat.pop('magnetism')
            magnetism['num_magnetic_sites'] = int(magnetism.pop('num_magnetic_sites'))  # str to int
            magnetism['true_total_magnetization'] = magnetism.pop('total_magnetization')  # different from mp's "total magnetisation" which is the total magnetisation per formula
            mat.update(magnetism)
            new_list.append(mat)
        except KeyError:
            pass
    return mp_list


def main():
    with open(API_KEY_JSON, "r") as f:
        api_key = json.load(f)["api_key"]
    mp_list = download_all_materials_project(api_key)
    mp_list_w_mag = unfold_magnetism(mp_list)
    df = pd.DataFrame(mp_list_w_mag)
    try: df['efermi'] = df['efermi'].replace('None', np.nan )  # bug: string "None" instead of NoneType None
    except KeyError: pass
    print("saving")
    df.to_pickle(MATERIALS_PROJECT_PKL)
    print(f"{len(df)} materials saved")


if __name__ == "__main__":
    main()
