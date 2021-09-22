# woqlDataframe.py

from importlib import import_module

from ..errors import InterfaceError


def result_to_df(all_records, keepid=False, max_embed_dep=0, client=None):
    """Turn result documents into pandas DataFrame, all documents should eb the same type. If max_embed_dep > 0, a client need to be provide to get objects to embed in DataFrame."""
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

    def expand_df(df):
        for col in df.columns:
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
                expanded.columns = list(map(lambda x: col + "." + x, expanded))
                df.drop(columns=col, inplace=True)
                df = df.join(expanded)
        return df

    def embed_obj(df, maxdep):
        if maxdep == 0:
            return df
        for col in df.columns:
            if "@" not in col:
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
                ):
                    df[col] = df[col].apply(client.get_document)
        finish_df = expand_df(df)
        if (
            len(finish_df.columns) == len(df.columns)
            and (finish_df.columns == df.columns).all()
        ):
            return finish_df
        else:
            return embed_obj(finish_df, maxdep - 1)

    df = pd.DataFrame().from_records(list(all_records))
    all_types = df["@type"].unique()
    if len(all_types) > 1:
        raise ValueError("Cannot convert to DataFrame from multiple type of objects.")
    else:
        class_obj = all_types[0]
    if not keepid:
        df.drop(columns=list(filter(lambda x: x[0] == "@", df.columns)), inplace=True)
    df = expand_df(df)
    if max_embed_dep > 0:
        if class_obj not in all_existing_class:
            raise InterfaceError(
                f"{class_obj} not found in database ({client.db}) schema.'"
            )
        df = embed_obj(df, maxdep=max_embed_dep)
    return df
