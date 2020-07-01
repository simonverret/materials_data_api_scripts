#%%

import numpy as np
import pandas as pd
from ase import data
from pymatgen import Element
from mendeleev import get_table
import warnings


from learn_materials import utils

from pathlib import Path  ## for os-agnostic paths
HERE = Path(__file__).parent
DESC_PATH = HERE /"descriptors"

class PeriodicTable(pd.DataFrame):
    # subclassing pandas requires to declare attributes rather than panda columns
    _metadata = ['alt_names','max_atomic_number','descriptor_units', 'max_Z']

    def __init__(self, max_Z=103):
        ptable = get_table("elements").iloc[0:max_Z]
        symbols = ptable["symbol"]
        ptable["ionization_energy"]   = pd.DataFrame(list(get_mend_energies(max_Z)))
        ptable["atomic_radius"]       = get_mg_atomic_radius(symbols, max_Z)
        ptable["electronegativity"]   = get_mg_electronegativity(symbols, max_Z)
        ptable["magnetic_moment"]     = data.ground_state_magnetic_moments[1:]
        ptable["valence_number"]      = desc_file("wiki/valence.csv")
        ptable["covalent_radius"]     = desc_file("imat/atomic_radius.csv")
        ptable["cohesive_energy"]     = desc_file("imat/cohesive_energy.csv")
        ptable["imat_valence"]        = desc_file("imat/valence.csv")
        ptable["binding_energy"]      = desc_file("imat/electron_binding_energy.csv")
        ptable["electron_affinity"]   = desc_file("imat/electron_affinity.csv")
        ptable["magp_atomic_volume"]  = desc_file("magpie/atomic_volume.csv")
        ptable["magp_covalent_radius"]= desc_file("magpie/covalent_radius.csv")
        ptable["magp_boiling_point"]  = desc_file("magpie/T_boil.csv")
        ptable["magp_melting_point"]  = desc_file("magpie/T_melt.csv")
        ptable["magp_density"]        = desc_file("magpie/density.csv")
        ptable["polarizability"]      = desc_file("magpie/polarizability.csv")
        ptable["column"]              = desc_file("magpie/column.csv")
        ptable["row"]                 = desc_file("magpie/row.csv")
        ptable["unfilled_d"]          = desc_file("magpie/unfilled_d.csv")
        ptable["unfilled_f"]          = desc_file("magpie/unfilled_f.csv")
        ptable["unfilled"]            = desc_file("magpie/unfilled.csv")
        ptable["valence_d"]           = desc_file("magpie/valence_d.csv")
        ptable["valence_f"]           = desc_file("magpie/valence_f.csv")
        ptable["valence_p"]           = desc_file("magpie/valence_p.csv")
        ptable["valence_s"]           = desc_file("magpie/valence_s.csv")
        ptable["magp_valence"]        = desc_file("magpie/valence.csv")
        pd.DataFrame.__init__(self, ptable)

        self.max_Z = 103        
        self.alt_names = {
            # names used by Marc-Antoine Gagnon (2019 intern)
            "atomic number"            :"atomic_number",
            "atomic mass"              :"atomic_weight",
            "atomic magnetic moment"   :"magnetic_moment",
            "atomic electronegativity" :"electronegativity",
            "ionization energy"        :"ionization_energy",
            "atomic radius"            :"atomic_radius",
            "electron affinity"        :"electron_affinity",
            "covalent radius"          :"covalent_radius",
            "cohesive energy"          :"cohesive_energy",
            "electron binding energy"  :"binding_energy",
            "atomic valence number"    :"valence_number",
            "atomic valence radius"    :"imat_valence",
            # names used by Benjamin Gloro-Pare (2020 intern)
        }

        self.descriptor_units = {
            "atomic number"            : None,
            "number of atoms"          : None,
            "atomic mass"              : "u",
            "atomic magnetic moment"   : "Bohr magneton",
            "atomic electronegativity" : "eV",
            "ionization energy"        : "eV",
            "atomic radius"            : "Å",
            "electron affinity"        : "eV",
            "electronegativity"        : None,
            "covalent radius"          : "pm",
            "cohesive energy"          : "eV/atom",
            "is magnetic"              : None,
            # TODO: add the units of:
            "atomic valence number"    : None,
            "atomic valence radius"    : None,
            "electron binding energy"  : None,
            "magp_atomic_volume"       : None,
            "magp_covalent_radius"     : None,
            "magp_boiling_point"       : None,
            "magp_melting_point"       : None,
            "magp_density"             : None,
            "polarizability"           : None,
            "column"                   : None,
            "row"                      : None,
            "unfilled_d"               : None,
            "unfilled_f"               : None,
            "unfilled"                 : None,
            "valence_d"                : None,
            "valence_f"                : None,
            "valence_p"                : None,
            "valence_s"                : None,
            "magp_valence"             : None
        }

    def get_attribute(self, attribute, from_value, from_type="atomic_number"):
        if attribute in self.alt_names:
            attribute = self.alt_names[attribute]
        return self.loc[self[from_type] == from_value, attribute].iloc[0]


def desc_file(path, max_Z=103):
    base_list = list(np.loadtxt(DESC_PATH/path))[1:]
    prop = path.split("/")[-1].replace(".csv","")

    ## except for those three prop, 0 mean unknown and must be replaced by None.
    if not prop in ["valence", "electron_affinity", "electronegativity"]:
        base_list = [None if x==0 else x for x in base_list] 
    
    if max_Z > len(base_list):
        padding = [None for i in range(max_Z-len(base_list))]
        return base_list + padding
    elif max_Z < len(base_list):
        return base_list[:max_Z]
    else:
        return base_list


def get_mg_atomic_radius(elements, max_Z):
    """ Radius [Angstrom] taken from the pymatgen project. Correspond roughly
    (complete verification still needed) to Wikipedia 'empirical radius' 
    (Slater, 1964) data of the 'Atomic radii of the elements (data page)' page.
    Roughly equivalent to 'covalent_radius_slater' from mendelee [pm]
    """
    atomic_radi = []
    for element in elements[:max_Z]:
        atomic_radi.append(Element(element).atomic_radius)
    return atomic_radi


def get_mg_electronegativity(elements, max_Z):
    """ Pauling Electronegativity [dimensionless] from pymatgen. More complete
    data than mendeleev 'en_pauling' property. Correspond roughly (complete
    verification still needed) to Wikipedia's 'Electronegativities of the
    elements (data page)'
    """
    electronegativity = []
    for element in elements[:max_Z]:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            electronegativity.append(Element(element).X)
    return electronegativity


def get_mend_energies(max_Z):
    """ First ionization energy [kJ/mol] from the mendeleev project. Correspond
    roughly (complete verification still needed) to Wikipedia's 'Ionization
    energies of the elements (data_page)' column '1' from source 'CRC'.
    Slight deviations from McGill's IMAT projects values.
    """
    mendeleev_ion_energies = get_table("ionizationenergies")
    return mendeleev_ion_energies.loc[mendeleev_ion_energies["degree"] == 1][
        "energy"
    ].iloc[:max_Z]

PERIODICTABLE = PeriodicTable()

list(PERIODICTABLE['symbol'])