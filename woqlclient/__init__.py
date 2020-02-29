"""
    woqlClient Library
    ~~~~~~~~~~~~~~~~~~~~~

"""
from .woqlClient import *
from .woql import WOQLQuery
from .woqlDataframe import *
from .__version__ import __version__

__all__ = ['woqlClient', 'woql', 'woqlDataframe']

name = "woqlclient"
#__version__ = "0.0.4"
# cmdclass = {'test': PyTest}
