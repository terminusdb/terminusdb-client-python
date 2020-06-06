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
        assert woqlObject.to_dict() == WoqlExtra["usingJson"]
        assert woqlObject01.to_dict() == WoqlExtra["usingJson"]

    def test_multi_using(self):
        woql = WOQLQuery()
        woql_object = woql.woql_and(
            woql.using(
                "admin/dbName/local/commit/commitID_1", woql.triple("v:A", "v:B", "v:C")
            ),
            woql.using(
                "admin/dbName/local/commit/commitID_2",
                woql.woql_not(woql.triple("v:A", "v:B", "v:C")),
            ),
        )
        assert woql_object == WoqlExtra["multiUsingJson"]

    def test_chain_and(self):
        woql = WOQLQuery()
        woql_query = woql.woql_and(
            woql.triple("v:A", "v:B", "v:C"), woql.triple("v:D", "v:E", "v:F")
        )
        assert woql_query.to_dict() == WoqlExtra["chainAndJson"]
