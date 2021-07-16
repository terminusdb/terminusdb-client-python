import enum
import os
import shutil
import sys

import click

# from terminusdb_client.woqlschema.woql_schema import TerminusClass
import terminusdb_client.woqlschema.woql_schema as woqlschema
from terminusdb_client.errors import DatabaseError, InterfaceError
from terminusdb_client.woqlclient.woqlClient import WOQLClient


@click.group()
def terminusdb():
    pass


@click.command()
def startproject():
    """Copy the template files into current working directory"""
    this_file_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(this_file_dir)
    for file in files:
        names = file.split("_")
        if names[-1] == "template.py":
            shutil.copyfile(
                this_file_dir + "/" + file, os.getcwd() + "/" + names[0] + ".py"
            )


def _load_settings():
    sys.path.append(os.getcwd())

    try:
        _temp = __import__("settings", globals(), locals(), ["SERVER", "DATABASE"], 0)
        SERVER = _temp.SERVER
        DATABASE = _temp.DATABASE
        return {"SERVER": SERVER, "DATABASE": DATABASE}
    except ImportError:
        msg = "Cannot find settings.py"
        raise ImportError(msg)


def _connect():
    SETTINGS = _load_settings()
    SERVER = SETTINGS["SERVER"]
    DATABASE = SETTINGS["DATABASE"]

    client = WOQLClient(SERVER)
    client.connect()
    try:
        client.create_database(DATABASE)
        return client, f"{DATABASE} created."
    except DatabaseError as error:
        if "Database already exists." in error.message:
            client.connect(db=DATABASE)
            return client, f"Connected to {DATABASE}."
        else:
            raise InterfaceError(f"Cannot connect to {DATABASE}.")


@click.command()
def sync():
    _, msg = _connect()
    print(msg)


@click.command()
def commit():
    client, msg = _connect()
    print(msg)
    schema_plan = __import__("schema", globals(), locals(), [], 0)
    all_existing_obj = client.get_all_documents(graph_type="schema")
    all_existing_id = list(map(lambda x: x.get("@id"), all_existing_obj))
    insert_schema = woqlschema.WOQLSchema()
    update_schema = woqlschema.WOQLSchema()
    for obj_str in dir(schema_plan):
        obj = eval(f"schema_plan.{obj_str}")
        if isinstance(obj, woqlschema.TerminusClass) or isinstance(obj, enum.EnumMeta):
            if obj_str not in dir(woqlschema):
                if obj_str in all_existing_id:
                    obj._schema = update_schema
                    update_schema.add_obj(obj)
                else:
                    obj._schema = insert_schema
                    insert_schema.add_obj(obj)
    client.replace_document(
        update_schema,
        commit_msg="Schema updated by Python client.",
        graph_type="schema",
    )
    client.insert_document(
        insert_schema,
        commit_msg="Schema object insert by Python client.",
        graph_type="schema",
    )
    print("Schema updated.")


@click.command()
@click.argument("database")
def deletedb(database):
    SETTINGS = _load_settings()
    SERVER = SETTINGS["SERVER"]
    DATABASE = SETTINGS["DATABASE"]
    if database != DATABASE:
        raise ValueError(
            "Name provided does not match project database name. You can only delete the database in this project."
        )
    else:
        client = WOQLClient(SERVER)
        client.connect()
        client.delete_database(database, client._account)
        print(f"{database} deleted.")


terminusdb.add_command(startproject)
terminusdb.add_command(sync)
terminusdb.add_command(commit)
terminusdb.add_command(deletedb)
