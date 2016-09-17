Django Pivot-Tables
===================

This package provides utilities for turning Django Querysets into
`Pivot-Tables <https://en.wikipedia.org/wiki/Pivot_table>`.

Examples
--------

I am going to shamelessly lift examples from the wikipedia page referenced in the header.
Here is part of the table of shirt sales:

======  ======  ====== ========== ====== ====== ======
Region  Gender  Style  Ship Date   Units  Price  Cost
======  ======  ====== ========== ====== ====== ======
East    Boy     Tee     1/31/2005     12  11.04  10.42
East    Boy     Golf    1/31/2005     12     13   12.6
East    Boy     Fancy   1/31/2005     12  11.96  11.74
East    Girl    Tee     1/31/2005     10  11.27  10.56
East    Girl    Golf    1/31/2005     10  12.12  11.95
East    Girl    Fancy   1/31/2005     10  13.74  13.33
West    Boy     Tee     1/31/2005     11  11.44  10.94
West    Boy     Golf    1/31/2005     11  12.63  11.73
West    Boy     Fancy   1/31/2005     11  12.06  11.51
West    Girl    Tee     1/31/2005     15  13.42  13.29
West    Girl    Golf    1/31/2005     15  11.48  10.67
Etc.
======  ======  ====== ========== ====== ====== ======

We might want to know How many *Units* did we sell in each *Region* for every *Ship Date*?
And get a result like:

======== ========= ========= ========= ========= =========
Region   1/31/2005 2/1/2005  2/2/2005  2/3/2005  2/4/2005
======== ========= ========= ========= ========= =========
East            66        80       102        93       114
North           86        91        95        88       107
South           73        78        84        76        91
West            92       103       111       104       123
======== ========= ========= ========= ========= =========

It takes 3 quantities to pivot the original table into the summary result, two columns and
an aggregate of a third column. In this case the two columns are Region and Ship Date, the
third column is Units and the aggregate is Sum