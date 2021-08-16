import builtins
import datetime as dt
import enum
import os
import shutil
import sys
from importlib import import_module

import click
from shed import shed

# from terminusdb_client.woqlschema.woql_schema import TerminusClass
import terminusdb_client.woqlschema.woql_schema as woqlschema

from .. import woql_type as wt
from ..errors import InterfaceError

# from ..woql_type import from_woql_type
from ..woqlclient.woqlClient import WOQLClient
from ..woqlschema.woql_schema import HashKey


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
        "Please enter a server location (press enter to use default)",
        type=str,
        default="http://127.0.0.1:6363/",
    )
    # create settings.py
    setting_file = open("settings.py", "w")
    setting_file.write(
        """####
# This is the script for storing the settings to connect to TerminusDB
# database for your project.
####"""
    )
    setting_file.write(f'\nSERVER = "{server_location}"\nDATABASE = "{project_name}"')
    setting_file.close()

    # copy all the other template files
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(this_file_dir)
    for file in files:
        names = file.split("_")
        if names[-1] == "template.py":
            shutil.copyfile(
                this_file_dir + "/" + file, os.getcwd() + "/" + names[0] + ".py"
            )
    print(  # noqa: T001
        "settings.py and schema.py created, please customize them to start your project."
    )


def _load_settings():
    sys.path.append(os.getcwd())

    try:
        _temp = __import__("settings", globals(), locals(), ["SERVER", "DATABASE"], 0)
        server = _temp.SERVER
        database = _temp.DATABASE
        return {"SERVER": server, "DATABASE": database}
    except ImportError:
        msg = "Cannot find settings.py"
        raise ImportError(msg)


def _connect(settings, new_db=True):
    server = settings["SERVER"]
    database = settings["DATABASE"]

    client = WOQLClient(server)
    try:
        client.connect(db=database)
        return client, f"Connected to {database}."
    except InterfaceError as error:
        if "does not exist" in str(error) and new_db:
            client.connect()
            client.create_database(database)
            return client, f"{database} created."
        else:
            raise InterfaceError(f"Cannot connect to {database}.")


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


def _sync(client, database):
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
        print(f"schema.py is updated with {database} schema.")  # noqa: T001
    else:
        print(  # noqa: T001
            f"{database} schema is empty so schema.py has not be changed."
        )


@click.command()
def sync():
    """Pull the current schema plan in database to schema.py"""
    settings = _load_settings()
    database = settings["DATABASE"]
    client, msg = _connect(settings, new_db=False)
    print(msg)  # noqa: T001
    _sync(client, database)


@click.command()
def commit():
    """Push the current schema plan in schema.py to database."""
    settings = _load_settings()
    database = settings["DATABASE"]
    client, msg = _connect(settings)
    print(msg)  # noqa: T001
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
    print(f"{database} schema updated.")  # noqa: T001


@click.command()
@click.argument("database")
def deletedb(database):
    """Delete the database in this project."""
    settings = _load_settings()
    server = settings["SERVER"]
    setting_database = settings["DATABASE"]
    if database != setting_database:
        raise ValueError(
            "Name provided does not match project database name. You can only delete the database in this project."
        )
    else:
        client = WOQLClient(server)
        client.connect()
        client.delete_database(database, client._account)
        print(f"{database} deleted.")  # noqa: T001


@click.command()
@click.argument("csv_file")
@click.option("--sep", default=",", show_default=True)
# @click.option('--header ', default=',', show_default=True)
def importcsv(csv_file, sep):
    """Import CSV file into pandas DataFrame then into TerminusDB, options are read_csv() options."""
    try:
        pd = import_module("pandas")
        np = import_module("numpy")
    except ImportError:
        raise ImportError(
            "Library 'pandas' is required to import csv, either install 'pandas' or install woqlDataframe requirements as follows: python -m pip install -U terminus-client-python[dataframe]"
        )
    settings = _load_settings()
    settings["SERVER"]
    database = settings["DATABASE"]
    df = pd.read_csv(csv_file, sep=sep)
    class_name = csv_file.split(".")[0].capitalize()
    class_dict = {"@type": "Class", "@id": class_name}
    np_to_buildin = {
        v: getattr(builtins, k) for k, v in np.typeDict.items() if k in vars(builtins)
    }
    np_to_buildin[np.datetime64] = dt.datetime
    for col, dtype in dict(df.dtypes).items():
        converted_type = np_to_buildin[dtype.type]
        if converted_type == object:
            converted_type = str  # pandas treats all string as objects
        converted_type = wt.to_woql_type(converted_type)
        converted_col = col.lower().replace(" ", "_")
        df.rename(columns={col: converted_col}, inplace=True)
        class_dict[converted_col] = converted_type
    class_dict["@key"] = {"@type": "Hash", "@fields": list(df.columns)}
    client, msg = _connect(settings)
    client.update_document(
        class_dict,
        commit_msg=f"Schema object insert/ update with {csv_file} insert by Python client.",
        graph_type="schema",
    )
    # if client.has_doc(class_name, graph_type="schema"):
    #     client.replace_document(
    #         class_dict,
    #         commit_msg=f"Schema object update with {csv_file} insert by Python client.",
    #         graph_type="schema",
    #     )
    # else:
    #     client.insert_document(
    #         class_dict,
    #         commit_msg=f"Schema object created with {csv_file} insert by Python client.",
    #         graph_type="schema",
    #     )
    print(  # noqa: T001
        f"Schema object created with {csv_file} inserted into database."
    )
    _sync(client, database)
    obj_list = df.to_dict(orient="records")
    for item in obj_list:
        item["@type"] = class_name
        item_id = HashKey(list(df.columns)).idgen(item)
        item["@id"] = item_id
    client.update_document(
        obj_list,
        commit_msg=f"Documents created with {csv_file} insert by Python client.",
    )
    print(  # noqa: T001
        f"Records in {csv_file} inserted into database with random ids."
    )


@click.command()
@click.argument("class_obj")
@click.option("--keepid", is_flag=True)
@click.option("--maxdep", default=2, show_default=True)
@click.option("--filename")
# @click.option('--header ', default=',', show_default=True)
def exportcsv(class_obj, keepid, maxdep, filename=None):
    """Export all documents in a TerminusDB class into a flatten CSV file."""
    try:
        pd = import_module("pandas")
    except ImportError:
        raise ImportError(
            "Library 'pandas' is required to export csv, either install 'pandas' or install woqlDataframe requirements as follows: python -m pip install -U terminus-client-python[dataframe]"
        )
    settings = _load_settings()
    settings["SERVER"]
    database = settings["DATABASE"]
    client, msg = _connect(settings, new_db=False)
    all_existing_obj = client.get_all_documents(graph_type="schema")
    all_existing_class = {}
    for item in all_existing_obj:
        if item.get("@id"):
            all_existing_class[item["@id"]] = item
    if class_obj not in all_existing_class:
        raise InterfaceError(f"{class_obj} not found in database ({database}) schema.'")

    all_existing_class[class_obj]

    def expand_df(df):
        for col in df.columns:
            expanded = None
            try:
                expanded = pd.json_normalize(df[col])
            except:
                pass
            if expanded is not None and "@id" in expanded.columns:
                # if len(expanded.columns) == 1:
                #     import pdb; pdb.set_trace()
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

    all_records = client.get_documents_by_type(class_obj)
    df = pd.DataFrame().from_records(list(all_records))
    if not keepid:
        df.drop(columns=list(filter(lambda x: x[0] == "@", df.columns)), inplace=True)
    df = expand_df(df)
    df = embed_obj(df, maxdep=maxdep)
    if filename is None:
        filename = class_obj + ".csv"
    df.to_csv(filename, index=False)
    print(  # noqa: T001
        f"CSV file {filename} created with {class_obj} from database {database}."
    )


@click.command()
@click.option("--schema", is_flag=True)
def alldocs(schema):
    """Get all documents in the database"""
    settings = _load_settings()
    settings["DATABASE"]
    client, msg = _connect(settings)
    if schema:
        print(list(client.get_all_documents(graph_type="schema")))  # noqa: T001
    else:
        print(list(client.get_all_documents()))  # noqa: T001


terminusdb.add_command(startproject)
terminusdb.add_command(sync)
terminusdb.add_command(commit)
terminusdb.add_command(deletedb)
terminusdb.add_command(importcsv)
terminusdb.add_command(exportcsv)
terminusdb.add_command(alldocs)
