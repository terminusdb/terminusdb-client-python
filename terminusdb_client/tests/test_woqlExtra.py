from ..woqlquery.woql_query import WOQLQuery
from .woqljson.woqlExtraJson import WoqlExtra
import pprint
pp = pprint.PrettyPrinter(indent=4)


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
        woql_object = WOQLQuery()
        woql_object.woql_and(
            WOQLQuery().using(
                "admin/dbName/local/commit/commitID_1", WOQLQuery().triple("v:A", "v:B", "v:C")
            ),
            WOQLQuery().using(
                "admin/dbName/local/commit/commitID_2",
                WOQLQuery().woql_not(WOQLQuery().triple("v:A", "v:B", "v:C")),
            ),
        )
        pp.pprint(woql_object.to_dict())
        print("___XXX___")
        pp.pprint( WoqlExtra["multiUsingJson"])
        assert woql_object.to_dict() == WoqlExtra["multiUsingJson"]

    def test_chain_and(self):
        woql_query = WOQLQuery()
        woql_query.woql_and(
            WOQLQuery().triple("v:A", "v:B", "v:C"), WOQLQuery().triple("v:D", "v:E", "v:F")
        )
        assert woql_query.to_dict() == WoqlExtra["chainAndJson"]
