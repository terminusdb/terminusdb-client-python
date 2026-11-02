import builtins
import datetime as dt
import enum
import json
import os
import shutil
import sys
from importlib import import_module

import click
import terminusdb_client.woqlschema.woql_schema as woqlschema
from shed import shed
from tqdm import tqdm

from .. import woql_type as wt
from ..client.Client import Client
from ..errors import InterfaceError
from ..woqldataframe.woqlDataframe import result_to_df
from ..woqlschema.woql_schema import WOQLSchema


def _df_to_schema(
    class_name, df, np, embedded=None, id_col=None, na_mode=None, keys=None
):
    """Convert a pandas DataFrame to a TerminusDB schema class definition.

    Args:
        class_name: Name of the schema class to create
        df: pandas DataFrame with columns to convert
        np: numpy module reference
        embedded: List of column names to treat as embedded references
        id_col: Column name to use as document ID
        na_mode: NA handling mode ('error', 'skip', or 'optional')
        keys: List of column names to use as keys

    Returns:
        dict: Schema class definition dictionary
    """
    if keys is None:
        keys = []
    if embedded is None:
        embedded = []

    class_dict = {"@type": "Class", "@id": class_name}
    np_to_builtin = {
        v: getattr(builtins, k) for k, v in np.sctypeDict.items() if k in vars(builtins)
    }
    np_to_builtin[np.datetime64] = dt.datetime

    for col, dtype in dict(df.dtypes).items():
        if embedded and col in embedded:
            converted_type = class_name
        else:
            converted_type = np_to_builtin.get(dtype.type, object)
            if converted_type is object:
                converted_type = str  # pandas treats all strings as objects
            converted_type = wt.to_woql_type(converted_type)

        if id_col and col == id_col:
            class_dict[col] = converted_type
        elif na_mode == "optional" and col not in keys:
            class_dict[col] = {"@type": "Optional", "@class": converted_type}
        else:
            class_dict[col] = converted_type

    return class_dict


@click.group()
def tdbpy():
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

    # if not local host
    if "http://127.0.0.1" not in server_location:
        team = click.prompt(
            "Please enter the team for login",
            type=str,
        )

        use_token = click.confirm("Are you using API token login?")

        if use_token:
            # set_token = click.confirm("Do you want to set up the TERMINUSDB_ACCESS_TOKEN?")

            if click.confirm("Do you want to set up the TERMINUSDB_ACCESS_TOKEN?"):
                # set token
                api_token = click.prompt(
                    "Please enter the API token",
                    type=str,
                    hide_input=True,
                )
                os.environ["TERMINUSDB_ACCESS_TOKEN"] = api_token

                click.echo(
                    "Token added as TERMINUSDB_ACCESS_TOKEN in your enviroment variables."
                )
            else:
                click.echo(
                    "Please make sure you have set up TERMINUSDB_ACCESS_TOKEN in your enviroment variables."
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
        json.dump({"branch": "main", "ref": None}, outfile)
    click.echo(
        "config.json and schema.py created, please customize them to start your project."
    )


def _load_settings(filename="config.json", check=("endpoint", "database")):
    with open(filename) as input_file:
        config = json.load(input_file)
        if not config:
            raise RuntimeError(f"Cannot load in {filename}")
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
    ref = settings.get("ref")
    if not team:
        team = "admin"
    if not branch:
        branch = "main"
    client = Client(server)
    try:
        client.connect(db=database, use_token=use_token, team=team, branch=branch)
        if ref is not None:
            client.reset(ref, soft=True)
        return client, f"Connected to {database}."
    except InterfaceError as error:
        if "does not exist" in str(error) and new_db:
            client.connect(use_token=use_token, team=team)
            client.create_database(database)
            if branch != "main" or ref is not None:
                with open(".TDB", "w") as outfile:
                    json.dump({"branch": "main", "ref": None}, outfile)
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
                if isinstance(parent, str) or len(parent) == 1:
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
####\n"""
    context = obj_list.pop(0)
    documentation = context.get("@documentation")
    if documentation:
        print_script += '"""\n'
        if documentation.get("@title"):
            print_script += "Title: " + documentation["@title"] + "\n"
        if documentation.get("@description"):
            print_script += "Description: " + documentation["@description"] + "\n"
        if documentation.get("@authors"):
            print_script += "Authors: " + ", ".join(documentation["@authors"]) + "\n"
        print_script += '"""\n'
    for obj_str in dir(woqlschema):
        obj = eval(f"woqlschema.{obj_str}")  # noqa: S307
        if isinstance(
            obj, (woqlschema.TerminusClass, enum.EnumMeta, type(woqlschema.TerminusKey))
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
            elif obj["@type"] == "TaggedUnion":
                result_obj = ResultObj(obj["@id"], "TaggedUnion")
            elif obj["@type"] == "Enum":
                result_obj = ResultObj(obj["@id"], "EnumTemplate")
                for value in obj["@value"]:
                    if " " not in value:
                        result_obj.script += f"    {value} = ()\n"
                    else:
                        result_obj.script += (
                            f"    {value.replace(' ', '_')} = '{value}'\n"
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
        elif isinstance(obj.parent, str) and obj.parent in printed:
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


_PY_KEY_CLASSES = {
    "Lexical": "LexicalKey",
    "Hash": "HashKey",
    "ValueHash": "ValueHashKey",
    "Random": "RandomKey",
    "UuidV7": "UuidV7Key",
}

_PY_BASES = {"DocumentTemplate": "TerminusModel", "TaggedUnion": "TerminusUnion"}


def _enum_member_name(value):
    name = "".join(c if c.isalnum() or c == "_" else "_" for c in value)
    if not name.isidentifier() or (name and name[0].isdigit()):
        name = "value_" + name
    return name


def _pydantic_spec_src(spec, used_keys, used_types):
    """Render a TerminusDB property spec as a pydantic field annotation.

    Returns (annotation_source, default_source_or_None).
    """
    if isinstance(spec, str):
        if spec == "sys:Unit":
            return ("Optional[None]", "None")
        src = wt.from_woql_type(spec, skip_convert_error=True, as_str=True)
        if src.startswith("'"):
            return (src, None)  # class-name forward reference
        if src == "dict":
            return ("dict", None)
        if hasattr(wt, src):
            used_types.add(src)
        return (src, None)
    if not isinstance(spec, dict):
        raise RuntimeError(f"{spec} is not a TerminusDB property spec")

    spec = dict(spec)
    unfold = spec.pop("@unfold", None)
    cardinality = {}
    for key in ("@cardinality", "@min_cardinality", "@max_cardinality"):
        if key in spec:
            cardinality[key] = spec.pop(key)

    spec_type = spec.get("@type")
    inner = spec.get("@class")
    if inner is None:
        raise RuntimeError(f"{spec} is not a TerminusDB property spec")
    inner_src, _ = _pydantic_spec_src(inner, used_keys, used_types)

    if spec_type == "Optional":
        src, default = f"Optional[{inner_src}]", "None"
    elif spec_type == "Set":
        src, default = f"Set[{inner_src}]", None
    elif spec_type in ("Cardinality",):
        src, default = f"Set[{inner_src}]", None
        cardinality = {**spec, **cardinality}
    elif spec_type == "List":
        src, default = f"List[{inner_src}]", None
    elif spec_type == "Array":
        dims = spec.get("@dimensions", 1)
        wrapped = inner_src
        for _ in range(dims):
            wrapped = f"list[{wrapped}]"
        src, default = f"Annotated[{wrapped}, Array]", None
    else:
        raise RuntimeError(f"{spec} is not a TerminusDB property spec")

    if unfold:
        src = f"Annotated[{src}, Unfold]"
    if cardinality:
        lo = cardinality.get("@min_cardinality", cardinality.get("@cardinality"))
        hi = cardinality.get("@max_cardinality", cardinality.get("@cardinality"))
        params = []
        if lo is not None:
            params.append(f"min_length={lo}")
        if hi is not None:
            params.append(f"max_length={hi}")
        default = f"Field({', '.join(params)})"
    return (src, default)


def _create_pydantic_script(obj_list):
    """Emit a pydantic-model schema.py from schema documents."""
    obj_list = list(obj_list)
    context = obj_list.pop(0) if obj_list and obj_list[0].get("@type") == "@context" else None

    used_keys, used_types, result_list = set(), set(), []
    print_script = (
        "####\n"
        "# This is the script for storing the schema of your TerminusDB\n"
        "# database for your project.\n"
        "# Use 'terminusdb commit' to commit changes to the database and\n"
        "# use 'terminusdb sync' to change this file according to\n"
        "# the exsisting database schema\n"
        "####\n"
    )
    if context is not None:
        documentation = context.get("@documentation") or {}
        print_script += '"""\n'
        if documentation.get("@title"):
            print_script += "Title: " + documentation["@title"] + "\n"
        if documentation.get("@description"):
            print_script += "Description: " + documentation["@description"] + "\n"
        if documentation.get("@authors"):
            print_script += "Authors: " + ", ".join(documentation["@authors"]) + "\n"
        print_script += '"""\n'

    for obj in obj_list:
        if not obj.get("@id"):
            continue
        obj_id, obj_type = obj["@id"], obj.get("@type")
        script = ""
        if obj_type == "Enum":
            script = f"class {obj_id}(TerminusEnum):\n"
            for value in obj.get("@value", []):
                script += f'    {_enum_member_name(value)} = "{value}"\n'
        elif obj_type == "Foreign":
            script = f"class {obj_id}(TerminusModel):\n    _foreign = True\n"
        else:
            if obj_type == "TaggedUnion":
                bases = ["TerminusUnion"]
            else:
                parents = obj.get("@inherits")
                if parents:
                    if isinstance(parents, str):
                        parents = [parents]
                    bases = [_PY_BASES.get(p, p) for p in parents]
                else:
                    bases = ["TerminusModel"]
            script = f"class {obj_id}({', '.join(bases)}):\n"
            prop_docs = {}
            if obj.get("@documentation"):
                doc = obj["@documentation"]
                if doc.get("@comment"):
                    script += f'    """{doc["@comment"]}"""\n'
                prop_docs = doc.get("@properties") or {}
            if obj.get("@subdocument") is not None:
                script += "    _subdocument = []\n"
            elif obj.get("@key"):
                key = obj["@key"]
                key_name = _PY_KEY_CLASSES.get(key.get("@type"))
                if key_name is None:
                    raise RuntimeError(f"{key} is not a TerminusDB key type")
                used_keys.add(key_name)
                if key.get("@fields"):
                    script += f"    _key = {key_name}({key['@fields']!r})\n"
                else:
                    script += f"    _key = {key_name}()\n"
            if obj.get("@abstract") is not None:
                script += "    _abstract = []\n"
            if obj.get("@shared") is not None:
                script += "    _shared = True\n"
            if obj.get("@unfoldable") is not None:
                script += "    _unfoldable = True\n"
            if obj.get("@base") is not None:
                script += f'    _base = "{obj["@base"]}"\n'
            if obj.get("@metadata") is not None:
                script += f"    _metadata = {obj['@metadata']!r}\n"
            field_lines = ""
            for key, value in obj.items():
                if key[0] == "@":
                    continue
                src, default = _pydantic_spec_src(value, used_keys, used_types)
                line = f"    {key}: {src}"
                descr = prop_docs.get(key)
                if descr is not None:
                    if default == "None":
                        default = f'Field(default=None, description={descr!r})'
                    elif default is None:
                        default = f'Field(description={descr!r})'
                    else:  # Field(...) for cardinality: append description
                        default = default[:-1] + f', description={descr!r})'
                if default is not None:
                    line += f" = {default}"
                field_lines += line + "\n"
            if field_lines:
                script += field_lines
            elif obj_type == "Class":
                script += "    pass\n"
        # ordering bookkeeping: parents must print before children
        entry = {"name": obj_id, "script": script}
        if obj_type == "Class" and obj.get("@inherits"):
            parents = obj["@inherits"]
            entry["parents"] = [parents] if isinstance(parents, str) else list(parents)
        else:
            entry["parents"] = []
        result_list.append(entry)

    body = ""
    printed = []
    while result_list:
        entry = result_list.pop(0)
        if all(p in printed or p not in {e["name"] for e in result_list + [entry]}
               for p in entry["parents"]):
            body += entry["script"] + "\n"
            printed.append(entry["name"])
        else:
            result_list.append(entry)

    imports = "from typing import Annotated, List, Optional, Set\n"
    if "Field(" in body:
        imports += "from pydantic import Field\n"
    imports += (
        "from terminusdb_client.schema.pydantic import "
        "Array, TerminusEnum, TerminusModel, TerminusUnion, Unfold\n"
    )
    if used_keys:
        imports += (
            f"from terminusdb_client.schema import {', '.join(sorted(used_keys))}\n"
        )
    if used_types:
        imports += (
            f"from terminusdb_client.woql_type import {', '.join(sorted(used_types))}\n"
        )
    print_script += imports + body
    return print_script


def _sync(client, model_backend="template"):
    # all_existing_obj = client.get_all_documents(graph_type="schema")
    # all_obj_list = []
    # for obj in all_existing_obj:
    #     all_obj_list.append(obj)
    all_obj_list = client.get_all_documents(graph_type="schema", as_list=True)
    if len(all_obj_list) > 1:
        if model_backend == "pydantic":
            print_script = _create_pydantic_script(all_obj_list)
        else:
            print_script = _create_script(all_obj_list)
        print_script = shed(source_code=print_script)
        file = open("schema.py", "w")
        file.write(print_script)
        file.close()
        return f"schema.py is updated with {client.db} schema."
    else:
        return f"{client.db} schema is empty so schema.py has not be changed."


@click.command()
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["template", "pydantic"]),
    default=None,
    help="Model backend for the generated schema.py",
)
def sync(fmt):
    """Pull the current schema plan in database to schema.py"""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    backend = fmt or settings.get("model_backend") or "template"
    if fmt is not None and fmt != settings.get("model_backend"):
        with open("config.json") as fp:
            stored = json.load(fp)
        stored["model_backend"] = fmt
        with open("config.json", "w") as outfile:
            json.dump(stored, outfile, sort_keys=True, indent=4)
    client, msg = _connect(settings, new_db=False)
    click.echo(msg)
    click.echo(_sync(client, backend))


@click.command()
@click.option(
    "-m",
    "--message",
    help="Commit message for the commit",
)
def commit(message):
    """Push the current schema plan in schema.py to database."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    database = settings["database"]
    client, msg = _connect(settings)
    click.echo(msg)
    sys.path.append(os.getcwd())
    schema_plan = __import__("schema", globals(), locals(), [], 0)
    last_item = None
    documentation = {}
    if schema_plan.__doc__:
        for line in schema_plan.__doc__.split("\n"):
            if "Title:" in line:
                documentation["title"] = line[6:].strip()
                last_tiem = documentation["title"]
            elif "Description:" in line:
                documentation["description"] = line[12:].strip()
                last_tiem = documentation["description"]
            elif "Authors:" in line:
                documentation["authors"] = line[8:].strip()
                last_tiem = documentation["authors"]
            elif last_item is not None:
                last_item += "\n" + line.strip()
    authors = documentation.get("authors")
    if authors:
        authors = documentation["authors"].split(",")
        authors = [x.strip() for x in authors]
    schema_obj = WOQLSchema(
        title=documentation.get("title"),
        description=documentation.get("description"),
        authors=authors,
    )
    for obj_str in dir(schema_plan):
        obj = eval(f"schema_plan.{obj_str}")  # noqa: S307
        if isinstance(obj, (woqlschema.TerminusClass, enum.EnumMeta)):
            if obj_str not in ["DocumentTemplate", "EnumTemplate", "TaggedUnion"]:
                schema_obj.add_obj(obj.__name__, obj)
        elif _is_terminus_model(obj):
            schema_obj.add_obj(obj.__name__, obj)
    if message is None:
        message = "Schema updated by Python client."
    schema_obj.commit(client, commit_msg=message, full_replace=True)
    click.echo(f"{database} schema updated.")


def _is_terminus_model(obj):
    try:
        from ..schema.pydantic import TerminusModel
    except ImportError:
        return False
    return (
        isinstance(obj, type)
        and issubclass(obj, TerminusModel)
        and obj not in (TerminusModel,)
    )


@click.command()
@click.option(
    "--ignore-docs",
    is_flag=True,
    help="Ignore @documentation differences when comparing schemas",
)
def check(ignore_docs):
    """Diff schema.py against the database schema. Exit 1 on drift."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, msg = _connect(settings, new_db=False)
    click.echo(msg)
    sys.path.append(os.getcwd())
    try:
        schema_plan = __import__("schema", globals(), locals(), [], 0)
    except ModuleNotFoundError:
        click.echo("No schema.py found in the current directory.")
        raise SystemExit(2)
    schema_obj = WOQLSchema()
    found = False
    for obj_str in dir(schema_plan):
        obj = eval(f"schema_plan.{obj_str}")  # noqa: S307
        if isinstance(obj, (woqlschema.TerminusClass, enum.EnumMeta)):
            if obj_str not in ["DocumentTemplate", "EnumTemplate", "TaggedUnion"]:
                schema_obj.add_obj(obj.__name__, obj)
                found = True
        elif _is_terminus_model(obj):
            schema_obj.add_obj(obj.__name__, obj)
            found = True
    if not found:
        click.echo("No schema classes found in schema.py.")
        raise SystemExit(2)
    lines = schema_obj.diff(client, ignore_docs=ignore_docs)
    if lines:
        for line in lines:
            click.echo(line)
        raise SystemExit(1)
    click.echo("schema.py is in sync with the database schema.")


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
        status["ref"] = None
        with open(".TDB", "w") as outfile:
            json.dump(status, outfile)
        click.echo(f"{database} deleted.")


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
    help="Specify how to handle NAs: 'skip' will skip entries with NAs, 'optional' will make all properties optional in the database, 'error' will just throw an error if there's NAs",
)
@click.option(
    "--id", "id_", help="Specify column to be used as ids instead of generated ids"
)
@click.option("-e", "--embedded", multiple=True, help="Specify embedded columns")
@click.option(
    "-m",
    "--message",
    help="Commit message for the import",
)
@click.option(
    "--sep",
    default=",",
    show_default=True,
    help="Specify separator character in the CSV",
)
# @click.option('--header ', default=',', show_default=True)
def importcsv(
    csv_file, keys, class_name, chunksize, schema, na, id_, embedded, message, sep
):
    """Import CSV file into pandas DataFrame then into TerminusDB, with read_csv() options.
    Options like chunksize, sep etc"""
    # If chunksize is too small, pandas may decide certain column to be integer if all values in the 1st chunk are 0.0. This can be problmetic for some cases.
    na = na.lower()
    dtype = None
    if id_:
        dtype = {id_: "object"}
        id_ = id_.lower().replace(" ", "_")
    if keys:
        keys = [x.lower().replace(" ", "_") for x in keys]
    if embedded:
        for item in embedded:
            dtype[item] = "object"
        embedded = [x.lower().replace(" ", "_") for x in embedded]
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
    has_schema = not schema and class_name in client.get_existing_classes()

    def _df_to_schema(class_name, df):
        class_dict = {"@type": "Class", "@id": class_name}
        np_to_buildin = {
            v: getattr(builtins, k)
            for k, v in np.sctypeDict.items()
            if k in vars(builtins)
        }
        np_to_buildin[np.datetime64] = dt.datetime
        np_to_buildin[str] = str
        for col, dtype in dict(df.dtypes).items():
            if embedded and col in embedded:
                converted_type = class_name
            else:
                converted_type = np_to_buildin[dtype.type]
                if converted_type is object:
                    converted_type = str  # pandas treats all string as objects
                # Map pandas/numpy dtype to Python type
                # Uses dtype.kind for compatibility with numpy 2.0+ and pandas 3.0+
                dtype_kind = getattr(dtype, "kind", "O")
                if dtype.type is str or dtype_kind in ("U", "O", "S", "T"):
                    converted_type = str
                elif dtype_kind in ("i", "u"):
                    converted_type = int
                elif dtype_kind == "f":
                    converted_type = float
                elif dtype_kind == "b":
                    converted_type = bool
                elif dtype_kind == "M":
                    converted_type = dt.datetime
                elif dtype_kind == "m":
                    converted_type = dt.timedelta
                else:
                    converted_type = str
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

    with pd.read_csv(csv_file, sep=sep, chunksize=chunksize, dtype=dtype) as reader:
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
                if message is None:
                    schema_msg = f"Schema object insert/ update with {csv_file} by Python client."
                else:
                    schema_msg = message + " (schema update)"
                client.update_document(
                    class_dict,
                    commit_msg=schema_msg,
                    graph_type="schema",
                )
                click.echo(
                    f"\nSchema object {class_name} created with {csv_file} being imported into database."
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
                                "@id": class_name + "/" + str(value),
                            }
                    item.update(new_items)
                # adding type
                item["@type"] = class_name
                # adding ids
                if id_:
                    if id_ in item:
                        item_id = class_name + "/" + str(item[id_])
                    else:
                        raise RuntimeError(
                            f"id {id} is missing in {item}. Cannot import CSV."
                        )
                elif keys:
                    item_id = "_".join(list(keys))
                elif na == "optional":
                    item_id = None
                else:
                    item_id = "_".join(list(df.columns))
                if item_id:
                    item["@id"] = item_id
            if message is None:
                message = f"Documents created with {csv_file} update by Python client."
            client.update_document(
                obj_list,
                commit_msg=message,
            )
    if id_:
        key_type = "specified"
    elif na == "optional" and not keys:
        key_type = "Random"
    else:
        key_type = "Lexical"
    click.echo(
        f"Records in {csv_file} inserted as type {class_name} into database with {key_type} ids."
    )


@click.command()
@click.argument("class_obj")
@click.option(
    "--keepid",
    is_flag=True,
    help="If used, the id of the object and the other meta (@) is to be kept as is in the CSV",
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
    all_records = client.get_documents_by_type(class_obj)
    df = result_to_df(all_records, keepid, maxdep, client)
    if filename is None:
        filename = class_obj + ".csv"
    df.to_csv(filename, index=False)
    click.echo(
        f"CSV file {filename} created with {class_obj} from database {client.db}."
    )


@click.command()
@click.option(
    "-s", "--schema", is_flag=True, help="Specify if getting schema object instead"
)
@click.option("-t", "--type", "type_", help="Type of the objects to be getting back")
@click.option(
    "-q",
    "--query",
    multiple=True,
    help="Use query to filter out objects getting back. Need to be used with -t/--type",
)
@click.option(
    "-h", "--head", help="Show/ export only set number of documents max", type=int
)
@click.option(
    "-e",
    "--export",
    is_flag=True,
    help="Specify if the result to be export as CSV. Only usable when using –t/--type and not -s/-–schema",
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
def alldocs(schema, type_, query, head, export, keepid, maxdep, filename=None):
    """Get all documents in the database, use --schema to specify schema, --type to select type and -q to make queries (e.g. -q date=2021-07-01)

    If using --type and not --schema, can export using -e with options: --keepid, --maxdep and --filename
    """
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, msg = _connect(settings)
    if schema:
        if type_:
            click.echo(
                json.dumps(client.get_document(type_, graph_type="schema"), indent=4)
            )
        else:
            click.echo(
                json.dumps(
                    list(client.get_all_documents(graph_type="schema", count=head)),
                    indent=4,
                )
            )
    elif type_:
        if not query:
            result = list(client.get_documents_by_type(type_, count=head))
        else:
            schema_dict = client.get_document(type_, graph_type="schema")
            # check if it got inherited props
            combined = {}
            if "@inherits" in schema_dict:
                parents = schema_dict["@inherits"]
                if not isinstance(parents, list):
                    parents = [parents]
                for parent in parents:
                    parent_dict = client.get_document(parent, graph_type="schema")
                    combined.update(parent_dict)
            combined.update(schema_dict)

            query_dict = {"@type": type_}
            for item in query:
                pair = item.split("=")
                if combined.get(pair[0]) is None:
                    raise InterfaceError(f"{pair[0]} is not a proerty in {type_}")
                elif combined.get(pair[0]) == "xsd:integer":
                    pair[1] = int(pair[1].strip('"'))
                elif combined.get(pair[0]) == "xsd:decimal":
                    pair[1] = float(pair[1].strip('"'))
                elif combined.get(pair[0]) == "xsd:boolean":
                    pair[1] = pair[1].strip('"')
                    if pair[1].lower() == "false":
                        pair[1] = False
                    elif pair[1].lower() == "true":
                        pair[1] = True
                    else:
                        raise InterfaceError(f"{pair[1]} cannot be parse as boolean")
                else:
                    pair[1] = pair[1]  # don't quote in query
                query_dict[pair[0]] = pair[1]
            result = list(client.query_document(query_dict, optimize=True, count=head))
        if export:
            df = result_to_df(result, keepid, maxdep, client)
            if filename is None:
                filename = type_ + ".csv"
            df.to_csv(filename, index=False)
            click.echo(
                f"CSV file {filename} created with {type_} from database {client.db}."
            )
        else:
            click.echo(json.dumps(result, indent=4))
    else:
        click.echo(json.dumps(list(client.get_all_documents(count=head)), indent=4))


@click.command()
@click.argument("branch_name", required=False)
@click.option(
    "-d",
    "--delete",
    multiple=True,
    help="Branch(es) to be deleted",
)
def branch(branch_name, delete):
    """Create or list branch."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    if delete:
        all_branches = client.get_all_branches()
        all_branches = [item["name"] for item in all_branches]
        for delete_branch in delete:
            if delete_branch in all_branches:
                if delete_branch != status["branch"]:
                    client.delete_branch(delete_branch)
                    click.echo(
                        f"Branch '{delete_branch}' deleted. Remain on '{status['branch']}' branch."
                    )
                else:
                    raise InterfaceError(
                        f"Cannot delete {delete_branch} which is current branch, please checkout to another branch first."
                    )
            else:
                raise InterfaceError(f"{delete_branch} does not exist.")
    else:
        if branch_name is None:
            all_branches = client.get_all_branches()
            all_branches = [item["name"] for item in all_branches]
            new_all_branches = []
            for each_branch in all_branches:
                if each_branch == status["branch"]:
                    new_all_branches.append("* " + each_branch)
                else:
                    new_all_branches.append("  " + each_branch)
            click.echo("\n".join(new_all_branches))
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
    all_branches = [item["name"] for item in all_branches]
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
@click.argument("branch_name")
def rebase(branch_name):
    """Reapply commits on top of another base tip on another branch."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    client.rebase(branch=branch_name)
    click.echo(f"Rebased {branch_name} branch.")


def _status(settings):
    message = f"Connecting to '{settings['database']}' at '{settings['endpoint']}'\non branch '{settings['branch']}'"
    if settings.get("team"):
        message += f"\nwith team '{settings['team']}'"
    if settings.get("ref"):
        message += f"\nat commit '{settings['ref']}'"
    return message


@click.command()
def status():
    """Show the working status of the project."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    click.echo(_status(settings))


@click.command()
def log():
    """Show commit log of the project."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    history = client.get_commit_history()
    click.echo("========")
    click.echo(_status(settings))
    click.echo("========\n")
    for item in history:
        click.echo(f"commit {item['commit']}")
        click.echo(f"Author: {item['author']}")
        click.echo(f"Date: {str(item['timestamp'])}")
        click.echo(f"\n    {item['message']}\n")


@click.command()
@click.argument("commit", required=False)
@click.option(
    "--soft",
    is_flag=True,
    help="Soft reset (referencing that commit) instead of hard reset (default, reset the state of the commit for the database, not reversible)",
)
def reset(commit, soft):
    """Reset the head of the commit to a certain commit with id as input. Default to be a hard reset (newer commit will be wipped, not reversible). If no commit is is provided, it will reset to the newest commit."""
    settings = _load_settings()
    status = _load_settings(".TDB", check=[])
    settings.update(status)
    client, _ = _connect(settings)
    if commit is None:
        status["ref"] = None
        with open(".TDB", "w") as outfile:
            json.dump(status, outfile)
        click.echo("Reset head to newest commit")
    elif soft:
        commit_ids = [item["commit"] for item in client.get_commit_history()]
        if commit not in commit_ids:
            raise InterfaceError(f"{commit} is not a commit in {client.db}.'")
        status["ref"] = commit
        with open(".TDB", "w") as outfile:
            json.dump(status, outfile)
        click.echo(f"Soft reset to commit {commit}")
    else:
        client.reset(commit)
        click.echo(f"Hard reset to commit {commit}")


@click.command()
@click.argument("set_config", required=False, nargs=-1)
@click.option(
    "-d",
    "--delete",
    multiple=True,
    help="Keys of items in the config.json to be deleted",
)
def config(set_config, delete):
    """Show or set config.json of the project. To set a config, use <key>=<value>, e.g. streams=MyClass or streams=[Class1, Class2]"""
    settings = _load_settings()

    def try_parsing(value):
        try:
            value = float(value)
        except BaseException:
            pass
        try:
            value = int(value)
        except BaseException:
            pass
        return value

    if not set_config and not delete:
        click.echo("Current config:")
        for key, value in settings.items():
            click.echo(f"{key}={value}")
    else:
        for item in set_config:
            key = item.split("=")[0]
            value = item.split("=")[1]
            if value[0] == "[" and value[-1] == "]":  # it's a list
                value = value.strip("[]").split(",")
                value = [try_parsing(x.strip()) for x in value]
            else:
                value = try_parsing(value)
            settings.update({key: value})
        for item in delete:
            settings.pop(item, None)
        with open("config.json", "w") as outfile:
            json.dump(settings, outfile, sort_keys=True, indent=4)
        click.echo("config.json updated")


tdbpy.add_command(startproject)
tdbpy.add_command(sync)
tdbpy.add_command(commit)
tdbpy.add_command(check)
tdbpy.add_command(deletedb)
tdbpy.add_command(importcsv)
tdbpy.add_command(exportcsv)
tdbpy.add_command(alldocs)
tdbpy.add_command(branch)
tdbpy.add_command(checkout)
tdbpy.add_command(rebase)
tdbpy.add_command(status)
tdbpy.add_command(log)
tdbpy.add_command(reset)
tdbpy.add_command(config)
