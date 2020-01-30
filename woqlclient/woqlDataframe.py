import woqlclient.woqlClient as woql
from woqlclient import WOQLQuery
import numpy as np
import pandas as pd
import re

def get_var_name(uri):
    (_,var_name) = re.split('^http://terminusdb.com/woql/variable/', uri, maxsplit=1)
    return var_name

def is_empty(query):
    return len(query['bindings']) == 0

def extract_header(query):
    header = []
    if is_empty(query):
        raise Exception('Query is empty')

    bindings = query['bindings'][0]
    for k, v in bindings.items():
        name = get_var_name(k)
        if isinstance(v,dict):
            ty = v['@type']
        else:
            ty = 'http://www.w3.org/2001/XMLSchema#string'
        header.append((name,ty))
    return header

def extract_column(query,name,ty):
    bindings = query['bindings']
    column = []
    for binding in bindings:
        for k,v in binding.items():
            if k == ('http://terminusdb.com/woql/variable/' + name):
                if isinstance(v,dict):
                    value = type_value_map(ty,v['@value'])
                else:
                    value = type_value_map(ty,v)
                column.append(value)
    return column

def type_map(ty_rdf):
    "Converts types between RDF and dataframe"
    if ty_rdf == 'http://www.w3.org/2001/XMLSchema#string':
        return np.unicode_
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#integer':
        return np.int
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#dateTime':
        return np.datetime64
    else:
        raise Exception("Unknown rdf type! "+ty_rdf)

def type_value_map(ty_rdf,value):
    if ty_rdf == 'http://www.w3.org/2001/XMLSchema#string':
        return value
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#integer':
        return int(value)
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#dateTime':
        return numpy.datetime64(value)
    else:
        raise Exception("Unknown rdf type! "+ty_rdf)

def query_to_dt(query):
    """Convert a query to a data frame.
       This only works for homogeneous query results!"""
    header = extract_header(query)
    dtypes = {}
    column_names = []
    for name,rdftype in header:
        column_names.append(name)
        dtype = type_map(rdftype)
        dtypes[name] = dtype

    dataframe = pd.DataFrame(columns=column_names)
    dataframe.astype(dtypes)

    for name,rdftype in header:
        column = extract_column(query,name,rdftype)
        dataframe[name] = column

    return dataframe
