# from terminusdb_client.woqlquery.woql_schema import (
#     Document,
#     Enums,
#     Property,
#     WOQLObject,
#     WOQLSchema,
# )
#
# my_schema = WOQLSchema()
#
#
# class MyEmployee(Document):
#     schema = my_schema
#
# # def test_test():
# #     import pdb; pdb.set_trace()
# #     # assert MyEmployee.properties == {MyAddressOf}
# #     assert False
#
# class MyAddress(WOQLObject):
#     schema = my_schema
#
#
# class MyTeam(Enums):
#     """This is Team"""
#
#     value_set = {"IT", "Marketing"}
#     schema = my_schema
#
#
# class MyAddressOf(Property):
#     domain = MyEmployee
#     prop_range = MyAddress
#     schema = my_schema
#
#
# def test_schema_construct():
#     assert my_schema.all_obj() == {MyEmployee, MyAddress, MyTeam}
#     assert my_schema.all_prop() == {MyAddressOf}
#     assert MyEmployee.properties == {MyAddressOf}
#
#
# def test_schema_copy():
#     copy_schema = my_schema.copy()
#     assert copy_schema.all_obj() == {MyEmployee, MyAddress, MyTeam}
#     assert copy_schema.all_prop() == {MyAddressOf}
