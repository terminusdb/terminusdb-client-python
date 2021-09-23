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


def convert_array(input_array: Union[list, set]):
    pass
