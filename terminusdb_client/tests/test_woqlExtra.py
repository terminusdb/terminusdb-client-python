# import pprint

from terminusdb_client.woqlquery.woql_query import WOQLQuery

from .woqljson.woqlExtraJson import WoqlExtra

# pp = pprint.PrettyPrinter(indent=4)


class TestWoqlExtra:
    def test_using(self):
        woql_object = WOQLQuery().using(
            "userName/dbName/local/commit/commitID",
            WOQLQuery().triple("v:A", "v:B", "v:C"),
        )
        woql_triple = WOQLQuery().triple("v:A", "v:B", "v:C")
        woql_object01 = WOQLQuery().using(
            "userName/dbName/local/commit/commitID", woql_triple
        )
        assert woql_object.to_dict() == WoqlExtra["usingJson"]
        assert woql_object01.to_dict() == WoqlExtra["usingJson"]

    def test_multi_using(self):
        woql_object = WOQLQuery()
        woql_object.woql_and(
            WOQLQuery().using(
                "admin/dbName/local/commit/commitID_1",
                WOQLQuery().triple("v:A", "v:B", "v:C"),
            ),
            WOQLQuery().using(
                "admin/dbName/local/commit/commitID_2",
                WOQLQuery().woql_not(WOQLQuery().triple("v:A", "v:B", "v:C")),
            ),
        )
        assert woql_object.to_dict() == WoqlExtra["multiUsingJson"]

    def test_chain_and(self):
        woql_query = WOQLQuery()
        woql_query.woql_and(
            WOQLQuery().triple("v:A", "v:B", "v:C"),
            WOQLQuery().triple("v:D", "v:E", "v:F"),
        )
        assert woql_query.to_dict() == WoqlExtra["chainAndJson"]
