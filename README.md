TerminusDB Client Python
==========================

[![build status](https://api.travis-ci.com/terminusdb/terminusdb-client-python.svg?branch=master)](https://travis-ci.com/terminusdb/terminusdb-client-python)
[![Documentation Status](https://readthedocs.org/projects/terminusdb-client/badge/?version=latest)](https://terminusdb-client.readthedocs.io/en/latest/?badge=latest)

Python version of the TerminusDB client - for TerminusDB API and WOQLpy

## Requirements
- [TerminusDB 3](https://github.com/terminusdb/terminusdb-server)
- [Python >=3.6](https://www.python.org/downloads)
## Release Notes and Previous Versions

- Please check [RELEASE_NOTES.md](RELEASE_NOTES.md) to find out what has changed.

These previous version(s) works with these version(s) of TerminusDB:

- 0.1.5 - works with TerminusDB server / console v2.0.4
- 0.2.2 - works with TerminusDB server / console v2.0.5
- 0.3.1 - works with TerminusDB server / console v3.0.0 to console v3.0.6
- 0.4.0 - works with TerminusDB server / console v3.0.7

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
```
>>> from terminusdb_client import WOQLQuery, WOQLClient
>>> client = WOQLClient(server_url = "https://127.0.0.1:6363")
>>> client.connect(key="root", account="admin", user="admin")
>>> client.db()
False
>>> client.create_database("university", accountid="admin", label="University Graph", description="graph connect
ing students with their courses in the university")
{'@type': 'api:DbCreateResponse', 'api:status': 'api:success'}
>>> client.db()
'university'
>>> schema = WOQLQuery().doctype("student").property("name","string")
>>> schema.execute(client, "some commit msg")
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': [], 'bindings': [{}], 'delet
es': 0, 'inserts': 5, 'transaction_retry_count': 0}
>>> insert = WOQLQuery().insert("Bob","scm:student")
>>> qry = WOQLQuery().when(True, insert)
>>> client.query(qry, 'university')
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': [], 'bindings': [{}], 'deletes': 0, 'inserts': 1, 'transaction_retry_count': 0}
```
Please check the [full Documentation](https://terminusdb.github.io/terminusdb-client-python/) for more information.

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
