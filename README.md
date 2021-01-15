# Materials Data API Scripts

This repository contains python scripts and Jupyter notebooks to download and analyse the data from:
- Materials project (MP)
- Open quantum materials database (OQMD)
- Inorganic crystal structure database (ICSD)

A periodic table combining data from `mendeleev`, `ase`, `pymatgen` and other custom descriptors is provided.

#### Content of this Readme
- [Requirements](#requirements)  
- [Materials Project (MP)](#materials-project-mp)
- [Inorganic crystal structure database (ICSD)](#inorganic-crystal-structure-database-icsd)  
- [Open quantum materials database (OQMD)](#open-quantum-materials-database-oqmd)
- [Periodic table](#periodic-table)
- [References](#references)  

## Requirements

The download scripts require

    pip install requests
    pip install pandas
    pip install jupyter
    pip install pymatgen

The notebooks require

    pip install seaborn
    pip install sklearn
    pip install umap-learn
    pip install mendeleev
    pip install ase

Note that the same version of Pandas must be used to save and load the `.pkl` [binary files](https://docs.python.org/3/library/pickle.html), otherwise you will get errors.

## Materials Project (MP)
Add your your API key by creating a file `mp/api_key.json` as

    echo '{"api_key":"******************"}' > mp/api_key.json

Download all MP data with

    python mp/download.py

A `pandas.DataFrame` object will be saved as `mp/materials_project.pkl`.

See the `example_mp.ipynb` and `example_pca.ipynb` Jupyter notebooks for usage examples.


## Inorganic crystal structure database (ICSD)
Your ICSD credentials by creating a file `icsd/icsd_credentials.json` as

    echo '{"loginid":"**********","password":"****************"}' > icsd/icsd_credentials.json

Download all ICSD `cif` strings with

    python icsd/download.py

A `pandas.DataFrame` object will be saved in binary format in the file `icsd/icsd_cifs.pkl`. Extract information from the `cif` strings it contains with

    python icsd/augment.py

which will extract new columns :

- id
- _database_code_ICSD
- _chemical_formula_structural
- _chemical_formula_sum
- _cell_length_a
- _cell_length_b
- _cell_length_c
- _cell_angle_alpha
- _cell_angle_beta
- _cell_angle_gamma
- _cell_volume

in a new `pandas.DataFrame` saved in `icsd/all_icsd_cifs_augmented.pkl` file. The data is also saved in a `.csv` files `icsd/icsd_formulas_all.csv`, but without the `cif` column. Two additional files are also saved, `icsd_formula_structural_integer.csv` and `icsd_formula_sum_integer.csv` which contain stochiometric compounds only.

See the `example_icsd.ipynb` Jupyter notebooks for usage examples (along with `example_mp_vs_icsd.ipynb` if you have MP downloaded).


## Open quantum materials database (OQMD)

Download all of OQMD materials (can take up to a few days) with

    python oqmd/download.py

A `pandas.DataFrame` object will be saved in binary format in the file `oqmd/oqmd.pkl`.


## Periodic table

Build the periodic table with

    python ptable/build.py

A `pandas.DataFrame` object will be saved in binary format in the file `ptable/ptable.pkl`.

See the `example_descriptors.ipynb` Jupyter notebook for usage examples.

---
## References
##### Main MP documentation
- https://materialsproject.org/open describes the various ways to acces the data. The present code used the pymatgen wrapper.
##### Main OQMD documentation:
- http://oqmd.org/static/docs/getting_started.html#setting-up-the-database provides a way to access materials: `qmpy-rester` but it is in `python 2.7`. Reading `qmpy`'s source code helped make the full download script with the `requests` python package to access web ressources.
##### Main ICSD API documentation:
- https://icsd.fiz-karlsruhe.de/api/ is more of an GUI to the API. You can experiment with it and find what is accessible. The HTML queries can then be [translated](https://curl.trillworks.com) from `curl` to python package to access web ressources.
##### Resources for REST:
- https://www.smashingmagazine.com/2018/01/understanding-using-rest-api/
- then get lost and ask yourself how http works: https://medium.com/better-programming/writing-your-own-http-server-introduction-b2f94581268b
- Useful curl to python translation: https://curl.trillworks.com
##### Unsued resources (kept here for reference):
- data scraping: https://github.com/hegdevinayi/icsd-queryer
- cambridge cristallographic data center: https://www.ccdc.cam.ac.uk/support-and-resources/support/case/?caseid=c344eefa-6b74-e811-91fa-005056975d8a
- AIIDA database importer: https://aiida-core.readthedocs.io/en/stable/import_export/dbimporters/icsd.html. This one is interesting, but it requires an intranet version of the database.
- re3data.org : https://www.re3data.org/repository/r3d100010085
- matminer retreiver for MDF, MPDS, OQMD and MongoDB : https://hackingmaterials.lbl.gov/matminer/matminer.data_retrieval.html#
##### More databases which could be added to this repository
- MDF: https://materialsdatafacility.org
- MPDS: https://mpds.io/#start
