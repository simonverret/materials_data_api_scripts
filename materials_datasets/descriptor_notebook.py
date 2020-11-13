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

print("\n\nSUBSET:")
subset_ids = pd.read_csv(SUBSET_MPIDS_CSV, names=["material_id"])
print(len(subset_ids), "material_ids")
subset_mpdf = mpdf[mpdf["material_id"].isin(subset_ids["material_id"])]


#%% CONTENT OF THE PERIODIC TABLE
for col in ptable.columns: 
    print(col)

for col in subset_mpdf.columns: 
    print(col)


#%% PARSING FORMULA TO DICT
import collections
import re

def get_symbol_dict(f, factor):
    symbol_dict = collections.defaultdict(float)
    for regex in re.finditer(r"([A-Z][a-z]*)\s*([-*\.e\d]*)", f):
        element = regex.group(1)
        amount = 1
        if regex.group(2).strip() != "":
            amount = float(regex.group(2))
        symbol_dict[element] += amount * factor
        f = f.replace(regex.group(), "", 1)
    if f.strip():
        raise ValueError("{} is an invalid formula!".format(f))
    return symbol_dict


def parse_formula_recursive(formula):
    formula = formula.replace("@", "")  # for Metallofullerene like "Y3N@C80"
    regex = re.search(r"\(([^\(\)]+)\)\s*([\.e\d]*)", formula)
    if regex:
        factor = 1
        if regex.group(2) != "":
            factor = float(regex.group(2))
        unit_symbol_dict = get_symbol_dict(regex.group(1), factor)
        expanded_symbol = "".join([
            f"{element}{amount}" for element, amount in unit_symbol_dict.items()
        ])
        expanded_formula = formula.replace(regex.group(), expanded_symbol)
        return parse_formula_recursive(expanded_formula)
    return get_symbol_dict(formula, 1)


def parse_formula(formula):
    return dict(parse_formula_recursive(formula))


#%% SET USED BY BENJAMIN
subset_stable = subset_mpdf.loc[mpdf['e_above_hull'] <= 0.1]

#%% EXAMPLE OF CONTENT
print("number of materials: ", len(subset_stable))
print("example:")
iii = 12345
formula = subset_stable.full_formula[iii]
print(formula)
print(parse_formula(formula))
print(subset_stable.total_magnetization[iii])
print(subset_stable.true_total_magnetization[iii])
print(subset_stable.nsites[iii])
subset_stable['magnetization_per_atom'] = subset_stable['true_total_magnetization']/subset_stable['nsites']
print(subset_stable.magnetization_per_atom[iii])


#%% COMPUTING DESCRIPTORS
import numpy as np

def prop_array(formula, prop):
    prop_arr = np.array([])
    for symbol, amount in parse_formula(formula).items(): 
        prop_val = ptable[prop].loc[symbol]
        prop_arr = np.append(prop_arr, prop_val*np.ones(int(amount)))
    return prop_arr

tree_df = pd.DataFrame()

# pred: maximum at. mass, importance from Benjamin's work: 0.1350313244529027
print("preparing max_magp_atomic...")
tree_df['max_magp_atomic_masses'] = subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_atomic_masses").max()
)
# pred: maximum at. electronegativity, importance from Benjamin's work: 0.044222686590578875
print("preparing max_magp_electr...")
tree_df['max_magp_electronegativity'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_electronegativity").max()
)
# pred: maximum at. unfilled number, importance from Benjamin's work: 0.1730765689253583
print("preparing max_magp_unfill...")
tree_df['max_magp_unfilled'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_unfilled").max()
)
# pred: maximum at. melting T, importance from Benjamin's work: 0.10773341701423939
print("preparing max_magp_T_melt...")
tree_df['max_magp_T_melt'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_T_melt").max()
)
# pred: maximum at. volume mendel, importance from Benjamin's work: 0.15884535333941543
print("preparing max_magp_atomic...")
tree_df['max_magp_atomic_volume'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_atomic_volume").max()
)
# pred: minimum at. d+f unfilled, importance from Benjamin's work: 0.00934994750435063
print("preparing min_magp_unfill...")
tree_df['min_magp_unfilled_d+f'] =  subset_stable.full_formula.apply(
    lambda s: (prop_array(s, "magp_unfilled_f") + prop_array(s, "magp_unfilled_d")).max()
)
# pred: minimum d shell valence, importance from Benjamin's work: 0.010249704771850143
print("preparing max_magp_valenc...")
tree_df['max_magp_valence_d'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_valence_d").min()
)
# pred: minimum at. volume, importance from Benjamin's work: 0.10943445265870913
print("preparing min_magp_atomic...")
tree_df['min_magp_atomic_volume'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_unfilled").min()
)
# pred: mean f shell valence, importance from Benjamin's work: 0.16113896790177093
print("preparing mean_magp_valen...")
tree_df['mean_magp_valence_f'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "magp_valence_f").mean()
)
# pred: mean at. valence wiki, importance from Benjamin's work: 0.09091757684082442
print("preparing mean_wiki_valen...")
tree_df['mean_wiki_valence'] =  subset_stable.full_formula.apply(
    lambda s: prop_array(s, "wiki_valence").mean()
)


#%%
tree_df['magnetization_per_atom'] = subset_stable['true_total_magnetization']/subset_stable['nsites']

#%%
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

features = tree_df.dropna()

labels = np.array(features['magnetization_per_atom'])
features= features.drop('magnetization_per_atom', axis = 1)
feature_list = list(features.columns)
features = np.array(features)

train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)

print(f"Training Random Forest")
rf = RandomForestRegressor(
    n_estimators=300,
    criterion="mse",
    max_depth=None,
    min_samples_split=6,
    max_features=4,
    bootstrap=False,
    min_samples_leaf=2
    # random_state = 42
)
rf.fit(train_features, train_labels)

print(f"Evaluating")
predictions = rf.predict(test_features)
print(f"MAE: {np.mean(abs(predictions - test_labels)):6.5f}")
print(f"MSE: {np.mean((predictions - test_labels)**2):6.5f}")


#%% UMAP
from sklearn.preprocessing import StandardScaler
import umap
import matplotlib.pyplot as plt

reducer = umap.UMAP(n_components=3)
umap_data = tree_df.drop(['magnetization_per_atom'], axis=1).dropna().values
umap_label = tree_df.dropna().magnetization_per_atom
scaled_data = StandardScaler().fit_transform(umap_data)
embedding = reducer.fit_transform(scaled_data)
print(embedding.shape)

plt.scatter(
    embedding[:, 0],
    embedding[:, 1],
    s=0.8,
    c=-umap_label
)
plt.gca().set_aspect('equal', 'datalim')
plt.title('UMAP projection', fontsize=24)

# plt.savefig('umap.pdf')

