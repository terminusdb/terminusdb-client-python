import datetime as dt
from typing import ForwardRef, List, Optional, Set, Union

CONVERT_TYPE = {
    str: "xsd:string",
    bool: "xsd:boolean",
    float: "xsd:decimal",
    int: "xsd:integer",
    dt.datetime: "xsd:dataTime",
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
    else:
        return str(input_type)


def from_woql_type(input_type: Union[str, dict]):
    invert_type = {v: k for k, v in CONVERT_TYPE.items()}
    if isinstance(input_type, "dict"):
        if input_type["@type"] == "List":
            return List[input_type["@class"]]
        elif input_type["@type"] == "Set":
            return Set[input_type["@class"]]
        elif input_type["@type"] == "Optional":
            return Optional[input_type["@class"]]
    elif input_type in invert_type:
        return invert_type[input_type]
    else:
        raise ValueError("Input type cannot be converted to Python type")


def convert_array(input_array: Union[list, set]):
    pass
