TerminusDB Client Python
==========================

[![build status](https://api.travis-ci.com/terminusdb/terminusdb-client-python.svg?branch=master)](https://travis-ci.com/terminusdb/terminusdb-client-python)
[![Documentation Status](https://readthedocs.org/projects/terminusdb-client/badge/?version=latest)](https://terminusdb-client.readthedocs.io/en/latest/?badge=latest)

Python version of the TerminusDB client - for TerminusDB API and WOQLpy

## Requirements
- [TerminusDB 2.0.5](https://github.com/terminusdb/terminusdb-server)
- Python >= 3.6

## Release Notes and Previous Versions

- Please check [RELEASE_NOTES.md](RELEASE_NOTES.md) to find out what has changed.

These previous version(s) works with these version(s) of TerminusDB:

- 0.1.5 - works with TerminusDB server / console v2.0.4

## Installation
-  TerminusDB Client can be downloaded form PyPI using pip:
`python -m pip install terminusdb-client`

This only includes the core Python Client (WOQLClient) and WOQLQuery.

If you want to use woqlDataframe:

`python -m pip install terminusdb-client[dataframe]`

*if you are installing form `zsh` you have to quote the argument like this:*

`python -m pip install 'terminusdb-client[dataframe]'`

- Install from source:

`python -m pip install git+https://github.com/terminusdb/terminusdb-client-python.git`

## Usage
Please check the [full Documentation](https://terminusdb.github.io/terminusdb-client-python/)

## Tutorials
Visit [terminus-tutorials](https://github.com/terminusdb/terminus-tutorials/tree/master/bike-tutorial/python) for tutorial scripts and [Create TerminusDB Graph with Python Client](https://terminusdb.com/docs/getting-started/start-tutorials/py_client/) for a python-specific one.

## Testing

1. Clone this repository
`git clone https://github.com/terminusdb/terminusdb-client-python.git`

2. Install all development dependencies
```sh
$ make init
```

3. (a) To run test files only
```sh
$ pytest terminusdb_client/tests
```

3. (b) To run full test
```sh
$ tox
```

## Documentation

Documentation on the latest version can be found [here](https://terminusdb.github.io/terminusdb-client-python/).

### Generating Documentation Locally

1. Clone this repository
`git clone https://github.com/terminusdb/terminusdb-client-python.git`

2. Install all development dependencies
```sh
$ make init
```

3. Change directory to docs
```sh
$ cd docs/
```

4. Build with Sphinx
```sh
$ make html
```

The output files are under `docs/build/html`, open `index.html` in your browser to inspect.

## Report Issues

If you encounter any issues, please report them with your os and environment setup, the version that you are using and a simple reproducible case.

If you have other questions, you can ask in our community [forum](https://community.terminusdb.com/) or [Discord](https://discord.gg/Gvdqw97).

## Contribute

It will be nice, if you open an issue first so that we can know what is going on, then, fork this repo and push in your ideas. Do not forget to add some test(s) of what value you adding.

Please check [Contributing.md](Contributing.md) for more information.

## Licence

Apache License (Version 2.0)

Copyright (c) 2019
