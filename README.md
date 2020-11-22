# Materials Data API Scripts

This repository contains scripts to download and analyse the data from:
- Materials project
- OQMD
- ICSD

## Requirements

    pip install requests
    pip install numpy
    pip install pandas
    pip install pymatgen  # required for MP only
    pip install asyncio  # required for OQMD only
    pip install concurrent  # required for OQMD only

## Usage
### MP
Create a file `mp/api_key.json` containing your API key as

    {
        "api_key": "********************"
    }
and download all of MP materials data with

    python mp/download.py

which will save a `pandas.DataFrame` object in the file `mp/materials_project.pkl`. This format is used because it enables faster loading, saving and manipulations than `csv` of `json` format. For example of how to use this file, see the `mp.ipynb` Jupyter notebook.

### ICSD
Create a file `icsd/icsd_credentials.json` containing your ICSD credentials as

    {
        "loginid":"*********",
        "password":"*****************"
    }

and download all ICSD `cif` strings with

    python icsd/download.py

which will save the strings in a `pandas.DataFrame` object in the file `icsd/icsd_cifs.pkl`. This format is used to enable faster loading, saving and manipulations than `csv` of `json` format. You can then extract information from the `cif` strings with

    python icsd/augment.py

which will extract:

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

and save a new `pandas.DataFrame` object saved in `icsd/all_icsd_cifs_augmented.pkl` (keeping the `cif` strings column). For example of how to use this file, see the `icsd.ipynb` notebook.

The extracted data is also saved in `.csv` files `icsd/icsd_formulas_all.csv` without the `cif` string data, along with two additional files `icsd_formula_structural_integer.csv` and `icsd_formula_sum_integer.csv`, which contain only the compounds with stochiometric formulae. 


### OQMD

Download all of OQMD materials (can take up to a few days) with

    python mp/download.py

which will save a `pandas.DataFrame` object in the file `oqmd/oqmd.pkl`. This format is used to enable faster loading, saving and manipulations than `csv` of `json` format. For example of how to use the resulting file, see the `oqmd.ipynb` notebook.


---
## Notes
##### Main ICSD API documentation:
- https://icsd.fiz-karlsruhe.de/api/
##### ressources for REST:
- https://www.smashingmagazine.com/2018/01/understanding-using-rest-api/
- then get lost and ask yourself how http works: https://medium.com/better-programming/writing-your-own-http-server-introduction-b2f94581268b
- curl to python code: https://curl.trillworks.com
##### other ressources:
- data scraping: https://github.com/hegdevinayi/icsd-queryer
- cambridge cristallographic data center: https://www.ccdc.cam.ac.uk/support-and-resources/support/case/?caseid=c344eefa-6b74-e811-91fa-005056975d8a
- AIIDA database importer: https://aiida-core.readthedocs.io/en/stable/import_export/dbimporters/icsd.html. This one is interesting, but it requires an intranet version of the database.
- re3data.org : https://www.re3data.org/repository/r3d100010085
- matminer retreiver for MDF, MPDS, OQMD and MongoDB : https://hackingmaterials.lbl.gov/matminer/matminer.data_retrieval.html#

##### Main OQMD documentation:
- http://oqmd.org/static/docs/getting_started.html#setting-up-the-database provides a way to access materials: `qmpy-rester` but it is in python 2. Yet, reading `qmpy`'s source code will help make the full download script (similar as ICSD)

##### More databases which could be added:
- MDF: https://materialsdatafacility.org
- MPDS: https://mpds.io/#start