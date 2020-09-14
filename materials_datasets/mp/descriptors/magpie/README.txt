These datafiles were gathered by intern Benjamin Gloro-Paré.
Most were taken from the Magpie project:
https://bitbucket.org/wolverton/magpie/src/master/lookup-data/


DIFFERENCES

Below are example of differences with the mendeleev module
Properties not listed were the same in mendeleev, in which case we use mendeleev
or they were absent from mendeleev, in which case we added them to PeriodicTable

Z       mendeleev       magpie     

atomic mass (we chose mendeleev)
70      173.0450        173.0540
84      209.0000        208.9824
85      210.0000        209.9872
86      222.0000        222.0176
87      223.0000        223.0197
88      226.0000        226.0254
89      227.0000        227.0277
93      237.0000        237.0482
94      244.0000        244.0642
95      243.0000        243.0614
96      247.0000        247.0703
97      247.0000        247.0703
98      251.0000        251.0796
99      252.0000        252.0830

atomic_volume
ALL_DIFFERENT (different temperature?) use 'magp_atomic_volume'

cohesive_energy (we chose mendeleev)
25        0.6700          2.9800

covalent_radius
ALL DIFFERENT (units?) use 'magp_covalent_radius'

density
ALL DIFFERENT (in addition to a factor 1000) use 'magp_density'

electron_affinity (we used mendeleev)
7         7.0000          0.0000

electronegativity (we used mendeleev)
36        3.0000          0.0000
86        2.2000          0.0000
87        0.7000          0.7900
88        0.9000          0.8900

T_boil
ALL DIFFERENT, both in Kelvin use 'magp_boiling_point'

T_melt
ALL DIFFERENT, both in Kelvin use 'magp_melting_point'

valence (we used wikipedia) use 'magp_valence'
Z      wikipedia          magpie
21        2.0000          3.0000
22        2.0000          4.0000
23        2.0000          5.0000
24        1.0000          6.0000
25        2.0000          7.0000
26        2.0000          8.0000
27        2.0000          9.0000
28        2.0000         10.0000
29        1.0000         11.0000
30        2.0000         12.0000
31        3.0000         13.0000
32        4.0000         14.0000
33        5.0000         15.0000
34        6.0000         16.0000
35        7.0000         17.0000
36        8.0000         18.0000
39        2.0000          3.0000
40        2.0000          4.0000
41        1.0000          5.0000
42        1.0000          6.0000
43        1.0000          7.0000
44        1.0000          8.0000
45        1.0000          9.0000
46        1.0000         10.0000
47        1.0000         11.0000
48        2.0000         12.0000
49        3.0000         13.0000
50        4.0000         14.0000
51        5.0000         15.0000
52        6.0000         16.0000
53        7.0000         17.0000
54        8.0000         18.0000
57        2.0000          3.0000
58        2.0000          4.0000
59        2.0000          5.0000
60        2.0000          6.0000
61        2.0000          7.0000
62        2.0000          8.0000
63        2.0000          9.0000
64        2.0000         10.0000
65        2.0000         11.0000
66        2.0000         12.0000
67        2.0000         13.0000
68        2.0000         14.0000
69        2.0000         15.0000
70        2.0000         16.0000
71        2.0000         17.0000
72        2.0000         18.0000
73        2.0000         19.0000
74        2.0000         20.0000
75        2.0000         21.0000
76        2.0000         22.0000
77        2.0000         23.0000
78        1.0000         24.0000
79        1.0000         25.0000
80        2.0000         26.0000
81        3.0000         27.0000
82        4.0000         28.0000
83        5.0000         29.0000
84        6.0000         30.0000
85        7.0000         31.0000
86        8.0000         32.0000
89        2.0000          3.0000
90        2.0000          4.0000
91        2.0000          5.0000
92        2.0000          6.0000
93        2.0000          7.0000
94        2.0000          8.0000
95        2.0000          9.0000
96        2.0000         10.0000
97        2.0000         11.0000
98        2.0000         12.0000
99        2.0000         13.0000
