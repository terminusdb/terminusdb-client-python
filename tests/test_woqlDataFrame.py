import pytest
#import unittest.mock as mock
#from woqlclient import WOQLQuery
#from woqlclient import WOQLClient
import woqlclient as woql
from woqlclient.woqlDataframe import EmptyException
#import woqlClient as woql
import numpy as np

MOCK_RESULT = {'bindings': [{'http://terminusdb.com/woql/variable/Product': {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    '@value': 'STRAWBERRY CANDY'},
   'http://terminusdb.com/woql/variable/Qty': {'@type': 'http://www.w3.org/2001/XMLSchema#decimal',
    '@value': 10},
   'http://terminusdb.com/woql/variable/Stock': 'http://195.201.12.87:6365/rational_warehouse/document/Stock110_101752_2019-12-22T00%3A00%3A00',
   'http://terminusdb.com/woql/variable/Warehouse': {'@language': 'en',
    '@value': 'Pittsburg'},
   'http://terminusdb.com/woql/variable/buyers_buy_product': 'http://195.201.12.87:6365/rational_warehouse/document/Product101752',
   'http://terminusdb.com/woql/variable/stockDate': {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
    '@value': '2019-12-22T00:00:00'},
   'http://terminusdb.com/woql/variable/warehouseCode': 'http://195.201.12.87:6365/rational_warehouse/document/Warehouse110'},
], "graphs": []}

TEST_TYPE=[('http://www.w3.org/2001/XMLSchema#string', np.unicode_),
('http://www.w3.org/2001/XMLSchema#integer', np.int),
('http://www.w3.org/2001/XMLSchema#dateTime', np.datetime64),
('http://www.w3.org/2001/XMLSchema#decimal', np.double),
]

TEST_TYPE_VALUE=[('http://www.w3.org/2001/XMLSchema#string', '10',  '10'),
('http://www.w3.org/2001/XMLSchema#integer', '10', 10),
('http://www.w3.org/2001/XMLSchema#dateTime', '2019-12-22T00:00:00', np.datetime64('2019-12-22T00:00:00')),
('http://www.w3.org/2001/XMLSchema#decimal', '10.10', 10.1),
]

class TestWoqlDataFrame:

    def test_extract_header_method(self):
        df_header = woql.extract_header(MOCK_RESULT)
        assert df_header == [('Product', 'http://www.w3.org/2001/XMLSchema#string'), ('Qty', 'http://www.w3.org/2001/XMLSchema#decimal'), ('Stock', 'http://www.w3.org/2001/XMLSchema#string'), ('Warehouse', 'http://www.w3.org/2001/XMLSchema#string'), ('buyers_buy_product', 'http://www.w3.org/2001/XMLSchema#string'), ('stockDate', 'http://www.w3.org/2001/XMLSchema#dateTime'), ('warehouseCode', 'http://www.w3.org/2001/XMLSchema#string')]

    def test_extract_header_method_empty(self):
        with pytest.raises(EmptyException):
            df_header = woql.extract_header({'bindings': []})

    def test_extract_column_method(self):
        df_column = woql.extract_column(MOCK_RESULT, 'Product',
        'http://www.w3.org/2001/XMLSchema#string')
        assert df_column == ['STRAWBERRY CANDY']

    @pytest.mark.parametrize("data_type,expected", TEST_TYPE)
    def test_type_map_method(self, data_type, expected):
        assert woql.type_map(data_type) == expected

    def test_type_map_method_unknown(self):
        with pytest.raises(Exception, match=r"Unknown rdf type! .*"):
            woql.type_map("some type that cause error")

    @pytest.mark.parametrize("data_type, value, expected", TEST_TYPE_VALUE)
    def test_type_value_map_method(self, data_type, value, expected):
        assert woql.type_value_map(data_type, value) == expected

    def test_type_value_map_method_unknown(self):
        with pytest.raises(Exception, match=r"Unknown rdf type! .*"):
            woql.type_value_map("some type that cause error","some val")

    def test_query_to_df_method(self):
        df = woql.query_to_df(MOCK_RESULT)
        assert df.shape == (1,7)
