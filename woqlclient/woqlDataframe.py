# woqlDataframe.py
import numpy as np
import pandas as pd
import re

class EmptyException(Exception):
    pass

def _get_var_name(uri):
    (_,var_name) = re.split('^http://terminusdb.com/woql/variable/', uri, maxsplit=1)
    return var_name

def _is_empty(query):
    return len(query['bindings']) == 0

def extract_header(query):
    """Extracts the header of the returned result table"""
    header = []
    if _is_empty(query):
        raise EmptyException('Query is empty')

    bindings = query['bindings'][0]
    for k, v in bindings.items():
        name = _get_var_name(k)
        if type(v) == dict and ('@type' in v):
            ty = v['@type']
        else:
            ty = 'http://www.w3.org/2001/XMLSchema#string'
        header.append((name,ty))
    return header

def extract_column(query,name,ty):
    """Extracts the column of the returned result table"""
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
    convert_mapping = {'http://www.w3.org/2001/XMLSchema#string': np.unicode_,
    'http://www.w3.org/2001/XMLSchema#integer': np.int,
    'http://www.w3.org/2001/XMLSchema#dateTime': np.datetime64,
    'http://www.w3.org/2001/XMLSchema#decimal': np.double,
    }
    if ty_rdf in convert_mapping:
        return convert_mapping[ty_rdf]
    else:
        raise Exception("Unknown rdf type! "+ty_rdf)

def type_value_map(ty_rdf,value):
    "Converts valuen of different types between RDF and dataframe"
    if ty_rdf == 'http://www.w3.org/2001/XMLSchema#string':
        return value
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#integer':
        return int(value)
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#dateTime':
        return np.datetime64(value)
    elif ty_rdf == 'http://www.w3.org/2001/XMLSchema#decimal':
        return float(value)
    else:
        raise Exception("Unknown rdf type! "+ty_rdf)

def query_to_df(query):
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
