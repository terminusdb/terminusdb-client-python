"""
    woqlClient Library
    ~~~~~~~~~~~~~~~~~~~~~

"""
import warnings
from .woqlClient import *
from .woql import WOQLQuery
from .__version__ import __version__

try:
    from .woqlDataframe import *
except ImportError:
    msg = (
        "woqlDataframe requirements are not installed.\n\n"
        "If you want to use woqlDataframe, please pip install as follows:\n\n"
        "  python -m pip install -U terminus-client-python[dataframe]"
    )
    warnings.warn(msg)

__all__ = ['woqlClient', 'woql', 'woqlDataframe']

name = "woqlclient"
#__version__ = "0.0.4"
# cmdclass = {'test': PyTest}
