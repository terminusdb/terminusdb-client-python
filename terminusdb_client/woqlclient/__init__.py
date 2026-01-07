import sys  # noqa
from ..client import GraphType, Patch, Client  # noqa

WOQLClient = Client
sys.modules["terminusdb_client.woqlclient.woqlClient"] = Client  # noqa
