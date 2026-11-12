import sys  # noqa
from ..schema import *  # noqa

WOQLSchema = Schema  # noqa
sys.modules["terminusdb_client.woqlschema.woql_schema"] = schema  # noqa
del schema  # noqa  keep the terminusdb_client.schema package importable
