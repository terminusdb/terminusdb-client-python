# import pytest
#
# from terminusdb_client.errors import DatabaseError
# from terminusdb_client.woqlclient.woqlClient import WOQLClient
# from terminusdb_client.woqlquery.woql_query import WOQLQuery
#
#
# def test_bank_tutorial(docker_url):
#
#     user = "admin"
#     account = "admin"
#     key = "root"
#     dbid = "bank_balance_example"
#     repository = "local"
#     label = "Bank Balance Example"
#     description = "An example database for playing with bank accounts"
#
#     client = WOQLClient(docker_url)
#     client.connect(user=user, account=account, key=key)
#     client.create_database(dbid, user, label=label, description=description)
#
#     # Add the schema (there is no harm in adding repeatedly as it is idempotent)
#     WOQLQuery().woql_and(
#         WOQLQuery()
#         .doctype("scm:BankAccount")
#         .label("Bank Account")
#         .description("A bank account")
#         .property("scm:owner", "xsd:string")
#         .label("owner")
#         .cardinality(1)
#         .property("scm:balance", "xsd:nonNegativeInteger")
#         .label("owner")
#     ).execute(client, "Adding bank account object to schema")
#
#     # Fix bug in schema
#     WOQLQuery().woql_and(
#         WOQLQuery().delete_quad("scm:balance", "label", "owner", "schema"),
#         WOQLQuery().add_quad("scm:balance", "label", "balance", "schema"),
#     ).execute(client, "Label for balance was wrong")
#
#     # Add the data from csv to the main branch (again idempotent as widget ids are chosen from sku)
#     WOQLQuery().woql_and(
#         WOQLQuery()
#         .insert("doc:mike", "scm:BankAccount")
#         .property("scm:owner", "mike")
#         .property("scm:balance", 123)
#     ).execute(client, "Add mike")
#
#     # try to make mike go below zero
#     balance, new_balance = WOQLQuery().vars("Balance", "New Balance")
#     with pytest.raises(DatabaseError):
#         WOQLQuery().woql_and(
#             WOQLQuery().triple("doc:mike", "scm:balance", balance),
#             WOQLQuery().delete_triple("doc:mike", "scm:balance", balance),
#             WOQLQuery().eval(WOQLQuery().minus(balance, 130), new_balance),
#             WOQLQuery().add_triple("doc:mike", "scm:balance", new_balance),
#         ).execute(client, "Update mike")
#
#     # Subtract less
#     WOQLQuery().woql_and(
#         WOQLQuery().triple("doc:mike", "scm:balance", balance),
#         WOQLQuery().delete_triple("doc:mike", "scm:balance", balance),
#         WOQLQuery().eval(WOQLQuery().minus(balance, 110), new_balance),
#         WOQLQuery().add_triple("doc:mike", "scm:balance", new_balance),
#     ).execute(client, "Update mike")
#
#     # Make the "branch_office" branch
#     branch = "branch_office"
#     client.branch(branch)
#
#     # Add some data to the branch
#     client.checkout(branch)
#     WOQLQuery().woql_and(
#         WOQLQuery()
#         .insert("doc:jim", "scm:BankAccount")
#         .property("owner", "jim")
#         .property("balance", 8)
#     ).execute(client, "Adding Jim")
#
#     # Return to the 'main' branch and add Jane
#     client.checkout("main")
#     WOQLQuery().woql_and(
#         WOQLQuery()
#         .insert("doc:jane", "scm:BankAccount")
#         .property("owner", "jane")
#         .property("balance", 887)
#     ).execute(client, "Adding Jane")
#
#     client.rebase(
#         rebase_source=f"{user}/{dbid}/{repository}/branch/{branch}",
#         author=user,
#         message="Merging jim in from branch_office",
#     )
#     result = WOQLQuery().triple("doc:jim", "scm:balance", 8).execute(client)
#     assert (
#         len(result.get("bindings")) == 1
#     )  # if jim is there, the length of the binding should be 1, if not it will be 0
