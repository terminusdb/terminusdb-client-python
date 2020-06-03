from ..woqlquery.woql_query import WOQLQuery
from .woqljson.woqlExtraJson import WoqlExtra


class TestWoqlExtra:
    def test_using(self):
        woqlObject = WOQLQuery().using(
            "userName/dbName/local/commit/commitID",
            WOQLQuery().triple("v:A", "v:B", "v:C"),
        )
        woqlTriple = WOQLQuery().triple("v:A", "v:B", "v:C")
        woqlObject01 = WOQLQuery().using(
            "userName/dbName/local/commit/commitID", woqlTriple
        )
        assert woqlObject.json() == WoqlExtra["usingJson"]
        assert woqlObject01.json() == WoqlExtra["usingJson"]
