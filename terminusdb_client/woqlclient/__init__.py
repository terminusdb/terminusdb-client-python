import sys # noqa
from ..client import Patch, Client  # noqa
WOQLClient = Client
sys.modules["terminusdb_client.woqlclient.woqlClient"] = Client # noqa
