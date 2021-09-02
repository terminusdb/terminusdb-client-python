# import csv
# import filecmp
import os

from terminusdb_client.woqlclient.woqlClient import WOQLClient
from terminusdb_client.woqlquery.woql_query import WOQLQuery

# from terminusdb_client.woqlquery.woql_query import WOQLQuery


def test_happy_path(docker_url):
    # create client
    client = WOQLClient(docker_url)
    assert not client._connected
    # test connect
    client.connect()
    assert client._connected
    # test create db
    client.create_database("test_happy_path", prefixes={"doc": "foo://"})
    init_commit = client._get_current_commit()
    assert client.db == "test_happy_path"
    assert "test_happy_path" in client.list_databases()
    # assert client._context.get("doc") == "foo://"
    assert len(client.get_commit_history()) == 1
    # test adding something
    client.query(WOQLQuery().add_quad("a", "rdf:type", "sys:Class", "schema"))
    first_commit = client._get_current_commit()
    assert first_commit != init_commit
    assert len(client.get_commit_history()) == 1
    client.query(WOQLQuery().add_quad("b", "rdf:type", "sys:Class", "schema"))
    commit_history = client.get_commit_history()
    assert client._get_target_commit(1) == first_commit
    assert len(client.get_commit_history()) == 2
    # test reset
    client.reset(commit_history[-1]["commit"])
    assert client._get_current_commit() == first_commit
    client.delete_database("test_happy_path", "admin")
    assert client.db is None
    assert "test_happy_path" not in client.list_databases()


def test_jwt(docker_url_jwt):
    # create client
    client = WOQLClient(docker_url_jwt)
    os.environ["TERMINUSDB_ACCESS_TOKEN"] = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InRlc3RrZXkifQ.eyJodHRwOi8vdGVybWludXNkYi5jb20vc2NoZW1hL3N5c3RlbSNhZ2VudF9uYW1lIjoiYWRtaW4iLCJodHRwOi8vdGVybWludXNkYi5jb20vc2NoZW1hL3N5c3RlbSN1c2VyX2lkZW50aWZpZXIiOiJhZG1pbkB1c2VyLmNvbSIsImlzcyI6Imh0dHBzOi8vdGVybWludXNodWIuZXUuYXV0aDAuY29tLyIsInN1YiI6ImFkbWluIiwiYXVkIjpbImh0dHBzOi8vdGVybWludXNodWIvcmVnaXN0ZXJVc2VyIiwiaHR0cHM6Ly90ZXJtaW51c2h1Yi5ldS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTkzNzY5MTgzLCJhenAiOiJNSkpuZEdwMHpVZE03bzNQT1RRUG1SSkltWTJobzBhaSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.Ru03Bi6vSIQ57bC41n6fClSdxlb61m0xX6Q34Yh91gql0_CyfYRWTuqzqPMFoCefe53hPC5E-eoSFdID_u6w1ih_pH-lTTqus9OWgi07Qou3QNs8UZBLiM4pgLqcBKs0N058jfg4y6h9GjIBGVhX9Ni2ez3JGNcz1_U45BhnreE"
    assert not client._connected
    # test connect
    client.connect(
        use_token=True
    )
    assert client._connected
    # test create db
    client.create_database("test_happy_path", prefixes={"doc": "foo://"})
    assert client.db == "test_happy_path"
    assert "test_happy_path" in client.list_databases()
    client.delete_database("test_happy_path", "admin")
    assert client.db is None
    assert "test_happy_path" not in client.list_databases()


def test_terminusx():
    os.environ["TERMINUSDB_ACCESS_TOKEN"] = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkpXUjBIOXYyeTFORUdaZXlodUM0aCJ9.eyJodHRwOi8vdGVybWludXNkYi5jb20vc2NoZW1hL3N5c3RlbSNhZ2VudF9uYW1lIjoiYXV0aDB8NjEyM2MwODYwZTI0NWEwMDZhMjg0YTM3IiwiaXNzIjoiaHR0cHM6Ly90ZXJtaW51cy1jbG91ZC1kZXYuZXUuYXV0aDAuY29tLyIsInN1YiI6Iko0NWpKNmVYTDM4M3NXVU1ueFJNelJJMktsUFRnRnlKQGNsaWVudHMiLCJhdWQiOiJodHRwczovL3Rlcm1pbnVzY2xvdWQvYXBpX3Rva2VucyIsImlhdCI6MTYyOTczMzE3OCwiZXhwIjoxNjMyMzI1MTc4LCJhenAiOiJKNDVqSjZlWEwzODNzV1VNbnhSTXpSSTJLbFBUZ0Z5SiIsImd0eSI6ImNsaWVudC1jcmVkZW50aWFscyJ9.d7BvjSOxZz5yysdm8cUD6TQFqgp86ZJqoPQze_ODodHeZDfHB38y3l0w_AkK2pdewcNOiygRidyO5WKYtoSQrbUPmpQEplXh1GbGCP1IMK3D1YuRN6EfRwVGa0gPQZoNsmlTCI8XeUGiSBX9lap23aOIhwZ0UzggDZFsoyHbul1F_gMV8d5WL49NjEq_I_FyRdLIFeTSlf-zWACNIVrOBXlR5Ea0mmDqaOUbHT9c5zWmuWB8RXCWj-H6IvZYUB_9O27DXgWTS40RbI_rY8su_DRb10sfsB9VMF6YcpUzWQWl8Cjjm0_O-tqzAxIpP981ilGko3WsHbnsARMxM65CmA"
    endpoint = "https://cloud-dev.dcm.ist/ubf40420team/"

    client = WOQLClient(endpoint)
    client.connect(use_token=True)


#
# def _generate_csv(option):
#     if option == 1:
#         file_path = "employee_file.csv"
#         with open(file_path, mode="w") as employee_file:
#             employee_writer = csv.writer(
#                 employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
#             )
#             employee_writer.writerow(["John Smith", "Accounting", "November"])
#             employee_writer.writerow(["Erica Meyers", "IT", "March"])
#         return file_path
#     else:
#         file_path = "employee_file.csv"
#         with open(file_path, mode="w") as employee_file:
#             employee_writer = csv.writer(
#                 employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
#             )
#             employee_writer.writerow(["Cow Duck", "Marketing", "April"])
#         return file_path
#
#
# def _file_clean_up(filename):
#     if os.path.exists(filename):
#         os.remove(filename)
#
#
# def test_csv_handeling(docker_url):
#     client = WOQLClient(docker_url)
#     assert not client._connected
#     # test connect
#     client.connect()
#     assert client._connected
#     # test create db
#     client.create_database("test_csv")
#     client._get_current_commit()
#     assert client._db == "test_csv"
#     assert "test_csv" in client.list_databases()
#     csv_file_path = _generate_csv(1)  # create testing csv
#     try:
#         client.insert_csv(csv_file_path)
#         client.get_csv(csv_file_path, csv_output_name="new_" + csv_file_path)
#         assert filecmp.cmp(csv_file_path, "new_" + csv_file_path)
#         csv_file_path = _generate_csv(2)
#         client.update_csv(csv_file_path)
#         client.get_csv(csv_file_path, csv_output_name="update_" + csv_file_path)
#         assert not filecmp.cmp("new_" + csv_file_path, "update_" + csv_file_path)
#     finally:
#         _file_clean_up(csv_file_path)
#         _file_clean_up("new_" + csv_file_path)
#         _file_clean_up("update_" + csv_file_path)
#

# def test_create_graph(docker_url):
#     client = WOQLClient(docker_url)
#     assert not client._connected
#     # test connect
#     client.connect()
#     assert client._connected
#     # test create db
#     client.create_database("test_graph")
#     client.create_graph("instance", "test-one-more-graph", "create test graph")
#     client.delete_graph("instance", "test-one-more-graph", "delete test graph")
