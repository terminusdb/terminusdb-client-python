Installation
============

Requirements
------------
* `TerminusDB <https://github.com/terminusdb/terminus-server>`_
  (you can `install using Docker <https://github.com/terminusdb/terminus-quickstart>`_)
* Python >= 3.6

Install using pip
-----------------

Install form PyPI:

``python -m pip install terminus-client-python``

this only include the core Python Client and WOQLQuery.

If you want to use woqlDataframe:

``python -m pip install terminus-client-python[dataframe]``

Install from source:

``python -m pip install git+https://github.com/terminusdb/terminus-client-python.git``
