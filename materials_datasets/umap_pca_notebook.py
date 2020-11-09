#%% IMPORTING THE FULL DATAFRAME
from pathlib import Path  ## for os-agnostic paths

import pandas as pd  ## provides a fast spreadsheet object (DataFrame)
import matplotlib.pyplot as plt  ## standard python plotting tool
import seaborn as sns

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


#%% USING UMAP
from sklearn.preprocessing import StandardScaler
import umap
import matplotlib.pyplot as plt

umap_mpdf = mpdf[[
    "band_gap",
    "density",
    "e_above_hull",
    # "efermi",
    # "encut",
    # "energy",
    "energy_per_atom",
    # "final_energy",
    # "final_energy_per_atom",
    "formation_energy_per_atom",
    # "nkpts",
    # "nsites",
    "total_magnetization",
    "volume",
    # "exchange_symmetry",
    # "num_unique_magnetic_sites",
    # "total_magnetization_normalized_vol",
    # "total_magnetization_normalized_formula_units",
    # "num_magnetic_sites",
    # "true_total_magnetization",
]].dropna()

## This line requires a reduced dataset
# sns.pairplot(umap_mpdf, hue='total_magnetization')
reducer = umap.UMAP(n_components=3)
umap_data = umap_mpdf[[
    "band_gap",
    "density",
    "e_above_hull",
    "energy_per_atom",
    # "total_magnetization",
    "volume",
]].values
scaled_data = StandardScaler().fit_transform(umap_data)
embedding = reducer.fit_transform(scaled_data)
embedding.shape


#%%
plt.scatter(
    embedding[:, 0],
    embedding[:, 1],
    s=0.8,
    c=-umap_mpdf.total_magnetization
)
plt.gca().set_aspect('equal', 'datalim')
plt.title('UMAP projection', fontsize=24)


#%% USING PCA
from sklearn import decomposition

pca = decomposition.PCA(n_components=3)
pca.fit(scaled_data)
pca_embedding = pca.transform(scaled_data)

#%%
plt.scatter(
    pca_embedding[:, 1],
    pca_embedding[:, 2],
    s=0.8,
    c=-umap_mpdf.total_magnetization
)
plt.gca().set_aspect('equal', 'datalim')
plt.title('PCA projection', fontsize=24)

