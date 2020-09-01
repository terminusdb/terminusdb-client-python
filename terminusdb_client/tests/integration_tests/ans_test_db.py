import pytest


@pytest.fixture(scope="module")
def one_class_obj():
    return {'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': ['Parents', 'Description', 'Class Name', 'Class ID', 'Children', 'Abstract'], 'bindings': [{'Abstract': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': 'No'}, 'Children': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': ''}, 'Class ID': 'terminusdb:///schema#Station', 'Class Name': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': 'Station Object'}, 'Description': {'@type': 'http://www.w3.org/2001/XMLSchema#string', '@value': 'A bike station object.'}, 'Parents': [['http://terminusdb.com/schema/system#Document']]}], 'deletes': 0, 'inserts': 0, 'transaction_retry_count': 0}
