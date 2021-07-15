import os
import shutil
import sys

import click

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.errors import DatabaseError, InterfaceError
from requests.exceptions import ConnectionError

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


@click.command()
def connect():
    sys.path.append(os.getcwd())

    try:
        _temp = __import__("settings", globals(), locals(), ["SERVER", "DATABASE"], 0)
        SERVER = _temp.SERVER
        DATABASE = _temp.DATABASE
    except ImportError:
        msg = "Cannot find settings.py"
        raise ImportError(msg)

    global client = WOQLClient(SERVER)
    # client = WOQLClient("http://123123:6363/")
    # client.connect()
    client.connect()
    try:
        client.create_database(DATABASE)
        print(f"{DATABASE} created.")
    except DatabaseError as error:
        if "Database already exists." in error.message:
            client.connect(db=DATABASE)
            print(f"Connected to {DATABASE}.")
        else:
            raise InterfaceError(f"Cannot connect to {DATABASE}.")


terminusdb.add_command(startproject)
terminusdb.add_command(connect)
