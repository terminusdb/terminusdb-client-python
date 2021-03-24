# woqlDataframe.py

import warnings
from importlib import import_module


def _import_needed(package):
    try:
        module = import_module(package)
        return module
    except ImportError:
        msg = (
            "woqlDataframe requirements are not installed.\n\n"
            "If you want to use woqlDataframe, please pip install as follows:\n\n"
            "  python -m pip install -U terminus-client-python[dataframe]"
        )
        raise ImportError(msg)


class EmptyException(Exception):
    """Exception inherited from the built-in Exception Class

    Parameters
    ----------
    msg : str
        Error message that is describing the exception

    Raises
    ------
    EmptyException
        If the result table of the query is empty

    """


def _is_empty(query):
    """Checks if the result table of a query is empty

    Parameters
    ----------
    query : dict
            JSON of the result of the query

    Returns
    -------
    bool
        TRUE if the result table is empty, else FALSE

    """
    return len(query["bindings"]) == 0


def extract_header(query):
    """Extracts the header of the returned result table

    Extrace the result of the query binding, including the header name and their WOQL rdf data type.

    Parameters
    ----------
    query : dict
            JSON of the result of the query

    Returns
    -------
    list
        List of tuples, each tuple will have the name of the column as the 1st element an the WOQL rdf data type of that column as the 2nd element.

    Examples
    --------
    >>> result = {'bindings': [{
    ...           'Product': {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...           '@value': 'STRAWBERRY CANDY'}
    ...           }], "graphs": []}
    >>> woql.extract_header(result)
    [('Product', 'http://www.w3.org/2001/XMLSchema#string')]

    See Also
    --------
    query_to_df : put the result of the query into a pandas DataFrame
    type_map : convert WQOL rdf data types into numpy data types
    extract_column : extract the column of the returned result table
    """
    header = []
    if _is_empty(query):
        raise EmptyException("Query is empty")

    bindings = query["bindings"][0]
    for name, v in bindings.items():
        if type(v) is dict and ("@type" in v):
            ty = v["@type"]
        else:
            ty = "http://www.w3.org/2001/XMLSchema#string"
        header.append((name, ty))
    return header


def extract_column(query, name, ty):
    """Extracts the column of the returned result table

    Extrace one specific column from the result of the query binding.

    Parameters
    ----------
    query : dict
            JSON of the result of the query
    name : str
            Name of the column, can be extract from `extract_header()`
    ty : str
            WOQL rdf type of the column

    Returns
    -------
    list
        List consist of elements in that column

    Examples
    --------
    >>> result = {'bindings': [{
    ...           Product': {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...           '@value': 'STRAWBERRY CANDY'}
    ...           }], "graphs": []}
    >>> woql.extract_column(result, 'Product', 'http://www.w3.org/2001/XMLSchema#string')
    ['STRAWBERRY CANDY']

    See Also
    --------
    query_to_df : put the result of the query into a pandas DataFrame
    type_map : convert WQOL rdf data types into numpy data types
    extract_header : extract header of the returned result table
    """
    bindings = query["bindings"]
    column = []
    for binding in bindings:
        for k, v in binding.items():
            if k == (name):
                if isinstance(v, dict):
                    value = type_value_map(ty, v["@value"])
                else:
                    value = type_value_map(ty, v)
                column.append(value)
    return column


def type_map(ty_rdf):
    """Mapping types from WOQL rdf to numpy data types

    Maps the WOQL rdf type in the result query binding to numpy data types so it can be used in constructed pandas DataFrame.

    Parameters
    ----------
    ty_rdf : str
            WOQL rdf type, an exception will be raise if it's not a valid type

    Returns
    -------
    one of the numpy built-in scalar types objects
        The numpy data type object that matches with the WOQL rdf data type

    Examples
    --------
    >>> woql.type_map('http://www.w3.org/2001/XMLSchema#string')
    <class 'numpy.str_'>

    See Also
    --------
    query_to_df : put the result of the query into a pandas DataFrame
    type_value_map : converts values of different WOQL rdf types to numpy data types values
    """
    np = _import_needed("numpy")
    convert_mapping = {
        "http://www.w3.org/2001/XMLSchema#string": np.unicode_,
        "http://www.w3.org/2001/XMLSchema#integer": np.int,
        "http://www.w3.org/2001/XMLSchema#dateTime": np.datetime64,
        "http://www.w3.org/2001/XMLSchema#decimal": np.double,
        "http://www.w3.org/2001/XMLSchema#date": np.datetime64,
    }
    if ty_rdf in convert_mapping:
        return convert_mapping[ty_rdf]
    else:
        raise Exception("Unknown rdf type! " + ty_rdf)


def type_value_map(ty_rdf, value):
    """Converts values of different WOQL rdf types to numpy data types values

    Converts the values in the result query binding to numpy data types according to their WOQL rdf type, so it can be used in constructed pandas DataFrame.

    Parameters
    ----------
    ty_rdf : str
            WOQL rdf type, an exception will be raise if it's not a valid type
    value : str
            value to be converted

    Returns
    -------
    one of the numpy built-in scalar types
        The converted value in numpy data type

    Examples
    --------
    >>> woql.type_value_map('http://www.w3.org/2001/XMLSchema#decimal', '10.80')
    10.8

    See Also
    --------
    query_to_df : put the result of the query into a pandas DataFrame
    type_map : mapping types from WOQL rdf to numpy data types
    """
    np = _import_needed("numpy")
    if ty_rdf == "http://www.w3.org/2001/XMLSchema#string":
        return value
    elif ty_rdf == "http://www.w3.org/2001/XMLSchema#integer":
        return int(value)
    elif (
        ty_rdf == "http://www.w3.org/2001/XMLSchema#dateTime"
        or ty_rdf == "http://www.w3.org/2001/XMLSchema#date"
    ):
        return np.datetime64(value)
    elif ty_rdf == "http://www.w3.org/2001/XMLSchema#decimal":
        return float(value)
    else:
        raise Exception("Unknown rdf type! " + ty_rdf)


def query_to_df(query):
    """DEPRECATED in 0.3.0: use result_to_df instead.

    Converts result query binding to a pandas DataFrame. This only works for homogeneous query results

    Parameters
    ----------
    query : dict
            JSON of the result of the query

    Returns
    -------
    pandas.DataFrame
        The pandas DataFrame that is converted from the result.

    Examples
    --------
    >>> result = {'bindings': [{
    ...           'http://terminusdb.com/woql/variable/Product': {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...           '@value': 'STRAWBERRY CANDY'}
    ...           }], "graphs": []}
    >>> woql.query_to_df(result)
                Product
    0  STRAWBERRY CANDY

    See Also
    --------
    WOQLQuery : create a WOQLQuery
    WOQLClient : create a WOQLClient
    """
    warnings.warn("DEPRECATED in 0.3.0: use result_to_df instead.")
    return result_to_df(query)


def result_to_df(query):
    """Convert a query result to a data frame.

    Converts result query binding to a pandas DataFrame. This only works for homogeneous query results

    Parameters
    ----------
    query : dict
            JSON of the result of the query

    Returns
    -------
    pandas.DataFrame
        The pandas DataFrame that is converted from the result.

    Examples
    --------
    >>> result = {'bindings': [{
    ...           'http://terminusdb.com/woql/variable/Product': {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...           '@value': 'STRAWBERRY CANDY'}
    ...           }], "graphs": []}
    >>> woql.query_to_df(result)
                Product
    0  STRAWBERRY CANDY

    See Also
    --------
    WOQLQuery : create a WOQLQuery
    WOQLClient : create a WOQLClient
    """
    pd = _import_needed("pandas")
    header = extract_header(query)
    dtypes = {}
    column_names = []
    for name, rdftype in header:
        column_names.append(name)
        dtype = type_map(rdftype)
        dtypes[name] = dtype

    dataframe = pd.DataFrame(columns=column_names)
    dataframe.astype(dtypes)

    for name, rdftype in header:
        column = extract_column(query, name, rdftype)
        dataframe[name] = column

    return dataframe
