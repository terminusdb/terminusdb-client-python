<img src="https://assets.terminusdb.com/images/main_lockup.png" width="700px"/>

TerminusDB Client Python
==========================

![Discord online](https://img.shields.io/discord/689805612053168129?color=7289da&logo=Discord&label=Discord%20chat) 
![Discourse topics](https://img.shields.io/discourse/topics?color=yellow&logo=Discourse&server=https%3A%2F%2Fdiscuss.terminusdb.com%2F)
![Follow on Twitter](https://img.shields.io/twitter/follow/terminusdb?color=skyblue&label=Follow%20on%20Twitter&logo=twitter&style=flat)


**Development status ⚙️**

[![Build Status](https://img.shields.io/github/workflow/status/terminusdb/terminusdb-client-python/Python%20package?logo=github)](https://github.com/terminusdb/terminusdb-client-python/actions)
[![Documentation Status](https://img.shields.io/github/deployments/terminusdb/terminusdb-client-python/github-pages?label=documentation&logo=github)](https://terminusdb.github.io/terminusdb-client-python/)
[![codecov](https://codecov.io/gh/terminusdb/terminusdb-client-python/branch/master/graph/badge.svg?token=BclAUaOPnQ)](https://codecov.io/gh/terminusdb/terminusdb-client-python)
[![last commit](https://img.shields.io/github/last-commit/terminusdb/terminusdb-client-python?logo=github)](https://github.com/terminusdb/terminusdb-client-python/commits/master)
[![number of contributors](https://img.shields.io/github/contributors/terminusdb/terminusdb-client-python?color=blue&logo=github)](https://github.com/terminusdb/terminusdb-client-python/graphs/contributors)

**Python Package status 📦**

[![PyPI version shields.io](https://img.shields.io/pypi/v/terminusdb-client.svg?logo=pypi)](https://pypi.python.org/pypi/terminusdb-client/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/terminusdb-client.svg?logo=python)](https://pypi.python.org/pypi/terminusdb-client/)
[![GitHub license](https://img.shields.io/github/license/terminusdb/terminusdb-client-python?color=pink&logo=apache)](https://github.com/terminusdb/terminusdb-client-python/blob/master/LICENSE)
[![PyPI download month](https://img.shields.io/pypi/dm/terminusdb-client.svg?logo=pypi)](https://pypi.python.org/pypi/terminusdb-client/)


### Python version of the TerminusDB client - for TerminusDB API and WOQLpy

![Demo gif](https://github.com/terminusdb/terminusdb-web-assets/blob/master/images/Web.gif)

## Requirements
- [TerminusDB 4](https://github.com/terminusdb/terminusdb-server)
- [Python >=3.6](https://www.python.org/downloads)

## Release Notes and Previous Versions

Please check [RELEASE_NOTES.md](RELEASE_NOTES.md) to find out what has changed.

These previous version(s) works with these version(s) of TerminusDB:

- 0.1.5 - works with TerminusDB server / console v2.0.4
- 0.2.2 - works with TerminusDB server / console v2.0.5
- 0.3.1 - works with TerminusDB server / console v3.0.0 to console v3.0.6
- 0.4.0 - works with TerminusDB server / console v3.0.7
- 0.5.0 - works with TerminusDB server / console v4.0.0

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
>>> client.create_database("university", accountid="admin", label="University Graph", description="graph connect
")
{'@type': 'api:DbCreateResponse', 'api:status': 'api:success'}

>>> client.get_database("university", account="admin")
{'label': 'University Graph', 'comment': 'graph connecting students with their courses in the university', 'id':
 'university', 'organization': 'admin'}
>>> WOQLQuery().doctype("scm:student").property("scm:name", "xsd:string").execute(client, "student schema created.")
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': [], 'bindings': [{}], 'deletes'
: 0, 'inserts': 5, 'transaction_retry_count': 0}

>>> WOQLQuery().insert("stu001", "scm:student").property("scm:name", "Alice").execute(client, "Adding Alice.")
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': [], 'bindings': [{}], 'deletes': 0, 'inserts': 2, 'transaction_retry_count': 0}
>>> WOQLQuery().insert("stu002", "scm:student").property("scm:name", "Bob").execute(client, "Adding Bob.")
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': [], 'bindings': [{}], 'deletes': 0, 'inserts': 2, 'transaction_retry_count': 0}
>>> client.query(WOQLQuery().star())
{'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': ['Subject', 'Predicate', 'Object'], 'bindings': [{'Object': 'terminusdb:///schema#student', 'Predicate': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'Subject': 'terminusdb:///data/stu001'}, {'Object': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': 'Alice'}, 'Predicate': 'terminusdb:///schema#name', 'Subject': 'terminusdb:///data/stu001'}, {'Object': 'terminusdb:///schema#student', 'Predicate': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'Subject': 'terminusdb:///data/stu002'}, {'Object': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': 'Bob'}, 'Predicate': 'terminusdb:///schema#name', 'Subject': 'terminusdb:///data/stu002'}], 'deletes': 0, 'inserts': 0, 'transaction_retry_count': 0}
```
Please check the [full Documentation](https://terminusdb.github.io/terminusdb-client-python/) for more information.

## Tutorials

There is a [list of examples](https://terminusdb.github.io/terminusdb-client-python/tutorials.html) that uses the Python client in our [tutorial repo](https://github.com/terminusdb/terminus-tutorials/). As a start, we would recommend having a look at [create TerminusDB graph with Python client using Jupyter notebook](https://github.com/terminusdb/terminusdb-tutorials/blob/master/bike-tutorial/python/Create%20TerminusDB%20Graph%20with%20Python%20Client.ipynb)

## Testing

1. Clone this repository
`git clone https://github.com/terminusdb/terminusdb-client-python.git`

2. Install all development dependencies using pipenv
```sh
$ make init
```

3. (a) To run test files only
```sh
$ pytest terminusdb_client/tests
```

3. (b) To run full test
```sh
$ tox -e test
```

## Documentation

Visit our [TerminusDB Documentation](https://terminusdb.com/docs/terminusdb/#/) for the full explanation of using TerminusDB.

Documentation specifically on the latest version of the Python Client can be found [here](https://terminusdb.github.io/terminusdb-client-python/).

### Generating Documentation Locally using Sphinx

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

If you encounter any issues, please [report them](https://github.com/terminusdb/terminusdb-client-python/issues) with your os and environment setup, the version that you are using and a simple reproducible case.

If you have other questions, you can ask in our community [forum](https://community.terminusdb.com/) or [Discord server](https://discord.gg/Gvdqw97).

## Community

Come visit us on our [discord server](https://discord.gg/yTJKAma)
or our [forum](https://discuss.terminusdb.com). We are also on [twitter](https://twitter.com/TerminusDB)
<img align="right" src="https://assets.terminusdb.com/images/TerminusDB%20color%20mascot.png" width="256px"/>

## Contribute

It will be nice, if you open an issue first so that we can know what is going on, then, fork this repo and push in your ideas. Do not forget to add some test(s) of what value you adding.

Please check [CONTRIBUTING.md](CONTRIBUTING.md) for more information.

## Licence

Apache License (Version 2.0)

Copyright (c) 2019
