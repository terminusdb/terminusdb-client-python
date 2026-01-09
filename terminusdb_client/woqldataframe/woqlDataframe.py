# woqlDataframe.py

from importlib import import_module

from ..errors import InterfaceError


def _expand_df(df, pd, keepid):
    """Expand nested JSON objects in DataFrame columns.

    Args:
        df: pandas DataFrame to expand
        pd: pandas module reference
        keepid: whether to keep @id columns

    Returns:
        DataFrame with nested objects expanded into separate columns
    """
    for col in df.columns:
        if col == "Document id":
            continue
        try:
            expanded = pd.json_normalize(df[col])
        except Exception:
            expanded = None
        if expanded is not None and "@id" in expanded.columns:
            if not keepid:
                expanded.drop(
                    columns=list(filter(lambda x: x[0] == "@", expanded.columns)),
                    inplace=True,
                )
            expanded.columns = [col + "." + x for x in expanded]
            df.drop(columns=col, inplace=True)
            df = df.join(expanded)
    return df


def _embed_obj(df, maxdep, pd, keepid, all_existing_class, class_obj, client):
    """Recursively embed object references in DataFrame.

    Args:
        df: pandas DataFrame to process
        maxdep: maximum recursion depth
        pd: pandas module reference
        keepid: whether to keep @id columns
        all_existing_class: dict of class definitions from schema
        class_obj: the class type of the documents
        client: TerminusDB client for fetching documents

    Returns:
        DataFrame with object references replaced by their document content
    """
    if maxdep == 0:
        return df
    for col in df.columns:
        if "@" not in col and col != "Document id":
            col_comp = col.split(".")
            if len(col_comp) == 1:
                prop_type = all_existing_class[class_obj][col]
            else:
                prop_type = class_obj
                for comp in col_comp:
                    prop_type = all_existing_class[prop_type][comp]
            if (
                isinstance(prop_type, str)
                and prop_type[:4] != "xsd:"
                and prop_type != class_obj
                and all_existing_class[prop_type].get("@type") != "Enum"
            ):
                df[col] = df[col].apply(client.get_document)
    finish_df = _expand_df(df, pd, keepid)
    if (
        len(finish_df.columns) == len(df.columns)
        and (finish_df.columns == df.columns).all()
    ):
        return finish_df
    else:
        return _embed_obj(finish_df, maxdep - 1, pd, keepid, all_existing_class, class_obj, client)


def result_to_df(all_records, keepid=False, max_embed_dep=0, client=None):
    """Turn result documents into pandas DataFrame, all documents should be the same type.
    If max_embed_dep > 0, a client needs to be provided to get objects to embed in DataFrame.
    """
    try:
        pd = import_module("pandas")
    except ImportError:
        raise ImportError(
            "Library 'pandas' is required, either install 'pandas' or install woqlDataframe requirements as follows: python -m pip install -U terminus-client-python[dataframe]"
        )

    if max_embed_dep > 0 and client is None:
        raise ValueError(
            "A client need to be provide to get objects to embed in DataFrame if max_embed_dep > 0"
        )
    elif max_embed_dep > 0:
        all_existing_class = client.get_existing_classes()

    df = pd.DataFrame().from_records(list(all_records))
    all_types = df["@type"].unique()
    if len(all_types) > 1:
        raise ValueError("Cannot convert to DataFrame from multiple type of objects.")
    else:
        class_obj = all_types[0]
    if not keepid:
        df.rename(columns={"@id": "Document id"}, inplace=True)
        df.drop(columns=list(filter(lambda x: x[0] == "@", df.columns)), inplace=True)
    df = _expand_df(df, pd, keepid)
    if max_embed_dep > 0:
        if class_obj not in all_existing_class:
            raise InterfaceError(
                f"{class_obj} not found in database ({client.db}) schema.'"
            )
        df = _embed_obj(df, max_embed_dep, pd, keepid, all_existing_class, class_obj, client)
    return df
