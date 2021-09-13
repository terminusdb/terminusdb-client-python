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

![Client Demo gif](https://github.com/terminusdb/terminusdb-web-assets/blob/master/images/terminusdb%20python%20v10%20client%20demo%201.gif)

## Requirements
- [TerminusDB v10.0](https://github.com/terminusdb/terminusdb-server)
- [Python >=3.7](https://www.python.org/downloads)

## Release Notes and Previous Versions

TerminusDB Client v10.0 works with TerminusDB v10.0 and TerminusX. Please check [RELEASE_NOTES.md](RELEASE_NOTES.md) to find out what has changed.

## Installation
-  TerminusDB Client can be downloaded form PyPI using pip:
`python -m pip install terminusdb-client`

This only includes the core Python Client (WOQLClient) and WOQLQuery.

If you want to use woqlDataframe or the import and export csv function in Scaffolding CLI tool:

`python -m pip install terminusdb-client[dataframe]`

*if you are installing form `zsh` you have to quote the argument like this:*

`python -m pip install 'terminusdb-client[dataframe]'`

- Install from source:

`python -m pip install git+https://github.com/terminusdb/terminusdb-client-python.git`

## Usage

### Python client

#### Connect to a server

Connect to local host

```Python
from terminusdb_client import WOQLClient

client = WOQLClient("http://127.0.0.1:6363/")
client.connect()
```

Connect to TerminusX

*check documentation for TerminusX about how to add the API token to the environment variable*


```Python
from terminusdb_client import WOQLClient

team="MyTeam"
client = WOQLClient(f"https://dashboard.terminusdb.com/{team}/")
client.connect(team="MyTeam", use_token=True)
```

#### Create a database

```Python
client.create_database("MyDatabase")
```

#### Create a schema

```Python
from terminusdb_client.woqlschema import WOQLSchema, DocumentTemplate, RandomKey

my_schema = WOQLSchema()

class Pet(DocumentTemplate):
    _schema = my_schema
    name: str
    species: str
    age: int
    weight: float

my_schema.commit(client)
```

#### Create and insert doucments

```Python
my_dog = Pet(name="Honda", species="Huskey", age=3, weight=21.1)
my_cat = Pet(name="Tiger", species="Bengal cat", age=5, weight=4.5)
client.insert_document([my_dog, my_cat])
```

#### Get back all documents

```Python
print(list(client.get_all_documents()))
```

```
[{'@id': 'Pet/b5edacf854e34fe79c228a91e2af45fb', '@type': 'Pet', 'age': 5, 'name': 'Tiger', 'species': 'Bengal cat', 'weight': 4.5}, {'@id': 'Pet/cdbe3f6d49394b38b952ae315309256d', '@type': 'Pet', 'age': 3, 'name': 'Honda', 'species': 'Huskey', 'weight': 21.1}]
```

#### Get a specific document

```Python
print(list(client.query_document({"@type":"Pet", "age":5})))
```

```
[{'@id': 'Pet/145eb73966d14a1394f7cd5576d7d0b8', '@type': 'Pet', 'age': 5, 'name': 'Tiger', 'species': 'Bengal cat', 'weight': 4.5}]
```

#### Delete a database

```Python
client.delete_database("MyDatabase")
```

### Scaffolding CLI tool

![Scaffolding Demo gif](https://github.com/terminusdb/terminusdb-web-assets/blob/master/images/terminusdb%20python%20v10%20scaffolding%20demo%202.gif)

Start a project in the directory

```bash
$terminusdb startproject
Please enter a project name (this will also be the database name): mydb
Please enter a endpoint location (press enter to use localhost default) [http://127.0.0.1:6363/]:
config.json and schema.py created, please customize them to start your project.
```

Import a CSV named `grades.csv`

``` bash
$terminusdb importcsv grades.csv --na=error
0it [00:00, ?it/s]
Schema object Grades created with grades.csv inserted into database.
schema.py is updated with mydb schema.
1it [00:00,  1.00it/s]
Records in grades.csv inserted as type Grades into database with Lexical ids.
```

Get documents with query

```bash
terminusdb alldocs --type Grades -q grade="B-"
[{'@id': 'Grades/Android_Electric_087-65-4321_42.0_23.0_36.0_45.0_47.0_B-', '@type': 'Grades', 'final': 47.0, 'first_name': 'Electric', 'grade': 'B-', 'last_name': 'Android', 'ssn': '087-65-4321', 'test1': 42.0, 'test2': 23.0, 'test3': 36.0, 'test4': 45.0}, {'@id': 'Grades/Elephant_Ima_456-71-9012_45.0_1.0_78.0_88.0_77.0_B-', '@type': 'Grades', 'final': 77.0, 'first_name': 'Ima', 'grade': 'B-', 'last_name': 'Elephant', 'ssn': '456-71-9012', 'test1': 45.0, 'test2': 1.0, 'test3': 78.0, 'test4': 88.0}, {'@id': 'Grades/Franklin_Benny_234-56-2890_50.0_1.0_90.0_80.0_90.0_B-', '@type': 'Grades', 'final': 90.0, 'first_name': 'Benny', 'grade': 'B-', 'last_name': 'Franklin', 'ssn': '234-56-2890', 'test1': 50.0, 'test2': 1.0, 'test3': 90.0, 'test4': 80.0}]
```

Delete the database

```bash
$terminusdb deletedb
Do you want to delete 'mydb'? WARNING: This opertation is non-reversible. [y/N]: y
mydb deleted.
```

### Please check the [full Documentation](https://terminusdb.github.io/terminusdb-client-python/) for more information.

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
