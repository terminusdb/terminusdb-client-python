from .woqljson.woqlExtraJson import *
from ..woqlquery.woql_query import WOQLQuery

class TestWoqlExtra:
    def test_using(self):
        woqlObject = WOQLQuery().using("userName/dbName/local/commit/commitID",
                                     WOQLQuery().triple("v:A", "v:B", "v:C"))
        woqlTriple = WOQLQuery().triple("v:A", "v:B", "v:C")
        woqlObject01 = WOQLQuery().using("userName/dbName/local/commit/commitID",woqlTriple)
        assert woqlObject.json() == woqlExtra['usingJson']
        assert woqlObject01.json() == woqlExtra['usingJson']
