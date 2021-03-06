Atmodel
=======
[*UCSB Experimental Cosmology Group*](http://deepspace.ucsb.edu)

This program is intended to facilitate the analysis of signal and noise data
obtained of various sources from various sites.

Dependencies
------------

* python (=2.7)
* PyQt4 (>= 4.9)
* matplotlib (>= 1.1)
* numpy (>= 1.6)
* scipy (>= 0.10)
* sqlite3 (>= 2.6)
* xlrd (>= 0.9)
* xlsxwriter (>= 0.5)
* xlwt (>= 0.7)

With the exception of the version number of Python itself, the numbers listed
above indicate the version number of the Python package which may differ from
that of the original package if the Python package is merely a binding.

Note that it may be possible to run this program with older versions of the
listed packages. However, such usage has not been tested.

Running the Program
-------------------

Atmodel's entry point is in main.py. To run the program, run "python main.py"
from a terminal. This should open a window with options, on the left, to add to
a graph that will appear on the right when the "Generate Graph" button is
clicked.
