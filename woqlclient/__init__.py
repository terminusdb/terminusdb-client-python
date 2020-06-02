"""
    woqlClient Library
    ~~~~~~~~~~~~~~~~~~~~~

"""
import warnings

#from .woql_query import *
#from .woql import *
from .woqlClient import *

try:
    from .woqlDataframe import *
except ImportError:
    msg = (
        "woqlDataframe requirements are not installed.\n\n"
        "If you want to use woqlDataframe, please pip install as follows:\n\n"
        "  python -m pip install -U terminus-client-python[dataframe]"
    )
    warnings.warn(msg)

__all__ = ["woqlClient", "woql", "woqlDataframe"]

name = "woqlclient"
# __version__ = "0.0.4"
# cmdclass = {'test': PyTest}
