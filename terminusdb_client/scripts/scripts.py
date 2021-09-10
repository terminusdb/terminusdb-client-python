import builtins
import datetime as dt
import enum
import json
import os
import shutil
import sys
from importlib import import_module

import click
from shed import shed
from tqdm import tqdm

# from terminusdb_client.woqlschema.woql_schema import TerminusClass
import terminusdb_client.woqlschema.woql_schema as woqlschema

from .. import woql_type as wt
from ..errors import InterfaceError

# from ..woql_type import from_woql_type
from ..woqlclient.woqlClient import WOQLClient
from ..woqlschema.woql_schema import LexicalKey, RandomKey


@click.group()
def terminusdb():
    pass


@click.command()
def startproject():
    """Create the template files into current working directory"""
    # prompt to get info for settings.py
    project_name = click.prompt(
        "Please enter a project name (this will also be the database name)", type=str
    )
    server_location = click.prompt(
        "Please enter a endpoint location (press enter to use localhost default)",
        type=str,
        default="http://127.0.0.1:6363/",
    )

    if "http://127.0.0.1" not in server_location:

        use_token = click.confirm("Are you using the TERMINUSDB_ACCESS_TOKEN?")
        if use_token:
            click.echo(
                "Please make sure you have set up TERMINUSDB_ACCESS_TOKEN in your enviroment variables."
            )
        team = click.prompt(
            "Please enter the team for login",
            type=str,
        )

        # create config.json
        with open("config.json", "w") as outfile:
            json.dump(
                {
                    "endpoint": server_location,
                    "database": project_name,
                    "use JWT token": use_token,
                    "team": team,
                },
                outfile,
                sort_keys=True,
                indent=4,
            )
    else:
        # create config.json
        with open("config.json", "w") as outfile:
            json.dump(
                {
                    "endpoint": server_location,
                    "database": project_name,
                    "team": "admin",
                },
                outfile,
                sort_keys=True,
                indent=4,
            )

    # copy all the other template files
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(this_file_dir)
    for file in files:
        names = file.split("_")
        if names[-1] == "template.py":
            shutil.copyfile(
                this_file_dir + "/" + file, os.getcwd() + "/" + names[0] + ".py"
            )
    # create operational file for TerminiusDB
    with open(".TDB", "w") as outfile:
        json.dump({"branch": "main"}, outfile)
    click.echo(
        "config.json and schema.py created, please customize them to start your project."
    )


def _load_settings(filename="config.json", check=("endpoint", "database")):
    with open(filename) as input_file:
        config = json.load(input_file)
    for item in check:
        if config.get(item) is None:
            raise InterfaceError(f"'{item}' setting cannot be found.")
    return config


def _connect(settings, new_db=True):
    server = settings.get("endpoint")
    database = settings.get("database")
    use_token = settings.get("use JWT token")
    team = settings.get("team")
    branch = settings.get("branch")
    if not team:
        team = "admin"
    if not branch:
        branch = "main"
    client = WOQLClient(server)
    try:
        client.connect(db=database, use_token=use_token, team=team, branch=branch)
        return client, f"Connected to {database}."
    except InterfaceError as error:
        if "does not exist" in str(error) and new_db:
            client.connect(use_token=use_token, team=team, branch=branch)
            client.create_database(database)
            return client, f"{database} created."
        else:
            raise InterfaceError(f"Cannot connect to {database}. Details: {error}")


def _create_script(obj_list):
    class ResultObj:
        def __init__(self, name, parent, script=None):
            self.name = name
            if parent in dir(woqlschema):
                self.parent = None
            else:
                self.parent = parent
            if script is None:
                if type(parent) == str or len(parent) == 1:
                    self.script = f"class {name}({parent}):\n"
                elif len(parent) > 1:
                    self.script = f"class {name}({', '.join(parent)}):\n"
                else:
                    self.script = f"class {name}:\n"
            else:
                self.script = script

        def add_key(self, key: str, fields: list = None):
            if fields is None:
                self.script += f"    _key = {key}Key()\n"
            else:
                self.script += f"    _key = {key}Key({fields})\n"

        def add_subdoc(self):
            self.script += "    _subdocument = []\n"

        def add_abstract(self):
            self.script += "    _abstract = []\n"

        def add_docstring(self, obj_dict):
            self.script += '    """'
            if obj_dict["@documentation"].get("@comment"):
                self.script += f'{obj_dict["@documentation"]["@comment"]}'
            if obj_dict["@documentation"].get("@properties"):
                self.script += "\n\n    Attributes\n    ----------\n"
                for prop, discription in obj_dict["@documentation"][
                    "@properties"
                ].items():
                    self.script += f"    {prop} : {wt.from_woql_type(obj_dict[prop], skip_convert_error=True, as_str=True)}\n        {discription}\n"
                self.script += "    "
            self.script += '"""\n'

    import_objs = []
    print_script = """####
# This is the script for storing the schema of your TerminusDB
# database for your project.
# Use 'terminusdb commit' to commit changes to the database and
# use 'terminusdb sync' to change this file according to
# the exsisting database schema
####\n\n"""
    for obj_str in dir(woqlschema):
        obj = eval(f"woqlschema.{obj_str}")  # noqa: S307
        if (
            isinstance(obj, woqlschema.TerminusClass)
            or isinstance(obj, enum.EnumMeta)
            or isinstance(obj, type(woqlschema.TerminusKey))
        ):
            import_objs.append(obj_str)
    print_script += "from typing import List, Optional, Set\n"
    print_script += (
        f"from terminusdb_client.woqlschema import {', '.join(import_objs)}\n"
    )

    result_list = []
    for obj in obj_list:
        if obj.get("@id"):
            if obj.get("@inherits"):
                result_obj = ResultObj(obj["@id"], obj["@inherits"])
            elif obj["@type"] == "Class":
                result_obj = ResultObj(obj["@id"], "DocumentTemplate")
            elif obj["@type"] == "Enum":
                result_obj = ResultObj(obj["@id"], "EnumTemplate")
                for value in obj["@value"]:
                    if " " not in value:
                        result_obj.script += f"    {value} = ()\n"
                    else:
                        result_obj.script += (
                            f"    {value.replace(' ','_')} = '{value}'\n"
                        )
            if obj.get("@documentation"):
                result_obj.add_docstring(obj)
            if obj.get("@subdocument") is not None:
                result_obj.add_subdoc()
            elif obj.get("@key"):
                result_obj.add_key(obj["@key"]["@type"], obj["@key"].get("@fields"))

            if obj.get("@abstract") is not None:
                result_obj.add_abstract()
            result_list.append(result_obj)

            for key, value in obj.items():
                if key[0] != "@":
                    result_obj.script += f"    {key}:{wt.from_woql_type(value, skip_convert_error=True, as_str=True)}\n"

    # sorts depends on the object inherits order
    printed = []
    while len(result_list) > 0:
        obj = result_list.pop(0)
        if obj.parent is None:
            print_script += obj.script
            printed.append(obj.name)
        elif type(obj.parent) == str and obj.parent in printed:
            print_script += obj.script
            printed.append(obj.name)
        else:
            parent_is_in = False
            for mama in obj.parent:
                if mama in printed:
                    parent_is_in = True
            if parent_is_in:
                print_script += obj.script
                printed.append(obj.name)
            else:
                result_list.append(obj)
    return print_script


def _sync(client):
    all_existing_obj = client.get_all_documents(graph_type="schema")
    all_obj_list = []
    for obj in all_existing_obj:
        all_obj_list.append(obj)
    if len(all_obj_list) > 1:
        print_script = _create_script(all_obj_list)
        print_script = shed(source_code=print_script)
        file = open("schema.py", "w")
        file.write(print_script)
        file.close()
        click.echo(f"schema.py is updated with {client.db} schema.")
    else:
        click.echo(f"{client.db} schema is empty so schema.py has not be changed.")


@click.command()
def sync():
    """Pull the current schema plan in database to schema.py"""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    settings["database"]
    client, msg = _connect(settings, new_db=False)
    click.echo(msg)
    _sync(client)


@click.command()
def commit():
    """Push the current schema plan in schema.py to database."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    database = settings["database"]
    client, msg = _connect(settings)
    click.echo(msg)
    sys.path.append(os.getcwd())
    schema_plan = __import__("schema", globals(), locals(), [], 0)
    all_obj = []
    for obj_str in dir(schema_plan):
        obj = eval(f"schema_plan.{obj_str}")  # noqa: S307
        if isinstance(obj, woqlschema.TerminusClass) or isinstance(obj, enum.EnumMeta):
            if obj_str not in ["DocumentTemplate", "EnumTemplate", "TaggedUnion"]:
                all_obj.append(obj)
    client.update_document(
        all_obj,
        commit_msg="Schema updated by Python client.",
        graph_type="schema",
    )
    click.echo(f"{database} schema updated.")


@click.command()
def deletedb():
    """Delete the database in this project."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    database = settings["database"]
    if click.confirm(
        f"Do you want to delete '{settings['database']}'? WARNING: This opertation is non-reversible."
    ):
        client, _ = _connect(settings, new_db=False)
        client.delete_database(database, client.team)
        # reset to main branch
        status["branch"] = "main"
        with open(".TDB", "w") as outfile:
            json.dump(status, outfile)
        click.echo(f"{database} deleted.")


def _get_existing_class(client):
    all_existing_obj = client.get_all_documents(graph_type="schema")
    all_existing_class = {}
    for item in all_existing_obj:
        if item.get("@id"):
            all_existing_class[item["@id"]] = item
    return all_existing_class


@click.command()
@click.argument("csv_file")
@click.argument("keys", nargs=-1)
@click.option(
    "--classname",
    "class_name",
    help="Customize the class name that the data from the CSV will be import as",
)
@click.option(
    "--chunksize",
    default=1000,
    show_default=True,
    help="Large files will be load into database in chunks, size of the chunks",
)
@click.option(
    "--schema",
    is_flag=True,
    help="Specify if schema to be updated if existed, default False",
)
@click.option(
    "--na",
    default="optional",
    type=click.Choice(["skip", "optional", "error"], case_sensitive=False),
    help="Specify how to handle NAs: 'skip' will skip entries with NAs, 'optional' will make all properties optional in the database, 'error' will just thow an error if there's NAs",
)
@click.option(
    "--id", "id_", help="Specify column to be used as ids instead of generated ids"
)
@click.option("-e", "--embedded", multiple=True, help="Specify embedded columns")
@click.option("--sep", default=",", show_default=True)
# @click.option('--header ', default=',', show_default=True)
def importcsv(csv_file, keys, class_name, chunksize, schema, na, id_, embedded, sep):
    """Import CSV file into pandas DataFrame then into TerminusDB, with read_csv() options.
    Options like chunksize, sep etc"""
    # If chunksize is too small, pandas may decide certain column to be integer if all values in the 1st chunk are 0.0. This can be problmetic for some cases.
    na = na.lower()
    if id_:
        id_ = id_.lower().replace(" ", "_")
    if keys:
        keys = list(map(lambda x: x.lower().replace(" ", "_"), keys))
    if embedded:
        embedded = list(map(lambda x: x.lower().replace(" ", "_"), embedded))
    try:
        pd = import_module("pandas")
        np = import_module("numpy")
    except ImportError:
        raise ImportError(
            "Library 'pandas' is required to import csv, either install 'pandas' or install woqlDataframe requirements as follows: python -m pip install -U terminus-client-python[dataframe]"
        )
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, msg = _connect(settings)
    if not class_name:
        class_name = csv_file.split(".")[0].replace("_", " ").title().replace(" ", "")
    # "not schema" make it always False if adding the schema option
    has_schema = not schema and class_name in _get_existing_class(client)

    def _df_to_schema(class_name, df):
        class_dict = {"@type": "Class", "@id": class_name}
        np_to_buildin = {
            v: getattr(builtins, k)
            for k, v in np.typeDict.items()
            if k in vars(builtins)
        }
        np_to_buildin[np.datetime64] = dt.datetime
        for col, dtype in dict(df.dtypes).items():
            if embedded and col in embedded:
                converted_type = class_name
            else:
                converted_type = np_to_buildin[dtype.type]
                if converted_type == object:
                    converted_type = str  # pandas treats all string as objects
                converted_type = wt.to_woql_type(converted_type)

            if id_ and col == id_:
                class_dict[col] = converted_type
            elif na == "optional" and col not in keys:
                class_dict[col] = {"@type": "Optional", "@class": converted_type}
            else:
                class_dict[col] = converted_type
        # if id_ is not None:
        #     pass  # don't need key if id is specified
        # elif keys:
        #     class_dict["@key"] = {"@type": "Random"}
        # elif na == "optional":
        #     # have to use random key cause keys will be optional
        #     class_dict["@key"] = {"@type": "Random"}
        # else:
        #     class_dict["@key"] = {"@type": "Random"}
        return class_dict

    with pd.read_csv(csv_file, sep=sep, chunksize=chunksize) as reader:
        for df in tqdm(reader):
            if any(df.isna().any()) and na == "error":
                raise RuntimeError(
                    f"{df}\nThere is NA in the data and cannot be automatically load in. Use --na options to remove all records with NA or make properties optional to accept missing data."
                )
            elif na == "skip":
                df.dropna(inplace=True)
            for col in df.columns:
                converted_col = col.lower().replace(" ", "_").replace(".", "_")
                df.rename(columns={col: converted_col}, inplace=True)
            if not has_schema:
                class_dict = _df_to_schema(class_name, df)
                client.update_document(
                    class_dict,
                    commit_msg=f"Schema object insert/ update with {csv_file} insert by Python client.",
                    graph_type="schema",
                )
                click.echo(
                    f"\nSchema object {class_name} created with {csv_file} inserted into database."
                )
                _sync(client)
                has_schema = True

            obj_list = df.to_dict(orient="records")
            for item in obj_list:
                # handle missing items
                if na == "optional":
                    bad_key = []
                    for key, value in item.items():
                        if pd.isna(value):
                            if key in keys:
                                raise RuntimeError(
                                    f"{key} is used as a key but missing in {item}. Cannot import CSV."
                                )
                            bad_key.append(key)
                    for key in bad_key:
                        item.pop(key)
                # handle embedded items
                if embedded:
                    new_items = {}
                    for key, value in item.items():
                        if key in embedded:
                            new_items[key] = {
                                "@type": "@id",
                                "@id": class_name + "/" + value,
                            }
                    item.update(new_items)
                # adding type
                item["@type"] = class_name
                # adding ids
                if id_:
                    if id_ in item:
                        item_id = class_name + "/" + item[id_]
                    else:
                        raise RuntimeError(
                            f"id {id} is missing in {item}. Cannot import CSV."
                        )
                elif keys:
                    item_id = LexicalKey(list(keys)).idgen(item)
                elif na == "optional":
                    item_id = RandomKey().idgen(item)
                else:
                    item_id = LexicalKey(list(df.columns)).idgen(item)
                item["@id"] = item_id
            client.update_document(
                obj_list,
                commit_msg=f"Documents created with {csv_file} insert by Python client.",
            )
    if id_:
        key_type = "specified"
    elif na == "optional" and not keys:
        key_type = "Random"
    else:
        key_type = "Lexical"
    # key_type = "Random" if (na == "optional" and not keys) else "Lexical"
    click.echo(
        f"Records in {csv_file} inserted as type {class_name} into database with {key_type} ids."
    )


def _exportcsv(
    class_obj, client, all_records, all_existing_class, keepid, maxdep, filename=None
):
    """Export into a flatten CSV file."""
    try:
        pd = import_module("pandas")
    except ImportError:
        raise ImportError(
            "Library 'pandas' is required to export csv, either install 'pandas' or install woqlDataframe requirements as follows: python -m pip install -U terminus-client-python[dataframe]"
        )

    def expand_df(df):
        for col in df.columns:
            try:
                expanded = pd.json_normalize(df[col])
            except Exception:
                expanded = None
            if expanded is not None and "@id" in expanded.columns:
                if not keepid:
                    expanded.drop(
                        columns=list(filter(lambda x: x[0] == "@", expanded.columns)),
                        inplace=True,
                    )
                expanded.columns = list(map(lambda x: col + "." + x, expanded))
                df.drop(columns=col, inplace=True)
                df = df.join(expanded)
        return df

    def embed_obj(df, maxdep):
        if maxdep == 0:
            return df
        for col in df.columns:
            if "@" not in col:
                col_comp = col.split(".")
                if len(col_comp) == 1:
                    prop_type = all_existing_class[class_obj][col]
                else:
                    prop_type = class_obj
                    for comp in col_comp:
                        prop_type = all_existing_class[prop_type][comp]
                if (
                    isinstance(prop_type, str)
                    and prop_type[:4] != "xsd:"
                    and prop_type != class_obj
                ):
                    df[col] = df[col].apply(client.get_document)
        finish_df = expand_df(df)
        if (
            len(finish_df.columns) == len(df.columns)
            and (finish_df.columns == df.columns).all()
        ):
            return finish_df
        else:
            return embed_obj(finish_df, maxdep - 1)

    df = pd.DataFrame().from_records(list(all_records))
    if not keepid:
        df.drop(columns=list(filter(lambda x: x[0] == "@", df.columns)), inplace=True)
    df = expand_df(df)
    df = embed_obj(df, maxdep=maxdep)
    if filename is None:
        filename = class_obj + ".csv"
    df.to_csv(filename, index=False)
    click.echo(
        f"CSV file {filename} created with {class_obj} from database {client.db}."
    )


@click.command()
@click.argument("class_obj")
@click.option(
    "--keepid", is_flag=True, help="If the id of the object is to be kept in the CSV"
)
@click.option(
    "--maxdep",
    default=2,
    show_default=True,
    help="Specify the depth of the embedding operation. When maximum is hit, the values will be kept as object ids",
)
@click.option(
    "--filename",
    help="File name if the exported file, if not specify it will use the name of the class e.g. 'ClassName.csv'",
)
# @click.option('--header ', default=',', show_default=True)
def exportcsv(class_obj, keepid, maxdep, filename=None):
    """Export all documents in a TerminusDB class into a flatten CSV file."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    settings["database"]
    client, msg = _connect(settings, new_db=False)
    all_existing_class = _get_existing_class(client)
    if class_obj not in all_existing_class:
        raise InterfaceError(
            f"{class_obj} not found in database ({client.db}) schema.'"
        )
    all_records = client.get_documents_by_type(class_obj)
    _exportcsv(
        class_obj,
        client,
        all_records,
        all_existing_class,
        keepid,
        maxdep,
        filename=None,
    )


@click.command()
@click.option("--schema", is_flag=True, help="Specify if getting schema object instead")
@click.option("--type", "type_", help="Type of the objects to be getting back")
@click.option(
    "-q",
    "--query",
    multiple=True,
    help="Use query to filter out objects getting back. Need to be used with --type",
)
@click.option(
    "-e",
    "--export",
    is_flag=True,
    help="Specify if the result to be export as CSV. Only usable when using –type and not –schema",
)
@click.option(
    "--keepid",
    is_flag=True,
    help="Option for export: if the id of the object is to be kept in the CSV",
)
@click.option(
    "--maxdep",
    default=2,
    show_default=True,
    help="Option for export: specify the depth of the embedding operation",
)
@click.option("--filename", help="Option for export: file name if the exported file")
def alldocs(schema, type_, query, export, keepid, maxdep, filename=None):
    """Get all documents in the database, use --schema to specify schema, --type to select type and -q to make queries (e.g. -q date=2021-07-01)

    If using --type and not --schema, can export using -e with options: --keepid, --maxdep and --filename"""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, msg = _connect(settings)
    if schema:
        if type_:
            click.echo(client.get_document(type_, graph_type="schema"))
        else:
            click.echo(list(client.get_all_documents(graph_type="schema")))
    elif type_:
        all_existing_class = _get_existing_class(client)
        if type_ not in all_existing_class:
            raise InterfaceError(
                f"{type_} not found in database ({client.db}) schema.'"
            )
        if not query:
            result = list(client.get_documents_by_type(type_))
        else:
            schema_dict = client.get_document(type_, graph_type="schema")
            query_dict = {"@type": type_}
            for item in query:
                pair = item.split("=")
                if schema_dict.get(pair[0]) is None:
                    raise InterfaceError(f"{pair[0]} is not a proerty in {type_}")
                elif schema_dict.get(pair[0]) == "xsd:integer":
                    pair[1] = int(pair[1].strip('"'))
                elif schema_dict.get(pair[0]) == "xsd:decimal":
                    pair[1] = float(pair[1].strip('"'))
                elif schema_dict.get(pair[0]) == "xsd:boolean":
                    pair[1] = pair[1].strip('"')
                    if pair[1].lower() == "false":
                        pair[1] = False
                    elif pair[1].lower() == "true":
                        pair[1] = True
                    else:
                        raise InterfaceError(f"{pair[1]} cannot be parse as boolean")
                else:
                    pair[1] = pair[1].strip('"')
                query_dict[pair[0]] = pair[1]
            result = list(client.query_document(query_dict, optimize=True))
        if export:
            _exportcsv(
                type_, client, result, all_existing_class, keepid, maxdep, filename
            )
        else:
            click.echo(result)
    else:
        click.echo(list(client.get_all_documents()))


@click.command()
@click.argument("branch_name", required=False)
def branch(branch_name):
    """Create or list branch."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    if branch_name is None:
        all_branches = client.get_all_branches()
        all_branches = list(map(lambda item: item["name"], all_branches))
        click.echo("\n".join(all_branches))
    else:
        client.create_branch(branch_name)
        click.echo(
            f"Branch '{branch_name}' created. Remain on '{status['branch']}' branch."
        )


@click.command()
@click.argument("branch_name")
@click.option("-b", "--branch", "new_branch", is_flag=True)
def checkout(branch_name, new_branch):
    """Switch branches. Use -b to create and switch to new branch."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    if new_branch:
        client.create_branch(branch_name)
    all_branches = client.get_all_branches()
    all_branches = list(map(lambda item: item["name"], all_branches))
    if branch_name not in all_branches:
        raise InterfaceError(f"{branch_name} does not exist.")
    status["branch"] = branch_name
    with open(".TDB", "w") as outfile:
        json.dump(status, outfile)
    if new_branch:
        click.echo(
            f"Branch '{branch_name}' created, checked out '{branch_name}' branch."
        )
    else:
        click.echo(f"Checked out '{branch_name}' branch.")


@click.command()
def status():
    """Show the working status of the project."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    message = f"Connecting to '{settings['database']}' at '{settings['endpoint']}'\non branch '{settings['branch']}'"
    if settings.get("team"):
        message += f"\nwith team '{settings['team']}'"
    click.echo(message)


@click.command()
@click.argument("branch_name")
def rebase(branch_name):
    """Reapply commits on top of another base tip on another branch."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    client.rebase(branch=branch_name)
    click.echo(f"Rebased {branch_name} branch.")


terminusdb.add_command(startproject)
terminusdb.add_command(sync)
terminusdb.add_command(commit)
terminusdb.add_command(deletedb)
terminusdb.add_command(importcsv)
terminusdb.add_command(exportcsv)
terminusdb.add_command(alldocs)
terminusdb.add_command(branch)
terminusdb.add_command(checkout)
terminusdb.add_command(status)
terminusdb.add_command(rebase)
