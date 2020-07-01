#%%
import cProfile
import numpy as np
import pandas as pd  ## provides a fast spreadsheet object (DataFrame)
from pathlib import Path  ## for os-agnostic paths
from pymatgen import Structure, PeriodicSite
import pymatgen.analysis.local_env as env
from chemistry import PERIODICTABLE


HERE = Path(__file__).parent
DATAFILE = str(HERE/"materials_project_full_dataframe.pkl")
mpdf = pd.read_pickle(DATAFILE)
print(f"loaded {len(mpdf)} materials")


#%%


def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


#%%
ii = 48456
print(mpdf['pretty_formula'][ii])
cif = mpdf['cif'][ii]
material_structure = Structure.from_str(cif, 'cif')

print(f"number of sites {mpdf['nsites'][ii]}")

print(cif)

# cProfile.run("graph_from_str(cif, 'voronoi', 6, bond_angles=True)")

def atomic_number_from_site(site):
    return PERIODICTABLE.get_attribute(
        "atomic_number",
        site.specie.as_dict()["element"],
        "symbol"
    )

#%%

sites = map(atomic_number_from_site, material_structure)
print(list(sites))

#%%
if strategy == "voronoi":
    neighbor_strategy = env.VoronoiNN()
elif strategy == "all":
    neighbor_strategy = env.MinimumDistanceNN(cutoff=cutoff, get_all_sites=True)

try:
    sites_neighbors = neighbor_strategy.get_all_nn_info(material_structure)
except ValueError:
    # FIXME: this is not very specific
    print("Graph for this material could not be computed")
    return (None,) * 7 if bond_angles else (None,) * 4
except RuntimeError:
    print("Pathological structure, graph for this material could not be computed")
    return (None,) * 7 if bond_angles else (None,) * 4

neighbors_coords = []
bonds = []
sites1 = []
sites2 = []
for i, site in enumerate(sites_neighbors):
    neighbors_coords.append([])
    for neighbor in site:
        neighbors_coords[i].append(neighbor["site"].coords)
        bonds.append(
            super(PeriodicSite, material_structure[i]).distance(neighbor["site"]),
        )
        sites1.append(i)
        sites2.append(neighbor["site_index"])

if bond_angles:
    angles = []
    bonds1 = []
    bonds2 = []
    start_index = 0
    for i, sitei in enumerate(neighbors_coords):
        sitei_coords = material_structure[i].coords
        for j, sitej in enumerate(sitei):
            bondindex1 = start_index + j
            ij_vector = sitei_coords - sitej
            for k, sitek in enumerate(sitei):
                bondindex2 = start_index + k
                if j != k:
                    ik_vector = sitei_coords - sitek
                    angles.append(angle_between(ij_vector, ik_vector),)
                    bonds1.append(bondindex1)
                    bonds2.append(bondindex2)
        start_index += len(sitei)
        
    return sites, bonds, sites1, sites2, angles, bonds1, bonds2
return sites, bonds, sites1, sites2