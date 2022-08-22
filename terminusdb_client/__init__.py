from .client import Patch, Client  # noqa
from .woqldataframe import woqlDataframe as WOQLDataFrame  # noqa
from .woqlquery import WOQLQuery  # noqa
from .woqlschema import *  # noqa
# Backwards compatibility
WOQLClient = Client # noqa
WOQLSchema = Schema # noqa
