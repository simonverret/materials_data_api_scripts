# Materials Data API Scripts

This repository contains scripts to download the data from:
- ICSD (requires credentials)
- Materials project (with pymatgen)
- OQMD (in progress)

The end goal of this project is to rely solely on python official modules.

## Requirements
install the requirements manually:

    pip install pandas
    pip install pymatgen  # for materials project only 

## Usage
### ICSD
Put your credentials in `icsd/icsd_credentials.json` and then

    python icsd/download.py

This will download only the 5398 cif strings that materials have 7 atoms in the unitcel




---
## Notes
### ICSD
##### Main API documentation:
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


#### OQMD
##### Main documentation:
- http://oqmd.org/static/docs/getting_started.html#setting-up-the-database provides a way to access materials: `qmpy-rester` but it is in python 2. Yet, reading `qmpy`'s source code will help make the full download script (similar as ICSD)

### More databases?
#### MDF: https://materialsdatafacility.org
#### MPDS: https://mpds.io/#start