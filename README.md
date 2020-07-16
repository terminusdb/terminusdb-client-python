TerminusDB Client Python
==========================

[![build status](https://api.travis-ci.com/terminusdb/terminusdb-client-python.svg?branch=master)](https://travis-ci.com/terminusdb/terminusdb-client-python)
[![Documentation Status](https://readthedocs.org/projects/terminusdb-client/badge/?version=latest)](https://terminusdb-client.readthedocs.io/en/latest/?badge=latest)

Python version of the TerminusDB client - for TerminusDB API and WOQLpy

## Requirements
- [TerminusDB 2.0](https://github.com/terminusdb/terminusdb-server)
- [Python >= 3.6]

## Installation
-  TerminusDB Client can be download form PyPI using pip:
`python -m pip install terminusdb-client`

this only include the core Python Client (WOQLClient) and WOQLQuery.

If you want to use woqlDataframe:

`python -m pip install terminusdb-client[dataframe]`

*if you are installing form `zsh` you have to quote the argument like this:*

`python -m pip install 'terminusdb-client[dataframe]'`

- Install from source:

`python -m pip install git+https://github.com/terminusdb/terminusdb-client-python.git`

## Usage
For the [full Documentation](https://terminusdb.github.io/terminusdb-client-python/)

## Tutorials
Visit [terminus-tutorials](https://github.com/terminusdb/terminusdb-tutorials) for tutorial scripts and [Create TerminusDB Graph with Python Client](https://terminusdb.com/docs/getting-started/start-tutorials/py_client/) for a python-specific one.

## Testing
* Clone this repository
`git clone https://github.com/terminusdb/terminusdb-client-python.git`

* Install all development dependencies
```sh
$ make init
```

* To run test files only
```sh
$ pytest terminusdb_client/tests
```

* To run full test
```sh
$ tox
```

## Report Issues

If you have encounter any issues, please report it with your os and environment setup, version that you are using and a simple reproducible case.

If you encounter other questions, you can ask in our community [forum](https://community.terminusdb.com/) or [Discord](https://discord.gg/Gvdqw97).

## Contribute

It will be nice, if you open an issue first so that we can know what is going on, then, fork this repo and push in your ideas. Do not forget to add a bit of test(s) of what value you adding.

Please check [Contributing.md](Contributing.md) for more information.

## Licence

Apache License (Version 2.0)

Copyright (c) 2019
