import datetime as dt
from enum import Enum
from typing import ForwardRef, List, Optional, Set, Union

CONVERT_TYPE = {
    str: "xsd:string",
    bool: "xsd:boolean",
    float: "xsd:decimal",
    int: "xsd:integer",
    dt.datetime: "xsd:dateTime",
    dt.date: "xsd:date",
    dt.time: "xsd:time",
    dt.timedelta: "xsd:duration",
}


def to_woql_type(input_type: type):
    if input_type in CONVERT_TYPE:
        return CONVERT_TYPE[input_type]
    elif hasattr(input_type, "__module__") and input_type.__module__ == "typing":
        if isinstance(input_type, ForwardRef):
            return input_type.__forward_arg__
        elif input_type._name:
            return {
                "@type": input_type._name,
                "@class": to_woql_type(input_type.__args__[0]),
            }
        else:
            return {"@type": "Optional", "@class": to_woql_type(input_type.__args__[0])}
    elif isinstance(input_type, type(Enum)):
        return input_type.__name__
    else:
        return str(input_type)


def from_woql_type(
    input_type: Union[str, dict], skip_convert_error=False, as_str=False
):
    """Converting the TerminusDB datatypes into Python types, it will not detect self define types (i.e. object properties) so if converting object properties, skip_convert_error need to be True.

    Parameters
    ----------
    input_type : str or dict
        TerminusDB datatypes to be converted.
    skip_convert_error : bool
        Will an error be raised if the datatype given cannot be convert to Python types. If set to True (and as_type set to False) and type cannot be converted, the type will be returned back without convertion.
    as_str : bool
        Will convert the type and present it as string (e.g. used in constructing scripts). It will always skip convert error if set to True.
    """
    if as_str:
        skip_convert_error = True
    invert_type = {v: k for k, v in CONVERT_TYPE.items()}
    if isinstance(input_type, dict):
        if input_type["@type"] == "List":
            if as_str:
                return f'List[{from_woql_type(input_type["@class"], as_str=True)}]'
            else:
                return List[from_woql_type(input_type["@class"], as_str=True)]
        elif input_type["@type"] == "Set":
            if as_str:
                return f'Set[{from_woql_type(input_type["@class"], as_str=True)}]'
            else:
                return Set[from_woql_type(input_type["@class"], as_str=True)]
        elif input_type["@type"] == "Optional":
            if as_str:
                return f'Optional[{from_woql_type(input_type["@class"], as_str=True)}]'
            else:
                return Optional[from_woql_type(input_type["@class"], as_str=True)]
        else:
            raise TypeError(
                f"Input type {input_type} cannot be converted to Python type"
            )
    elif input_type in invert_type:
        if as_str:
            return invert_type[input_type].__name__
        return invert_type[input_type]
    elif skip_convert_error:
        if as_str:
            return f"'{input_type}'"
        return input_type
    else:
        raise TypeError(f"Input type {input_type} cannot be converted to Python type")


def datetime_to_woql(dt_obj):
    """Convert datetime objects into strings that is recognize by woql.
    Do nothing and return the object as it if it is not one of the supported datetime object."""
    if (
        isinstance(dt_obj, dt.datetime)
        or isinstance(dt_obj, dt.date)
        or isinstance(dt_obj, dt.time)
    ):
        return dt_obj.isoformat()
    elif isinstance(dt_obj, dt.timedelta):
        return f"PT{dt_obj.total_seconds()}S"
    else:
        return dt_obj


def datetime_from_woql(dt_str, woql_type):
    """Convert woql datetime objects (str format) to datetime object.
    Raise ValueError if cannot be converted."""
    if woql_type == "xsd:duration" or "P" in dt_str:
        if dt_str[0] == "-":
            pidx = 1  # is_negative
        else:
            pidx = 0
        dpart = dt_str[pidx + 1 :].split("T")[0]
        if "Y" in dpart or "M" in dpart:
            raise ValueError(f"Duration {dt_str} is undetermined")
        elif not dpart:
            days = 0
        else:
            days = float(dpart[:-1])
        tpart = dt_str[pidx + 1 :].split("T")[1]
        tkeys = ["H", "M", "S"]
        tdict = {}
        for key in tkeys:
            idx = tpart.find(key)
            if idx != -1:
                tdict[key] = float(tpart[:idx])
                tpart = tpart[idx + 1 :]
            else:
                tdict[key] = 0
        delta_obj = dt.timedelta(
            days=days, hours=tdict["H"], minutes=tdict["M"], seconds=tdict["S"]
        )
        if pidx:
            delta_obj = -delta_obj
        return delta_obj
    else:
        dt_obj = dt.datetime.fromisoformat(dt_str.replace("Z", ""))
        if woql_type == "xsd:dateTime":
            return dt_obj
        elif woql_type == "xsd:date":
            return dt_obj.date()
        elif woql_type == "xsd:time":
            return dt_obj.time()
        else:
            raise ValueError(
                f"{woql_type} object {dt_str} not supported datetime type or cannot be converted."
            )
